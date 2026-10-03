# Job Application AI Agent

This repository is a starter project for building an AI agent that helps identify relevant jobs, match your profile, and draft or prepare job applications.

## What this project does

The MVP includes:
- reading a resume
- loading job postings from a JSON file
- extracting keywords and skills
- ranking jobs by fit
- generating an application plan for top matches

This is a base for a future agent that can:
- scrape job boards
- generate tailored cover letters
- auto-fill application forms
- track submitted applications
- schedule follow-ups

## Project structure

- `app/` - Python source code
- `sample_resume.txt` - example resume text
- `sample_jobs.json` - example job postings
- `requirements.txt` - Python dependencies

## Quick start

1. Create a virtual environment
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Run the demo
   ```bash
   python -m app.main --resume sample_resume.txt --jobs sample_jobs.json --top 5
   ```

## Example output

The CLI prints ranked jobs with match scores and highlights matched vs missing skills.

## Recommended next steps

1. Add real job board scraping
2. Integrate an LLM for resume tailoring and cover letters
3. Add browser automation for form-based applications
4. Save application history in a database
5. Build a dashboard to monitor replies and interviews

## Notes

This repo intentionally keeps the first version simple and easy to extend. It is designed to help you build a real agent incrementally rather than trying to launch a full automation system all at once.
