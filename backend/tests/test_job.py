"""LinkedIn URL validation and parsing tests."""

import requests
import pytest

from backend.scraping import job as job_module
from backend.scraping.job import Job, JobScrapingError, UnsupportedJobUrl


def test_job_url_accepts_numeric_and_slugged_linkedin_urls():
    assert Job.get_api_url_from_job_posting_url(
        "https://www.linkedin.com/jobs/view/123456789/?trackingId=test"
    ).endswith("/123456789")
    assert Job.get_api_url_from_job_posting_url(
        "https://ca.linkedin.com/jobs/view/software-developer-987654321"
    ).endswith("/987654321")


@pytest.mark.parametrize(
    "url",
    [
        "http://www.linkedin.com/jobs/view/123456789",
        "https://linkedin.example.com/jobs/view/123456789",
        "https://www.linkedin.com/feed/",
    ],
)
def test_job_url_rejects_unsupported_urls(url):
    with pytest.raises(UnsupportedJobUrl):
        Job.get_api_url_from_job_posting_url(url)


def test_job_parses_company_and_qualification_sections(monkeypatch):
    class FakeResponse:
        text = """
            <a class="topcard__org-name-link">PRI Engineering</a>
            <div class="show-more-less-html__markup">
              Build internal software.
              Required Qualifications
              REST APIs and Git.
              Preferred Qualifications
              Azure exposure.
            </div>
        """

        @staticmethod
        def raise_for_status():
            return None

    monkeypatch.setattr(job_module.requests, "get", lambda *_args, **_kwargs: FakeResponse())

    job = Job("https://www.linkedin.com/jobs/view/123456789")

    assert job.company_name == "PRI Engineering"
    assert job.description == "Build internal software."
    assert job.basic_qualifications == "REST APIs and Git."
    assert job.preferred_qualifications == "Azure exposure."


def test_job_wraps_network_errors(monkeypatch):
    def fail_request(*_args, **_kwargs):
        raise requests.RequestException("offline")

    monkeypatch.setattr(job_module.requests, "get", fail_request)

    with pytest.raises(JobScrapingError, match="could not be retrieved"):
        Job("https://www.linkedin.com/jobs/view/123456789")


def test_job_rejects_unexpected_markup(monkeypatch):
    class FakeResponse:
        text = "<html><body>No job here</body></html>"

        @staticmethod
        def raise_for_status():
            return None

    monkeypatch.setattr(job_module.requests, "get", lambda *_args, **_kwargs: FakeResponse())

    with pytest.raises(JobScrapingError, match="expected details"):
        Job("https://www.linkedin.com/jobs/view/123456789")
