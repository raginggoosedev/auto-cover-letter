"""
Main class for LLM backend
"""

__author__ = "Michael Quick"
__email__ = "mwquick04@gmail.com"
__version__ = "1.0.0"

import os, sys

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from openai import OpenAI
from dotenv import load_dotenv

from backend.scraping.job import Job

load_dotenv()  # Get API key from env

OpenAI.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()


def main():
    """
    Main entry point for LLM program.
    """

    job = Job("https://www.linkedin.com/jobs/view/4181203458")

    response = client.responses.create(
        model="gpt-4o",
        input=f"Please write a cover letter for this {job.company_name} job posting:\n\n \
                Description: {job.description} \n\n \
                Qualifications: {job.basic_qualifications} {job.preferred_qualifications} \
                \n\n\n My name is Josh Muszka and I am a 3rd year computer science student at Western University"
    )

    print(response.output_text)


if __name__ == "__main__":
    main()
