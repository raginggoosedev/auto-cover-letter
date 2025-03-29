from flask import Flask, request, jsonify, send_file
import io
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from llm.llm import Llm
from latex.compile import CompileLatex
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    # Expect form-data information coming from the frontend
    job_url = request.form.get('jobName', '')
    extra_details = request.form.get('extraDetails', '')
    letter_style = request.form.get('letterStyle', '')

    comments = request.form.get('comments', '')
    # resume file is available in request.files if needed:
    resume = request.form.get('resume', None)

    prompt = Llm.create_prompt(job_url, extra_details, letter_style, comments, resume)

    cover_letter = Llm.generate(prompt)

    # Return the cover letter
    return jsonify({"coverLetter": cover_letter.output_text.strip("`").removeprefix("latex")})

@app.route('/compile-latex', methods=['POST'])
def compile_latex():
    data = request.get_json()
    latex_content = data.get('latex', '')
    
    if not latex_content:
        return jsonify({"error": "No LaTeX content provided"}), 400

    try:
        # Automatically provide a newline to simulate pressing Enter during compilation
        old_stdin = sys.stdin
        sys.stdin = io.StringIO('\n')
        try:
            # Compile the LaTeX content
            CompileLatex.compile(latex_content)
        finally:
            sys.stdin = old_stdin
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Define file paths, now expecting that the compilation produces cover-letter.pdf and cover-letter.log
    base_dir = os.path.dirname(__file__)
    pdf_path = os.path.abspath(os.path.join(base_dir, 'cover-letter.pdf'))
    log_path = os.path.abspath(os.path.join(base_dir, 'cover-letter.log'))
    
    if not os.path.exists(pdf_path):
        return jsonify({"error": "PDF file not found. Compilation may have failed."}), 500

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
            if os.path.exists(log_path):
                os.remove(log_path)
        except Exception as e:
            print("Error deleting temporary files:", e)

    response.call_on_close(remove_temp_files)
    return response

if __name__ == '__main__':
    app.run(debug=True)