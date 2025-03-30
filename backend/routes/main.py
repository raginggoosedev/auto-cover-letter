"""
Routes cover letter files for website
"""

import os

import PyPDF2

from flask_cors import CORS

from flask import Flask, request, jsonify, send_file

from ..latex.compile import CompileLatex
from ..llm.llm import Llm

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    """
    Hello world test
    """
    return 'Hello, World!'


@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """
    Generates a cover letter
    """
    # Expect form-data information coming from the frontend
    job_url = request.form.get('jobName', '')
    extra_details = request.form.get('extraDetails', '')
    letter_style = request.form.get('letterStyle', '')
    comments = request.form.get('comments', '')

    # Get resume file from request.files instead of request.form
    resume_text = ""
    if 'resume' in request.files:
        resume_file = request.files['resume']
        if resume_file.filename != '':
            # Create a temporary file to save the uploaded resume
            temp_file_path = os.path.join(os.path.dirname(__file__), 'temp_resume.pdf')
            resume_file.save(temp_file_path)

            try:
                # Extract text from PDF
                with open(temp_file_path, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    for page in reader.pages:
                        text = page.extract_text() or ""
                        resume_text += text + "\n"

                # Clean up the temporary file
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error processing resume: {e}")

    prompt = Llm.create_prompt(job_url, extra_details, letter_style, comments, resume_text)
    cover_letter = Llm.generate(prompt)

    # Return the cover letter
    return jsonify({"coverLetter": cover_letter.output_text.strip("`").removeprefix("latex")})


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
            except Exception as e:
                print("Error deleting temporary files:", e)

        response.call_on_close(remove_temp_files)
        return response

    except Exception as e:
        print(f"Exception during PDF compilation: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
