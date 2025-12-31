# Legal Work Tracker

A local-first Flask application for law firm partners managing multiple legal matters. Track deadlines, follow-ups, and project status without cloud dependencies.

## Features

- **Dashboard** - Urgency-based "Today" view showing overdue items, due today, upcoming deadlines, and stale projects
- **Project Management** - Track clients, matters, deadlines, attorneys, and priority with filtering/sorting
- **Follow-ups** - Schedule reminders for associates, clients, or opposing counsel with snooze/complete actions
- **Status Updates** - Low-friction logging to maintain project history and prevent staleness
- **Staleness Alerts** - Visual warnings for projects without updates (yellow: 7-13 days, red: 14+ days)
- **CSV Export** - Download active projects for backup or reporting
- **Archive** - Track completed projects with actual hours for retrospective analysis

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask init-db
flask run
```

Open http://localhost:5000

## Tech Stack

Python 3.11+ / Flask / SQLAlchemy / SQLite / Jinja2 / Vanilla CSS+JS

## Development

```bash
# Run tests with 100% coverage requirement
pytest --cov=app --cov=config --cov-report=term-missing --cov-fail-under=100
```

## Configuration

Set `WORKLIST_DATA_DIR` environment variable to customize database location (defaults to `./data/`).

## License

MIT
