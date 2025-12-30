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

## Reference Documents

- `SPEC.md` - Feature specification and requirements
- `IMPLEMENTATION_PLAN.md` - Tech stack rationale, 6-phase roadmap, database schema
