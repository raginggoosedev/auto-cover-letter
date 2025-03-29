from openai import OpenAI
from dotenv import load_dotenv
import os

from scraping.job import Job

class Llm:
    """
    Class to interact with OpenAI's API for generating cover letters.
    """
    load_dotenv()  # Get API key from env

    def create_prompt(self, job_url, extra_details, letter_style, comments, resume):
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