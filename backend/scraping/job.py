"""
Job class for Scraping backend
"""

__author__ = "Josh Muszka"
__email__ = "joshmuszka67@gmail.com"
__version__ = "1.0.0"


class Job:
    company_name = ""
    description = ""
    basic_qualifications = ""
    preferred_qualifications = ""

    def __init__(self, company_name, description = "", basic_qualifications = "", preferred_qualifications = ""):
        self.company_name = company_name
        self.description = descriptions
        self.basic_qualifications = basic_qualifications
        self.preferred_qualifications = preferred_qualifications