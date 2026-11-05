"""API route and request-validation tests."""

from io import BytesIO

import pytest
from werkzeug.datastructures import FileStorage

from backend.llm.llm import CoverLetterPrompt, LlmGenerationError
from backend.routes import main
from backend.scraping.job import JobScrapingError


@pytest.fixture()
def client():
    """Create a Flask test client with production upload limits."""
    main.app.config.update(TESTING=True, MAX_CONTENT_LENGTH=main.MAX_RESUME_BYTES)
    with main.app.test_client() as test_client:
        yield test_client
    main.app.config["MAX_CONTENT_LENGTH"] = main.MAX_RESUME_BYTES


def multipart_payload(filename="resume.pdf"):
    """Return the minimum documented request payload."""
    return {
        "resume": (BytesIO(b"%PDF-test"), filename),
        "jobUrl": "https://www.linkedin.com/jobs/view/123456789",
        "tone": "modern",
    }


def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_generate_requires_resume(client):
    response = client.post(
        "/api/generate-cover-letter",
        data={"jobUrl": "https://www.linkedin.com/jobs/view/123456789"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Upload a PDF resume."


def test_generate_rejects_invalid_url_before_external_calls(client):
    payload = multipart_payload()
    payload["jobUrl"] = "https://example.com/jobs/123"

    response = client.post("/api/generate-cover-letter", data=payload)

    assert response.status_code == 400
    assert "LinkedIn" in response.get_json()["error"]


def test_generate_rejects_non_pdf(client):
    response = client.post(
        "/api/generate-cover-letter",
        data=multipart_payload("resume.docx"),
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Upload a PDF resume."


def test_generate_success_uses_documented_fields(client, monkeypatch):
    captured = {}
    prompt = CoverLetterPrompt(instructions="facts only", input_text="input")
    monkeypatch.setattr(main, "parse_resume", lambda _upload: "Resume text")

    def fake_create_prompt(context):
        captured["context"] = context
        return prompt

    monkeypatch.setattr(main.Llm, "create_prompt", fake_create_prompt)
    monkeypatch.setattr(
        main.Llm,
        "generate",
        lambda received_prompt: "```latex\n\\documentclass{article}\n```"
        if received_prompt is prompt
        else "",
    )
    payload = multipart_payload()
    payload.update(
        {
            "extraDetails": "Built internal tools",
            "comments": "Use a shorter opening",
            "tone": "traditional",
        }
    )

    response = client.post("/api/generate-cover-letter", data=payload)

    assert response.status_code == 200
    assert response.get_json() == {"coverLetter": "\\documentclass{article}"}
    assert captured["context"].resume_text == "Resume text"
    assert captured["context"].extra_details == "Built internal tools"
    assert captured["context"].comments == "Use a shorter opening"
    assert captured["context"].tone == "traditional"


def test_generate_reports_scraping_failure(client, monkeypatch):
    monkeypatch.setattr(main, "parse_resume", lambda _upload: "Resume text")

    def fail_scrape(_context):
        raise JobScrapingError("The LinkedIn job posting could not be retrieved.")

    monkeypatch.setattr(main.Llm, "create_prompt", fail_scrape)

    response = client.post(
        "/api/generate-cover-letter",
        data=multipart_payload(),
    )

    assert response.status_code == 502
    assert "could not be retrieved" in response.get_json()["error"]


def test_generate_reports_model_failure(client, monkeypatch):
    monkeypatch.setattr(main, "parse_resume", lambda _upload: "Resume text")
    monkeypatch.setattr(
        main.Llm,
        "create_prompt",
        lambda _context: CoverLetterPrompt("facts only", "input"),
    )

    def fail_generation(_prompt):
        raise LlmGenerationError("empty")

    monkeypatch.setattr(main.Llm, "generate", fail_generation)

    response = client.post(
        "/api/generate-cover-letter",
        data=multipart_payload(),
    )

    assert response.status_code == 502
    assert response.get_json()["error"] == (
        "The cover letter service is temporarily unavailable."
    )


def test_generate_rejects_oversized_upload(client):
    main.app.config["MAX_CONTENT_LENGTH"] = 128
    payload = multipart_payload()
    payload["resume"] = (BytesIO(b"x" * 1024), "resume.pdf")

    response = client.post("/api/generate-cover-letter", data=payload)

    assert response.status_code == 413
    assert "5 MiB" in response.get_json()["error"]


def test_parse_resume_extracts_text_without_writing_files(monkeypatch):
    class FakePage:
        @staticmethod
        def extract_text():
            return "Nicholas Woo\nSoftware Developer"

    class FakeReader:
        is_encrypted = False
        pages = [FakePage()]

        def __init__(self, stream):
            assert stream.read(4) == b"%PDF"

    monkeypatch.setattr(main, "PdfReader", FakeReader)
    upload = FileStorage(
        stream=BytesIO(b"%PDF-test"),
        filename="resume.pdf",
        content_type="application/pdf",
    )

    assert main.parse_resume(upload) == "Nicholas Woo\nSoftware Developer"


def test_parse_resume_rejects_malformed_pdf():
    upload = FileStorage(
        stream=BytesIO(b"not a pdf"),
        filename="resume.pdf",
        content_type="application/pdf",
    )

    with pytest.raises(main.ResumeValidationError, match="could not be read"):
        main.parse_resume(upload)


def test_compile_returns_pdf(client, monkeypatch):
    monkeypatch.setattr(main.CompileLatex, "compile", lambda _source: b"%PDF-result")

    response = client.post(
        "/api/compile-latex",
        json={"latex": "\\documentclass{article}"},
    )

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data == b"%PDF-result"


def test_compile_rejects_missing_latex(client):
    response = client.post("/api/compile-latex", json={})

    assert response.status_code == 400
    assert response.get_json()["error"] == "No LaTeX content was provided."


def test_compile_reports_invalid_latex(client, monkeypatch):
    def fail_compile(_source):
        raise main.LatexCompilationError("XeLaTeX could not compile the generated document.")

    monkeypatch.setattr(main.CompileLatex, "compile", fail_compile)

    response = client.post("/api/compile-latex", json={"latex": "invalid"})

    assert response.status_code == 422
    assert "could not compile" in response.get_json()["error"]
