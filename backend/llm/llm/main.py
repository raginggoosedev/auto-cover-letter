"""
Main class for LLM backend
"""

__author__ = "Michael Quick"
__email__ = "mwquick04@gmail.com"
__version__ = "1.0.0"

import os, sys, subprocess

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from openai import OpenAI
from dotenv import load_dotenv

from scraping.job import Job

load_dotenv()  # Get API key from env

OpenAI.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()

def create_prompt(job_url, extra_details, letter_style, comments, resume):
    """
    Create a prompt for the LLM based on user input.
    """
    
    job_description = Job._get_job_api_url_from_job_posting_url(job_url)
    # Simulate the prompt creation process
    prompt = (
        f"Create a raw latex document cover letter for the job at {job_url}.\n"
        f"Job Description: {job_description}\n"
        f"Extra Details: {extra_details}\n"
        f"Structure Style: {letter_style}\n"
        f"Comments: {comments}\n"
        f"Resume: {resume}\n"
    )
    return prompt

def generate(prompt):
    response = client.responses.create(
        model="gpt-4o",
        input=prompt
    )
    return response
def main():
    """
    Main entry point for LLM program.
    """

    job = Job("https://www.linkedin.com/jobs/view/4072387977")
    f = open("../latex/format.tex")
    template = f.read()
    f.close()

    response = client.responses.create(
        model="gpt-4o",
        input=f"Please write a cover letter for this {job.company_name} job posting:\n\n \
                Description: {job.description} \n\n \
                Qualifications: {job.basic_qualifications} {job.preferred_qualifications} \
                \n\n\n My name is Josh Muszka and I am a 3rd year computer science student at Western University \
                \n\n Here is the latex template: \n\n \
                {template} \n\n Please only return the latex with the according information turned in. If there is any information you can't fill in then make something up"
    )

    with open("../latex/resume.tex", "+w") as f:
        f.write(response.output_text.strip("`").removeprefix("latex"))

    read, write = os.pipe() 
    os.write(write, b"\n")
    os.close(write)
    subprocess.run(["xelatex", "../latex/resume.tex", ])
    subprocess.run(["rm", "resume.aux", ])
    subprocess.run(["rm", "resume.log", ])
    subprocess.run(["mv", "resume.pdf", "../latex/resume.pdf"])
    print(response.output_text)


if __name__ == "__main__":
    main()
