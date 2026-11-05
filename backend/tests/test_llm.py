"""Prompt construction and Responses API adapter tests."""

from types import SimpleNamespace

import pytest

from backend.llm import llm as llm_module
from backend.llm.llm import (
    CoverLetterContext,
    CoverLetterPrompt,
    Llm,
    LlmConfigurationError,
    LlmGenerationError,
)


class FakeJob:
    company_name = "PRI Engineering"
    description = "Build internal web applications."
    basic_qualifications = "REST APIs and Git"
    preferred_qualifications = "Azure exposure"

    def __init__(self, url):
        assert url.startswith("https://www.linkedin.com/jobs/view/")


def test_prompt_is_fact_constrained_and_uses_tone(monkeypatch):
    monkeypatch.setattr(llm_module, "Job", FakeJob)

    prompt = Llm.create_prompt(
        CoverLetterContext(
            job_url="https://www.linkedin.com/jobs/view/123456789",
            extra_details="I enjoy data-heavy problems.",
            letter_template="\\documentclass{article}",
            comments="Shorten the opening.",
            resume_text="Nicholas Woo - Software Developer",
            tone="modern",
        )
    )

    assert "Never invent" in prompt.instructions
    assert "untrusted reference data" in prompt.instructions
    assert "concise, direct" in prompt.input_text
    assert "Nicholas Woo" in prompt.input_text
    assert "Shorten the opening" in prompt.input_text


def test_prompt_rejects_unknown_tone(monkeypatch):
    monkeypatch.setattr(llm_module, "Job", FakeJob)

    with pytest.raises(ValueError, match="supported writing tone"):
        Llm.create_prompt(
            CoverLetterContext(
                job_url="https://www.linkedin.com/jobs/view/123456789",
                extra_details="",
                letter_template="template",
                comments="",
                resume_text="resume",
                tone="dramatic",
            )
        )


def test_generate_requires_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(LlmConfigurationError, match="OPENAI_API_KEY"):
        Llm.generate(CoverLetterPrompt("facts only", "input"))


def test_generate_uses_responses_api_without_storage(monkeypatch):
    captured = {}

    class FakeResponses:
        @staticmethod
        def create(**kwargs):
            captured.update(kwargs)
            return SimpleNamespace(output_text="  \\documentclass{article}  ")

    class FakeClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.responses = FakeResponses()

    monkeypatch.setattr(llm_module, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")

    result = Llm.generate(CoverLetterPrompt("facts only", "input"))

    assert result == "\\documentclass{article}"
    assert captured["api_key"] == "test-key"
    assert captured["timeout"] == 30.0
    assert captured["max_retries"] == 1
    assert captured["model"] == "test-model"
    assert captured["instructions"] == "facts only"
    assert captured["input"] == "input"
    assert captured["store"] is False


def test_generate_rejects_empty_output(monkeypatch):
    class FakeResponses:
        @staticmethod
        def create(**_kwargs):
            return SimpleNamespace(output_text="   ")

    class FakeClient:
        def __init__(self, **kwargs):
            assert kwargs["api_key"] == "test-key"
            self.responses = FakeResponses()

    monkeypatch.setattr(llm_module, "OpenAI", FakeClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    with pytest.raises(LlmGenerationError, match="empty response"):
        Llm.generate(CoverLetterPrompt("facts only", "input"))
