# Showcase hardening

The Git history remains the source of truth for what the team completed during
DataQuest 2025. The changes below were made afterward to prepare the project for
public review; they must not be described as features completed during the
hackathon.

| Area | Original hackathon MVP | Showcase hardening |
| --- | --- | --- |
| Routing | Localhost URLs and a separate deployment branch | Consistent same-origin `/api` contract and local React proxy |
| Input | UI offered PDF, DOC, and DOCX, while the backend parsed only PDF | PDF-only UI and API validation, 5 MiB limit, readable-text checks |
| Tone/style | UI sent a style value that the backend ignored | Validated tone guidance is included in the model input |
| Privacy | Fixed temporary resume path and resume text in logs | Resume parsed in memory, logging removed, model storage disabled |
| Factuality | Prompt allowed extrapolation | Prompt prohibits invented qualifications and treats inputs as untrusted data |
| PDF compilation | Shared filenames and no timeout | Per-request temporary directory, shell escape disabled, 30-second timeout |
| Errors | Mostly console output | Structured API errors and visible UI feedback |
| Quality | Boilerplate frontend test and Python lint workflow | Mocked backend tests, interaction-focused frontend tests, lint/test/build CI |
| Frontend tooling | Create React App and an obsolete dependency tree | Vite and Vitest with a current, smaller dependency tree |
| Documentation | Short install notes | Architecture, ownership, API, setup, privacy, limitations, and project status |

The retired deployment used Cloudflare and Nginx in front of the React and Flask
applications on one Linux server. A WSGI entry point remains in the repository,
but the exact Python process manager is not documented and is intentionally not
guessed.
