"""
Main class for LLM backend
"""

__author__ = "Michael Quick", "Nicholas Woo"
__email__ = "mwquick04@gmail.com", "nwoo68@gmail.com"
__version__ = "1.0.0"

import os
import sys

import PyPDF2

from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from scraping.job import Job


class Llm:
    """
    Class to interact with OpenAI's API for generating cover letters.
    """
    load_dotenv()  # Get API key from env

    @classmethod
    def create_prompt(cls, job_url, extra_details, letter_style, comments, resume):
        """
        Create a prompt for the LLM based on user input.
        Resume can be either a file path or the extracted text content.
        """
        # Instantiate the Job object to scrape job details from the provided URL
        job = Job(job_url)
        job_name = job.company_name
        job_description = job.description
        job_basic_qualifications = job.basic_qualifications
        job_preferred_qualifications = job.preferred_qualifications

        # Determine resume content based on input type
        resume_content = ""
        if resume:
            if isinstance(resume, str) and os.path.isfile(resume):
                # Handle case where resume is a file path
                try:
                    with open(resume, "rb") as pdf_file:
                        reader = PyPDF2.PdfReader(pdf_file)
                        for page in reader.pages:
                            text = page.extract_text() or ""
                            resume_content += text + "\n"
                except Exception as e:
                    resume_content = f"Error reading PDF: {e}"
            else:
                # Resume is already text content
                resume_content = resume

        print("Final resume content:", resume_content)

        # Build the prompt
        prompt = (
            f"Create a raw LaTeX cover letter for the job at {job_name}.\n"
            f"Job Description: {job_description}\n"
            f"Extra Details: {extra_details}\n"
            f"Cover Letter Style: {letter_style}\n"
            f"User Comments: {comments}\n"
            f"Basic Qualifications: {job_basic_qualifications}\n"
            f"Preferred Qualifications: {job_preferred_qualifications}\n"
            f"Resume Content: {resume_content}\n"
            f"Only return the latex do not include beginning messages or ending messages.\n"
        )
        return prompt

    @classmethod
    def generate(cls, prompt):
        """
        Generate a response from the LLM based on the provided prompt."
        """

        OpenAI.api_key = os.environ.get("OPENAI_API_KEY")
        client = OpenAI()
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return response
