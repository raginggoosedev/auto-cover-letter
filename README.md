# dataquest-2025

## About

In competitive job markets, a cover letter is crucial to stand out and highlight what you bring to the table. However, consistently writing personalized, high-quality cover letters consumes your valuable time and energy.

With autocoverletter, you can automate the mundane process of writing a tailored cover letter for each job application. Simply upload your resume and a link to the job posting, and you will have a clean, detailed cover letter within seconds.


## Installation

1. Clone the repository: `git clone https://github.com/raginggoosedev/auto-cover-letter.git && cd auto-cover-letter/`

2. Install dependencies:
    - `nodejs` and `npm` for the front-end
    - `python` and `uv` for the back-end
    - `LaTeX` (specifically, `XeTeX`) for compiling nice-looking PDFs
    - And copy `env.example` to `.env` and paste your OpenAI API key

3. Run the back-end:
    - `cd backend/`
    - `uv run -m routes.main`
    - (uv package manager will automatically install the dependencies before the first run)

4. Run the front-end:
    - `cd frontend/`
    - `npm install`
    - `npm run start`
