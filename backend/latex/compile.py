"""
Complies LaTex files into PDF
"""

import os
import subprocess


class CompileLatex:
    """
    Class to compile LaTeX files into PDF format.
    """

    @classmethod
    def compile(cls, response):
        """
        Compile the LaTeX file into a PDF.
        """
        # Get current working directory
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Create file paths with absolute paths
        tex_path = os.path.join(current_dir, "cover-letter.tex")

        # Write the LaTeX content to a file
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(response.strip("`").removeprefix("latex"))

        # Change to the directory where the tex file is located
        original_dir = os.getcwd()
        os.chdir(current_dir)

        try:
            # Run the xelatex command to compile the LaTeX file
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", "cover-letter.tex"],
                capture_output=True,
                text=True,
                check=False,
            )

            # Print output for debugging
            print("xelatex stdout:", result.stdout)
            print("xelatex stderr:", result.stderr)

            if result.returncode != 0:
                print(f"LaTeX compilation failed with return code {result.returncode}")
        finally:
            # Return to original directory
            os.chdir(original_dir)

        # Return the path to the generated PDF
        return os.path.join(current_dir, "cover-letter.pdf")
