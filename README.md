# Customer Feedback Analyzer

A Flask and SQLite application for collecting customer feedback and summarizing common themes.

## Team workflow

- Each member works on their assigned file on a feature branch.
- Commit and push your changes to that branch.
- Open a pull request into `main` and ask the group leader for review.
- Do not commit directly to `main` unless the group leader explicitly agrees.

## Setup

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run the app with `python app.py`.
5. Open `http://127.0.0.1:5000` in your browser.

## Project files

- `app.py`: Flask application and feedback storage.
- `preprocessing.py`: cleans feedback text.
- `keyword_counter.py`: counts frequent keywords.
- `analytics_api.py`: analytics endpoint logic.
- `static/`: JavaScript for the form, summary cards, keyword chart, and feedback table.
- `templates/index.html`: shared dashboard page.
- `tests/test_app.py`: starter tests.

The SQLite database is created locally when the app runs. Do not commit database files or virtual environments.
