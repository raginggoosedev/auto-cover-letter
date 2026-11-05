"""Isolated XeLaTeX compilation tests."""

from pathlib import Path
import subprocess

import pytest

from backend.latex import compile as compile_module
from backend.latex.compile import (
    CompileLatex,
    LatexCompilationError,
    LatexCompilationTimeout,
)


def test_compile_returns_bytes_and_removes_temporary_directory(monkeypatch):
    captured_directory = None

    def fake_run(command, **kwargs):
        nonlocal captured_directory
        captured_directory = Path(kwargs["cwd"])
        assert "-no-shell-escape" in command
        assert kwargs["timeout"] == 30
        (captured_directory / "cover-letter.pdf").write_bytes(b"%PDF-result")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(compile_module.subprocess, "run", fake_run)

    result = CompileLatex.compile("\\documentclass{article}")

    assert result == b"%PDF-result"
    assert captured_directory is not None
    assert not captured_directory.exists()


def test_compile_reports_invalid_latex(monkeypatch):
    monkeypatch.setattr(
        compile_module.subprocess,
        "run",
        lambda command, **_kwargs: subprocess.CompletedProcess(command, 1, "", "error"),
    )

    with pytest.raises(LatexCompilationError, match="could not compile"):
        CompileLatex.compile("invalid")


def test_compile_reports_timeout(monkeypatch):
    def timeout(command, **_kwargs):
        raise subprocess.TimeoutExpired(command, 30)

    monkeypatch.setattr(compile_module.subprocess, "run", timeout)

    with pytest.raises(LatexCompilationTimeout, match="time limit"):
        CompileLatex.compile("\\documentclass{article}")


def test_compile_reports_missing_xelatex(monkeypatch):
    def missing_binary(_command, **_kwargs):
        raise FileNotFoundError("xelatex")

    monkeypatch.setattr(compile_module.subprocess, "run", missing_binary)

    with pytest.raises(LatexCompilationError, match="not installed"):
        CompileLatex.compile("\\documentclass{article}")
