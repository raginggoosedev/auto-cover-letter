from openai import OpenAI
from dotenv import load_dotenv
import os

from scraping.job import Job

class Llm:
    """
    Class to interact with OpenAI's API for generating cover letters.
    """
    load_dotenv()  # Get API key from env

    @classmethod
    def create_prompt(self, job_url, extra_details, letter_style, comments, resume):
        """
        Create a prompt for the LLM based on user input.
        """
        # Instantiate the Job object to scrape job details from the provided URL
        job = Job(job_url)
        job_name = job.company_name
        job_description = job.description
        job_basic_qualifications = job.basic_qualifications
        job_preferred_qualifications = job.preferred_qualifications
        
        # Build the prompt by combining the scraped job description with other details
        prompt = (
            f"Create a raw LaTeX cover letter for the job at {job_name}.\n"
            f"Job Description: {job_description}\n"
            f"Extra Details: {extra_details}\n"
            f"Cover Letter Style: {letter_style}\n"
            f"User Comments: {comments}\n"
            f"Basic Qualifications: {job_basic_qualifications}\n"
            f"Preferred Qualifications: {job_preferred_qualifications}\n"
            f"Resume Content: {resume}\n"
            f"Please only return the latex do not include beginning messages or ending messages.\n"
        )
        return prompt

    @classmethod
    def generate(self, prompt):
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