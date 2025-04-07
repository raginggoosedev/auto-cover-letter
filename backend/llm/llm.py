"""
Main class for LLM backend
"""

__author__ = "Michael Quick", "Nicholas Woo"
__email__ = "mwquick04@gmail.com", "nwoo68@gmail.com"
__version__ = "1.0.0"

import os

import PyPDF2

from openai import OpenAI
from dotenv import load_dotenv

from backend.scraping.job import Job


class Llm:
    """
    Class to interact with OpenAI's API for generating cover letters.
    """
    
    load_dotenv('/var/www/html/dataquest-2025/backend/llm/.env') # Get API key from env

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
                except IOError as e:
                    resume_content = f"Error reading PDF: {e}"
            else:
                # Resume is already text content
                resume_content = resume

        print("Final resume content:", resume_content)

        # Build the prompt
        prompt = (
            f"I need you to help me generate a professional-sounding cover letter for my "
            f"job application at {job_name}. "
            f"I will provide the job description, and the LaTeX template file that I made the font for the latex file should be Linux Libertine O font"
            f"I will also provide you my resume. "
            f"I want you to fill in the information and tailor the cover letter to the job "
            f"description, using information from my resume. You will only return the LaTeX "
            f"source code.\n\n"
            f"Job Description: {job_description}\n\n"
            f"Extra Details: {extra_details}\n\n"
            f"Cover Letter Style (it IS CRUCIAL that you follow EXACTLY this format): "
            f"{letter_style}\n\n"
            f"User Comments: {comments}\n\n"
            f"Basic Qualifications: {job_basic_qualifications}\n\n"
            f"Preferred Qualifications: {job_preferred_qualifications}\n\n"
            f"Resume Content: {resume_content}\n\n"
            f"Only return the latex do not include beginning messages or ending messages.\n"
            f"If you can't determine the job position then simply put Software Developer, "
            f"if there is no recruiter then simply put Recruiter. "
            f"Do not, under any circumstances, leave any information unfilled. "
            f"You may extrapolate information, and make it sound as professional and human-like "
            f"as possible."
        )
        return prompt

    @classmethod
    def generate(cls, prompt):
        """
        Generate a response from the LLM based on the provided prompt."
        """

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt
        )
        return response
