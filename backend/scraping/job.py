"""
Job class for Scraping backend
"""

# Disable pylint for too few public methods
# pylint: disable=R0903

__author__ = "Josh Muszka", "Michael Quick"
__version__ = "1.0.0"

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class UnsupportedJobUrl(ValueError):
    """Raised when a URL is not a supported LinkedIn job posting."""


class JobScrapingError(RuntimeError):
    """Raised when a supported job posting cannot be retrieved or parsed."""


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
        try:
            response = requests.get(
                api_url,
                timeout=10,
                headers={"User-Agent": "AutoCoverLetter/1.0"},
            )
            response.raise_for_status()
        except requests.RequestException as error:
            raise JobScrapingError(
                "The LinkedIn job posting could not be retrieved."
            ) from error

        soup = BeautifulSoup(response.text, "html.parser")
        company_element = soup.select_one("a.topcard__org-name-link")
        description_element = (
            soup.select_one("div.show-more-less-html__markup")
            or soup.select_one("div.core-section-container__content")
        )

        if company_element is None or description_element is None:
            raise JobScrapingError(
                "The LinkedIn job posting did not contain the expected details."
            )

        self.company_name = company_element.get_text(" ", strip=True)
        description_text = description_element.get_text("\n", strip=True)
        self.description = description_text
        self.basic_qualifications = ""
        self.preferred_qualifications = ""

        sections = re.split(
            r"(?i)(?:basic|required) qualifications|preferred qualifications",
            description_text,
            maxsplit=2,
        )
        if sections:
            self.description = sections[0].strip()
        if len(sections) > 1:
            self.basic_qualifications = sections[1].strip()
        if len(sections) > 2:
            self.preferred_qualifications = sections[2].strip()

    @staticmethod
    def get_api_url_from_job_posting_url(url: str) -> str:
        """
        Converts a LinkedIn job posting URL into the corresponding API URL.

        Raises:
            UnsupportedJobUrl: If the URL is not a LinkedIn job posting.
        """
        parsed_url = urlparse(url.strip())
        valid_hosts = {"linkedin.com", "www.linkedin.com", "ca.linkedin.com"}
        job_match = re.search(
            r"/jobs/view/(?:[^/?#]*-)?(?P<job_id>\d+)(?:[/?#]|$)",
            parsed_url.path + ("?" + parsed_url.query if parsed_url.query else ""),
        )

        if parsed_url.scheme != "https" or parsed_url.hostname not in valid_hosts:
            raise UnsupportedJobUrl(
                "Enter a valid HTTPS LinkedIn job posting URL."
            )
        if job_match is None:
            raise UnsupportedJobUrl(
                "Enter a LinkedIn job URL containing a numeric job ID."
            )

        job_id = job_match.group("job_id")
        return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
