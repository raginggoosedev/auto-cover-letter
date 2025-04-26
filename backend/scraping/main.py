"""
Main script for Scraping backend demonstration.
"""

__author__ = "Josh Muszka", "Michael Quick"
__email__ = "joshmuszka67@gmail.com", "mwquick04@gmail.com"
__version__ = "1.0.0"

from scraping.job import Job


def main():
    """
    Scrape and print details from a LinkedIn job posting.
    """
    url = "https://www.linkedin.com/jobs/view/4072387977"
    job = Job(url)

    print("Company Name:", job.company_name)
    print("Job Description:", job.description)
    print("Basic Qualifications:", job.basic_qualifications)
    print("Preferred Qualifications:", job.preferred_qualifications)


if __name__ == "__main__":
    main()
