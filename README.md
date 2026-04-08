# InternSync

InternSync is a Flask-based internship resource and chatbot web application. It includes a front-end UI in `Front_new`, a backend scraper in `BACKEND`, and a SQLite database stored under `Databases`.

## Project structure

- `Front_new/` - Main Flask application, routes, chat integration, and frontend templates.
- `BACKEND/` - Backend support code and web scraping utilities.
- `Databases/` - SQLite database files and initialization scripts.

## Environment setup

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Populate the secrets in `.env`:
   - `AZURE_OPENAI_API_KEY`
   - `FLASK_SECRET_KEY`
   - `YOUTUBE_API_KEY`
   - `GROQ_API_KEY`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If `requirements.txt` is not present, install Flask, requests, openai, and sqlite3 support manually.

## Run the app

From the repository root:

```bash
python Front_new/Main.py
```

Or run the frontend Flask application if using a different entrypoint.

## Secrets and Git safety

- `.env` is excluded from Git using `.gitignore`.
- `README.md` and `.env.example` are safe to keep in the repository.

## Notes

- Do not commit actual API keys or secret values.
- Keep `.env` local and never add it to source control.
