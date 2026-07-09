# Lead-Generation-Data-Automation-Dashboard
=======

LeadFlow Generation is an API-first automation and web intelligence project.
It collects public data from reliable API/feed sources, stores it in SQLite, exports Excel/CSV files, and opens an interactive Streamlit dashboard.

## Sources

- GitHub repositories through the GitHub REST API
- Hacker News through the Algolia HN API
- RemoteOK jobs through a public JSON feed
- StackOverflow questions through the Stack Exchange API

## Why this is strong

This project does not bypass CAPTCHA or anti-bot systems. It uses official APIs and public feeds when available, which is cleaner and more professional for real freelance work.

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
## One-command run

```powershell
python start_leadflow.py
```

The launcher asks for:

- source
- keyword
- max pages

Then it runs the scraper and opens Streamlit automatically.

## Manual commands

Run all sources:

```powershell
python -m app.main --source all --keyword "python automation" --max-pages 1
```

Run dashboard only:

```powershell
streamlit run run_dashboard.py
```

## Windows double click

After installing dependencies, double-click:

```text
run_leadflow.bat
```

## Portfolio description

LeadFlow Pro is a Python automation and web intelligence dashboard that collects public data using official APIs and public JSON feeds, stores results in SQLite, prevents duplicates, scores records, exports Excel/CSV files, and provides a Streamlit dashboard for filtering and managing collected data. The project uses secure environment variables for API tokens and avoids bypassing CAPTCHA or anti-bot protections.
(Initial commit - Leadflow Generation automation dashboard)
