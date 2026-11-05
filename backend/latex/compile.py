"""Compile generated LaTeX into an isolated PDF document."""

# Disable pylint for too few public methods
# pylint: disable=R0903

from pathlib import Path
import subprocess
import tempfile


class LatexCompilationError(RuntimeError):
    """Raised when XeLaTeX cannot create a PDF."""


class LatexCompilationTimeout(LatexCompilationError):
    """Raised when XeLaTeX exceeds the configured time limit."""


class CompileLatex:
    """
    Class to compile LaTeX files into PDF format.
    """

    @classmethod
    def compile(cls, latex_source: str, timeout_seconds: int = 30) -> bytes:
        """Compile ``latex_source`` and return the PDF bytes.

        Every request receives its own temporary directory. The directory is
        removed before this method returns, including on compilation failure.
        """
        if not latex_source or not latex_source.strip():
            raise LatexCompilationError("No LaTeX content was provided.")

        with tempfile.TemporaryDirectory(prefix="auto-cover-letter-") as temp_dir:
            working_directory = Path(temp_dir)
            tex_path = working_directory / "cover-letter.tex"
            pdf_path = working_directory / "cover-letter.pdf"
            tex_path.write_text(latex_source, encoding="utf-8")

            try:
                result = subprocess.run(
                    [
                        "xelatex",
                        "-no-shell-escape",
                        "-halt-on-error",
                        "-interaction=nonstopmode",
                        tex_path.name,
                    ],
                    cwd=working_directory,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    check=False,
                    timeout=timeout_seconds,
                )
            except FileNotFoundError as error:
                raise LatexCompilationError(
                    "XeLaTeX is not installed or is not available on PATH."
                ) from error
            except subprocess.TimeoutExpired as error:
                raise LatexCompilationTimeout(
                    "LaTeX compilation exceeded the time limit."
                ) from error

            if result.returncode != 0 or not pdf_path.exists():
                raise LatexCompilationError(
                    "XeLaTeX could not compile the generated document."
                )

            return pdf_path.read_bytes()
