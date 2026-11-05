"""HTTP API for generating and compiling cover letters."""

from io import BytesIO
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from openai import OpenAIError
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from werkzeug.exceptions import RequestEntityTooLarge

from backend.latex.compile import CompileLatex, LatexCompilationError
from backend.llm.llm import (
    CoverLetterContext,
    Llm,
    LlmConfigurationError,
    LlmGenerationError,
)
from backend.scraping.job import Job, JobScrapingError, UnsupportedJobUrl

MAX_RESUME_BYTES = 5 * 1024 * 1024
SUPPORTED_TONES = frozenset(Llm.TONE_GUIDANCE)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_RESUME_BYTES

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})


class ResumeValidationError(ValueError):
    """Raised when an uploaded resume is missing or unreadable."""


def error_response(message: str, status_code: int):
    """Return the API's standard error shape."""
    return jsonify({"error": message}), status_code


@app.errorhandler(RequestEntityTooLarge)
def handle_oversized_upload(_error):
    """Return JSON when Flask rejects an oversized request."""
    return error_response("The resume must be no larger than 5 MiB.", 413)


def parse_resume(uploaded_file) -> str:
    """Extract text from a PDF upload without writing it to disk."""
    filename = Path(uploaded_file.filename or "").name
    if Path(filename).suffix.lower() != ".pdf":
        raise ResumeValidationError("Upload a PDF resume.")

    try:
        uploaded_file.stream.seek(0)
        reader = PdfReader(uploaded_file.stream)
        if reader.is_encrypted:
            raise ResumeValidationError("Password-protected PDFs are not supported.")
        resume_text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
    except (PdfReadError, OSError, ValueError) as error:
        if isinstance(error, ResumeValidationError):
            raise
        raise ResumeValidationError("The uploaded PDF could not be read.") from error

    if not resume_text:
        raise ResumeValidationError(
            "No selectable text was found in the PDF resume."
        )
    return resume_text


def load_letter_template() -> str:
    """Load the version-controlled LaTeX template."""
    template_path = Path(__file__).resolve().parents[1] / "latex" / "format.tex"
    return template_path.read_text(encoding="utf-8")


def clean_model_output(output_text: str) -> str:
    """Remove an optional Markdown fence from otherwise valid LaTeX."""
    cleaned = output_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().lower() in {"```", "```latex", "```tex"}:
            lines.pop(0)
        if lines and lines[-1].strip() == "```":
            lines.pop()
        cleaned = "\n".join(lines).strip()
    return cleaned


@app.get("/api/health")
def health():
    """Report whether the Flask process is running."""
    return jsonify({"status": "ok"})


@app.post("/api/generate-cover-letter")
# The explicit returns keep each HTTP validation/error path easy to audit.
# pylint: disable=too-many-return-statements
def generate_cover_letter():
    """Generate editable LaTeX from a PDF resume and LinkedIn job URL."""
    uploaded_resume = request.files.get("resume")
    job_url = request.form.get("jobUrl", "").strip()
    extra_details = request.form.get("extraDetails", "").strip()
    comments = request.form.get("comments", "").strip()
    tone = request.form.get("tone", "modern").strip().lower()

    if uploaded_resume is None or not uploaded_resume.filename:
        return error_response("Upload a PDF resume.", 400)
    if not job_url:
        return error_response("Enter a LinkedIn job posting URL.", 400)
    if tone not in SUPPORTED_TONES:
        return error_response("Choose a supported writing tone.", 400)

    try:
        Job.get_api_url_from_job_posting_url(job_url)
        resume_text = parse_resume(uploaded_resume)
        prompt = Llm.create_prompt(
            CoverLetterContext(
                job_url=job_url,
                extra_details=extra_details,
                letter_template=load_letter_template(),
                comments=comments,
                resume_text=resume_text,
                tone=tone,
            )
        )
        cover_letter = clean_model_output(Llm.generate(prompt))
    except (UnsupportedJobUrl, ResumeValidationError, ValueError) as error:
        return error_response(str(error), 400)
    except JobScrapingError as error:
        return error_response(str(error), 502)
    except LlmConfigurationError as error:
        return error_response(str(error), 503)
    except (LlmGenerationError, OpenAIError):
        return error_response("The cover letter service is temporarily unavailable.", 502)

    if not cover_letter:
        return error_response("The model did not return a cover letter.", 502)
    return jsonify({"coverLetter": cover_letter})


@app.post("/api/compile-latex")
def compile_latex():
    """Compile submitted LaTeX and return a downloadable PDF."""
    data = request.get_json(silent=True) or {}
    latex_content = data.get("latex", "")
    if not isinstance(latex_content, str) or not latex_content.strip():
        return error_response("No LaTeX content was provided.", 400)

    try:
        pdf_bytes = CompileLatex.compile(clean_model_output(latex_content))
    except LatexCompilationError as error:
        return error_response(str(error), 422)

    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="cover-letter.pdf",
        max_age=0,
    )


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
