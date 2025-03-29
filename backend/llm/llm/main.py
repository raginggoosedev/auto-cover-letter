"""
Main class for LLM backend
"""

__author__ = "Michael Quick"
__email__ = "mwquick04@gmail.com"
__version__ = "1.0.0"

import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # Get API key from env

OpenAI.api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI()


def main():
    """
    Main entry point for LLM program.
    """

    response = client.responses.create(
        model="gpt-4o",
        input="Please write about how great I, Michael Quick, am."
    )

    print(response.output_text)


if __name__ == "__main__":
    main()
