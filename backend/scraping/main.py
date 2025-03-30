"""
Main class for Scraping backend
"""

__author__ = "Josh Muszka"
__email__ = "joshmuszka67@gmail.com"
__version__ = "1.0.0"

import re

import requests
from bs4 import BeautifulSoup

from ..scraping.job import Job


def get_job_api_url_from_job_posting_url(url=""):
    # Check if job post URL is valid and convert to an API url
    pattern = re.compile("^https://www.linkedin.com/jobs/view/[0-9]+")
    if pattern.match(url): return f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{url.split('/')[-1]}"
    else: raise RuntimeException("Invalid job posting URL - must be a LinkedIn job post")

def main():
    url = get_job_api_url_from_job_posting_url("https://www.linkedin.com/jobs/view/4072387977")
    soup = BeautifulSoup(requests.get(url).text, "html.parser")
    
    company_name = soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
    # print(company_name)

    description_html = soup.find("div", {"class": "core-section-container__content break-words"})
    
    elems = re.split('Description|Basic Qualifications|Preferred Qualifications', description_html.text)

    description = elems[1].strip()
    basic_qualifications = elems[2].strip()
    preferred_qualifications = elems[3].strip()

    job = Job(company_name, description, basic_qualifications, preferred_qualifications)



if __name__ == "__main__":
    main()
