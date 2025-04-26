"""
Routes cover letter files for website
"""

__author__ = "Michael Quick", "Nicholas Woo"
__email__ = "mwquick04@gmail.com", "nwoo68@gmail.com"
__version__ = "1.0.0"

import os

import PyPDF2

from flask_cors import CORS

from flask import Flask, request, jsonify, send_file

from latex.compile import CompileLatex
from llm.llm import Llm

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    """
    Hello world test
    """
    return 'Hello, World!'


def parse_resume(uploaded_file) -> str:
    """
    Given a werkzeug FileStorage for a PDF resume, extract text,
    force ASCII only, and return the clean string.
    """

    # save to temp
    tmp = os.path.join(os.path.dirname(__file__), 'temp_resume.pdf')
    uploaded_file.save(tmp)

    text_accum = []
    try:
        with open(tmp, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                raw = page.extract_text() or ""
                # normalize → ascii
                clean = raw.encode('ascii', 'ignore').decode('ascii')
                text_accum.append(clean)
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass

    return "\n".join(text_accum)


def load_letter_style() -> str:
    """
    Load the letter style from the format.tex latex file
    """
    here = os.path.dirname(__file__)
    fmt = os.path.join(here, "..", "latex", "format.tex")
    with open(fmt, "r", encoding="utf-8") as f:
        return f.read()


@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """
    Generate the cover letter by collecting the information from the resume,
    job description, and extras, and sending the LLM a prompt
    """

    job_url = request.form.get('jobName', '')
    extra_details = request.form.get('extraDetails', '')
    comments = request.form.get('comments', '')
    letter_style = load_letter_style()

    resume_text = ""
    if 'resume' in request.files and request.files['resume'].filename:
        resume_text = parse_resume(request.files['resume'])

    prompt = Llm.create_prompt(
        job_url,
        extra_details,
        letter_style,
        comments,
        resume_text
    )
    cover_letter = Llm.generate(prompt)

    return jsonify({
        "coverLetter": cover_letter
        .output_text
        .strip("`")
        .removeprefix("latex")
    })


@app.route('/compile-latex', methods=['POST'])
def compile_latex():
    """
    Compiles the latex file
    """
    data = request.get_json()
    latex_content = data.get('latex', '')

    if not latex_content:
        return jsonify({"error": "No LaTeX content provided"}), 400

    try:
        # Compile the LaTeX content
        pdf_path = CompileLatex.compile(latex_content)

        if not os.path.exists(pdf_path):
            return jsonify({"error": "PDF file not found. Compilation may have failed."}), 500

        # Send the generated PDF file
        response = send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='cover-letter.pdf'
        )

        # After sending the file, delete temporary files
        def remove_temp_files():
            try:
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                log_path = pdf_path.replace('.pdf', '.log')
                aux_path = pdf_path.replace('.pdf', '.aux')
                if os.path.exists(log_path):
                    os.remove(log_path)
                if os.path.exists(aux_path):
                    os.remove(aux_path)
            except IOError as e:
                print("Error deleting temporary files:", e)

        response.call_on_close(remove_temp_files)
        return response

    except IOError as e:
        print(f"Exception during PDF compilation: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
