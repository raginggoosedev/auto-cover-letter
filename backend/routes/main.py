from flask import Flask, request, jsonify, send_file
import io
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from llm.llm import Llm
from flask_cors import CORS

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
    return jsonify({"coverLetter": cover_letter.output_text})

@app.route('/compile-latex', methods=['POST'])
def compile_latex():
    print("Compiling LaTeX...")

if __name__ == '__main__':
    app.run(debug=True)