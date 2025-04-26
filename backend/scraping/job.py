"""
Job class for Scraping backend
"""

# Disable pylint for too few public methods
# pylint: disable=R0903

__author__ = "Josh Muszka", "Michael Quick"
__email__ = "joshmuszka67@gmail.com", "mwquick04@gmail.com"
__version__ = "1.0.0"

import re
from urllib.error import URLError
import requests
from bs4 import BeautifulSoup


class Job:
    """
    Represents a job posting scraped from LinkedIn.

    Attributes:
        company_name (str): Name of the company.
        description (str): Job description.
        basic_qualifications (str): Basic qualifications.
        preferred_qualifications (str): Preferred qualifications.
    """

    def __init__(self, url: str):
        api_url = self.get_api_url_from_job_posting_url(url)
        soup = BeautifulSoup(requests.get(api_url, timeout=10).text, "html.parser")

        self.company_name = (
            soup.find(
                "a",
                {"class": "topcard__org-name-link topcard__flavor--black-link"}
            )
            .text.strip()
        )

        description_html = soup.find(
            "div", {"class": "core-section-container__content break-words"}
        )
        elems = re.split(
            r'Description|Basic Qualifications|Preferred Qualifications',
            description_html.text
        )

        # Assign sections if present
        if len(elems) >= 2:
            self.description = elems[1].strip()
        if len(elems) >= 3:
            self.basic_qualifications = elems[2].strip()
        if len(elems) >= 4:
            self.preferred_qualifications = elems[3].strip()
        elif len(elems) == 1:
            self.description = elems[0].strip()

    @staticmethod
    def get_api_url_from_job_posting_url(url: str) -> str:
        """
        Converts a LinkedIn job posting URL into the corresponding API URL.

        Raises:
            URLError: If the URL does not match the expected LinkedIn pattern.
        """
        pattern = re.compile(r"^https://www\.linkedin\.com/jobs/view/\d+")
        if pattern.match(url):
            job_id = url.rstrip("/").split("/")[-1]
            return (
                f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
            )
        raise URLError("Invalid job posting URL - must be a LinkedIn job post")
