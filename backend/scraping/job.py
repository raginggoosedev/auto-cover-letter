"""
Job class for Scraping backend
"""

__author__ = "Josh Muszka"
__email__ = "joshmuszka67@gmail.com"
__version__ = "1.0.0"

import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import re


class Job:
    company_name = ""
    description = ""
    basic_qualifications = ""
    preferred_qualifications = ""

    def __init__(self, url):
        url = self._get_job_api_url_from_job_posting_url(url)
        soup = BeautifulSoup(requests.get(url).text, "html.parser")

        self.company_name = soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()

        description_html = soup.find("div", {"class": "core-section-container__content break-words"})

        elems = re.split('Description|Basic Qualifications|Preferred Qualifications', description_html.text)
        
        if len(elems) >= 2: self.description = elems[1].strip()
        if len(elems) >= 3: self.basic_qualifications = elems[2].strip()
        if len(elems) >= 4: self.preferred_qualifications = elems[3].strip()

        if len(elems) == 0: self.description = elems[0].strip()

    def _get_job_api_url_from_job_posting_url(self, url=""):
        # Check if job post URL is valid and convert to an API url
        pattern = re.compile("^https://www.linkedin.com/jobs/view/[0-9]+")
        if pattern.match(url):
            return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{url.split('/')[-1]}"
        else:
            raise Exception("Invalid job posting URL - must be a LinkedIn job post")
