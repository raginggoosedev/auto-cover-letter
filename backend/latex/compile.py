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
        # Write the LaTeX content to a file

        with open("../latex/resume.tex", "+w") as f:
            f.write(response.strip("`").removeprefix("latex"))

        # Create a pipe to handle the subprocess output
        read, write = os.pipe() 
        os.write(write, b"\n")
        os.close(write)
        # Run the xelatex command to compile the LaTeX file
        subprocess.run(["xelatex", "../latex/resume.tex", ])
        # Clean up auxiliary files generated during compilation
        #subprocess.run(["rm", "../latex/resume.aux", ])
        # Remove the log file generated during compilation
        #subprocess.run(["rm", "../latex/resume.log", ])
        # Move the generated PDF to the desired location
        #subprocess.run(["mv", "resume.pdf", "../latex/resume.pdf"])
