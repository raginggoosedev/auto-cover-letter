"""
Job class for Scraping backend
"""

__author__ = "Josh Muszka"
__email__ = "joshmuszka67@gmail.com"
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
    company_name = ""
    description = ""
    basic_qualifications = ""
    preferred_qualifications = ""

    def __init__(self, url):
        url = self._get_job_api_url_from_job_posting_url(url)
        soup = BeautifulSoup(requests.get(url, timeout=10).text, "html.parser")

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
            'Description|Basic Qualifications|Preferred Qualifications',
            description_html.text
        )

        if len(elems) >= 2:
            self.description = elems[1].strip()
        if len(elems) >= 3:
            self.basic_qualifications = elems[2].strip()
        if len(elems) >= 4:
            self.preferred_qualifications = elems[3].strip()
        elif len(elems) == 1:
            self.description = elems[0].strip()

    def _get_job_api_url_from_job_posting_url(self, url=""):
        """
        Converts a LinkedIn job posting URL into the corresponding API URL.

        Args:
            url (str): Original job posting URL.

        Returns:
            str: API URL for the job posting.

        Raises:
            ValueError: If the URL does not match the expected pattern.
        """
        # Check if job post URL is valid and convert to an API url
        pattern = re.compile("^https://www.linkedin.com/jobs/view/[0-9]+")
        if pattern.match(url):
            return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{url.split('/')[-1]}"

        raise URLError("Invalid job posting URL - must be a LinkedIn job post")
