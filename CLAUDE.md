# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Legal Work Tracker - A local-first Flask application for managing legal matters, deadlines, follow-ups, and status updates. Single-user desktop application with SQLite storage, designed for law firm partners tracking multiple projects.

## Development Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database (first time)
flask init-db

# Run development server
flask run
# Access at http://localhost:5000

# Run tests with coverage (required before completing any sprint)
pytest --cov=app --cov=config --cov-report=term-missing --cov-fail-under=100

# Run tests with HTML coverage report
pytest --cov=app --cov=config --cov-report=html

# Run specific test file
pytest tests/routes/test_projects.py -v
```

## Architecture

**Tech Stack:** Python 3.11+, Flask, SQLAlchemy, SQLite, Jinja2 templates, vanilla CSS/JS

**Project Structure:**
```
app/
├── __init__.py          # Flask app factory
├── models.py            # SQLAlchemy models (Project, FollowUp, StatusUpdate)
├── routes/              # Feature-based route handlers
│   ├── dashboard.py     # Today view with urgency filtering
│   ├── projects.py      # Project CRUD
│   ├── followups.py     # Follow-up management
│   ├── updates.py       # Status update logging
│   └── export.py        # CSV export
├── templates/           # Jinja2 templates
└── static/              # CSS and minimal JS
data/                    # SQLite database (worklist.db)
tests/                   # Test suite (pytest)
├── conftest.py          # Shared fixtures
├── test_config.py       # Config tests
├── test_app_factory.py  # App factory tests
├── test_models.py       # Model tests
└── routes/              # Route tests (one per blueprint)
```

**Data Model:**
- **Projects**: Core entity with client/matter info, deadlines, priority, attorneys
- **Follow-ups**: Reminders with target type (associate/client/opposing counsel), due dates, completion tracking
- **Status Updates**: Activity log entries linked to projects

## Key Implementation Patterns

**Staleness Calculation:** Days since last status update (or creation if none)
- 7-13 days: Yellow warning
- 14+ days: Red warning

**Dashboard Categories:**
- Follow-ups due today
- Upcoming deadlines (within 7 days)
- Dusty projects (no updates 7+ days)
- Overdue follow-ups

**CSV Export:** Active projects with latest status and next follow-up, filename pattern `worklist_YYYY-MM-DD.csv`

**Database Location:** Defaults to `./data/`, overridable via `WORKLIST_DATA_DIR` environment variable

## Testing Requirements

**100% code coverage is required.** Tests must pass with full coverage before any sprint is considered complete.

**Test Infrastructure:**
- **pytest** with pytest-cov for coverage
- **In-memory SQLite** for fast test execution
- **Fixtures** in `tests/conftest.py`: `app`, `client`, `db_session`, `sample_project`, `sample_followup`, `runner`

**Sprint Completion Checklist:**
1. Write/update tests for new functionality
2. Run `pytest --cov=app --cov=config --cov-report=term-missing --cov-fail-under=100`
3. All tests must pass with 100% coverage
4. Update IMPLEMENTATION_PLAN.md with sprint completion details

**Test Organization:**
- `test_config.py` - Configuration loading tests
- `test_app_factory.py` - App factory and CLI command tests
- `test_models.py` - Model creation, relationships, cascade deletes
- `tests/routes/test_*.py` - One test file per blueprint

## Reference Documents

- `SPEC.md` - Feature specification and requirements
- `IMPLEMENTATION_PLAN.md` - Tech stack rationale, 6-phase roadmap, database schema
