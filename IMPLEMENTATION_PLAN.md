# Legal Worklist Application — Implementation Plan

## Tech Stack

### Backend
- **Python 3.11+**
- **Flask** — Lightweight, well-documented, good for single-user local apps
- **SQLite** — File-based database, no server needed, easily backed up
- **SQLAlchemy** — ORM for database operations (cleaner than raw SQL, good for learning)

### Frontend
- **Jinja2 templates** — Server-side rendering, comes with Flask
- **Vanilla CSS + minimal JavaScript** — Keep it simple, no build step
- **HTMX** (optional) — For dynamic updates without full page reloads, if desired

### Why This Stack
- Python is familiar territory (Nick is learning Python)
- Flask is simple enough to understand and modify
- No npm, no webpack, no build process — just run the Python app
- SQLite file can be copied/backed up trivially
- All dependencies installable via pip

---

## Project Structure

```
legal-worklist/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py     # Dashboard/Today view
│   │   ├── projects.py      # Project CRUD
│   │   ├── followups.py     # Follow-up CRUD
│   │   ├── updates.py       # Status update CRUD
│   │   └── export.py        # CSV export
│   ├── templates/
│   │   ├── base.html        # Base template with nav
│   │   ├── dashboard.html
│   │   ├── projects/
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   └── form.html
│   │   ├── followups/
│   │   │   └── form.html
│   │   ├── updates/
│   │   │   └── form.html
│   │   └── archived.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js       # Minimal JS for interactions
├── data/
│   └── worklist.db          # SQLite database (gitignored)
├── exports/                  # CSV exports land here
├── config.py                 # Configuration
├── run.py                    # Entry point
├── requirements.txt
├── SPEC.md
├── IMPLEMENTATION_PLAN.md
└── README.md
```

---

## Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    project_name TEXT NOT NULL,
    matter_number TEXT,
    hard_deadline DATE,
    internal_deadline DATE NOT NULL,
    assigner TEXT NOT NULL DEFAULT 'Self',
    assigned_attorneys TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
    status TEXT NOT NULL CHECK (status IN ('active', 'archived')) DEFAULT 'active',
    estimated_hours REAL,
    actual_hours REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Follow-ups table
CREATE TABLE followups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    target_type TEXT NOT NULL CHECK (target_type IN ('associate', 'client', 'opposing_counsel', 'other')),
    target_name TEXT NOT NULL,
    due_date DATE NOT NULL,
    notes TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Status updates table
CREATE TABLE status_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    notes TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Indexes for common queries
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_internal_deadline ON projects(internal_deadline);
CREATE INDEX idx_followups_due_date ON followups(due_date);
CREATE INDEX idx_followups_completed ON followups(completed);
CREATE INDEX idx_status_updates_project ON status_updates(project_id);
CREATE INDEX idx_status_updates_created ON status_updates(created_at);
```

---

## Implementation Phases

### Phase 1: Foundation

**Goal:** Runnable Flask app with database, basic CRUD for projects.

**Tasks:**

1. Set up project structure and virtual environment
2. Create Flask app factory with configuration
3. Implement SQLAlchemy models (Project, FollowUp, StatusUpdate)
4. Create database initialization script
5. Build project routes:
   - GET /projects — List all active projects
   - GET /projects/new — New project form
   - POST /projects — Create project
   - GET /projects/<id> — Project detail
   - GET /projects/<id>/edit — Edit project form
   - POST /projects/<id> — Update project
   - POST /projects/<id>/archive — Archive project
6. Create base HTML template with navigation
7. Build project list and form templates
8. Add basic CSS styling

**Deliverable:** Can create, view, edit, and archive projects through the web interface.

---

### Phase 2: Status Updates

**Goal:** Add status update logging to projects.

**Tasks:**

1. Build status update routes:
   - GET /updates/new — New update form (with project selector)
   - GET /projects/<id>/updates/new — New update form (project pre-selected)
   - POST /updates — Create update
2. Create status update form template
3. Add status update log to project detail view
4. Display "last updated" and "days since update" on project list
5. Add quick "Add Update" button to project list rows

**Deliverable:** Can log status updates from dashboard or project detail, see update history on project detail.

---

### Phase 3: Follow-ups

**Goal:** Full follow-up management.

**Tasks:**

1. Build follow-up routes:
   - GET /followups — List all pending follow-ups (optional standalone view)
   - GET /followups/new — New follow-up form
   - GET /projects/<id>/followups/new — New follow-up (project pre-selected)
   - POST /followups — Create follow-up
   - POST /followups/<id>/complete — Mark complete
   - POST /followups/<id>/snooze — Snooze (push due date)
2. Create follow-up form template with quick-set date buttons
3. Add follow-up list to project detail view
4. Display pending follow-ups on project list

**Deliverable:** Can create, view, complete, and snooze follow-ups.

---

### Phase 4: Dashboard

**Goal:** The "Today" view that surfaces what needs attention.

**Tasks:**

1. Build dashboard route (GET / or GET /dashboard)
2. Query logic for:
   - Follow-ups due today
   - Overdue follow-ups
   - Projects with deadlines in next 7 days
   - Dusty projects (7-13 days = warning, 14+ days = critical)
3. Create dashboard template with sections
4. Add color coding (CSS classes for urgency levels)
5. Quick action buttons (complete follow-up, add update, view project)

**Deliverable:** Landing page shows actionable items at a glance.

---

### Phase 5: Export and Archive

**Goal:** CSV export and archived projects view.

**Tasks:**

1. Build export route (GET /export)
2. Generate CSV with active projects:
   - Client name, project name, matter number
   - Hard deadline, internal deadline
   - Assigned attorneys, priority
   - Most recent status update notes
   - Next follow-up date
3. Return CSV as file download
4. Build archived projects route (GET /archived)
5. Create archived projects list template
6. Add actual_hours prompt to archive flow

**Deliverable:** Can export active worklist to CSV, view archived projects.

---

### Phase 6: Polish

**Goal:** Refinements for daily usability.

**Tasks:**

1. Filtering and sorting on project list:
   - Filter by attorney, priority, assigner
   - Sort by deadline, priority, staleness
2. Search/filter for project selector dropdowns
3. Form validation and error messages
4. Confirmation dialogs for destructive actions
5. Improve mobile responsiveness (low priority but nice to have)
6. Add flash messages for success/error feedback
7. Keyboard shortcuts for common actions (stretch)

**Deliverable:** Polished, usable application ready for daily use.

---

## Key Implementation Details

### Staleness Calculation

Calculate days since last status update for each project:

```python
from datetime import datetime, timedelta
from sqlalchemy import func

def get_last_update_date(project_id):
    """Get the date of the most recent status update for a project."""
    update = StatusUpdate.query.filter_by(project_id=project_id)\
        .order_by(StatusUpdate.created_at.desc()).first()
    return update.created_at if update else None

def calculate_staleness(project):
    """Return days since last update, or days since creation if no updates."""
    last_update = get_last_update_date(project.id)
    reference_date = last_update or project.created_at
    return (datetime.now() - reference_date).days
```

For dashboard query, use a subquery to get last update date efficiently:

```python
from sqlalchemy import func, case

last_update_subq = db.session.query(
    StatusUpdate.project_id,
    func.max(StatusUpdate.created_at).label('last_update')
).group_by(StatusUpdate.project_id).subquery()

dusty_projects = db.session.query(Project)\
    .outerjoin(last_update_subq, Project.id == last_update_subq.c.project_id)\
    .filter(Project.status == 'active')\
    .filter(
        func.julianday('now') - func.julianday(
            func.coalesce(last_update_subq.c.last_update, Project.created_at)
        ) >= 7
    ).all()
```

### CSV Export Format

```python
import csv
from io import StringIO
from flask import Response

def export_csv():
    output = StringIO()
    writer = csv.writer(output)
    
    # Header row
    writer.writerow([
        'Client', 'Project', 'Matter #', 'Hard Deadline', 
        'Internal Deadline', 'Attorneys', 'Priority', 
        'Current Status', 'Next Follow-up'
    ])
    
    # Data rows
    for project in Project.query.filter_by(status='active').all():
        latest_update = StatusUpdate.query.filter_by(project_id=project.id)\
            .order_by(StatusUpdate.created_at.desc()).first()
        next_followup = FollowUp.query.filter_by(project_id=project.id, completed=False)\
            .order_by(FollowUp.due_date.asc()).first()
        
        writer.writerow([
            project.client_name,
            project.project_name,
            project.matter_number or '',
            project.hard_deadline.isoformat() if project.hard_deadline else '',
            project.internal_deadline.isoformat(),
            project.assigned_attorneys,
            project.priority,
            latest_update.notes if latest_update else '',
            next_followup.due_date.isoformat() if next_followup else ''
        ])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=worklist_{date.today()}.csv'}
    )
```

### Database Location

Store database in a user-accessible location:

```python
# config.py
import os
from pathlib import Path

# Default to ./data/worklist.db relative to project root
# Can be overridden with environment variable
BASE_DIR = Path(__file__).parent
DATA_DIR = Path(os.environ.get('WORKLIST_DATA_DIR', BASE_DIR / 'data'))
DATA_DIR.mkdir(exist_ok=True)

SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATA_DIR / 'worklist.db'}"
```

---

## Running the Application

### Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (first time only)
flask init-db

# Run development server
flask run

# Access at http://localhost:5000
```

### Requirements.txt

```
flask>=3.0
flask-sqlalchemy>=3.1
python-dateutil>=2.8
```

---

## Testing Strategy

### Manual Testing Checklist

For each phase, verify:

1. **Projects:**
   - [ ] Create project with all fields
   - [ ] Create project with minimal fields (just required)
   - [ ] Edit existing project
   - [ ] Archive project (with actual hours prompt)
   - [ ] View project detail
   - [ ] Project appears in list

2. **Status Updates:**
   - [ ] Add update from project detail
   - [ ] Add update from standalone form (select project)
   - [ ] Updates appear in project detail (newest first)
   - [ ] "Last updated" shows on project list
   - [ ] Days since update calculates correctly

3. **Follow-ups:**
   - [ ] Create follow-up with custom date
   - [ ] Create follow-up with quick-set buttons
   - [ ] Mark follow-up complete
   - [ ] Snooze follow-up
   - [ ] Follow-ups appear on project detail

4. **Dashboard:**
   - [ ] Due today section shows correct follow-ups
   - [ ] Overdue section shows past-due follow-ups
   - [ ] Upcoming deadlines shows next 7 days
   - [ ] Dusty warnings appear at 7 and 14 days
   - [ ] Color coding works

5. **Export:**
   - [ ] CSV downloads with correct filename
   - [ ] All active projects included
   - [ ] Archived projects excluded
   - [ ] Latest status and next follow-up populated

---

## Future Considerations (v2)

### LLM Integration Points

When adding natural language input:

1. **Input parsing** — Route natural language through local LLM to extract:
   - Intent (new project, update, follow-up, query)
   - Entities (client name, deadline, attorney names, etc.)
   
2. **Confidence handling** — If LLM confidence is low, fall back to form with pre-filled guesses

3. **Query interface** — "What's assigned to Rebecca?" → SQL query → formatted response

### Scheduling Engine

For scheduling suggestions:

1. Track available hours per day (configurable, default 8)
2. Sum estimated hours for projects by deadline
3. Suggest daily allocation based on deadline pressure
4. Reflow command when plans change

### Similarity Search

For time estimation learning:

1. On project archive, generate embedding of project description
2. Store embedding in separate table
3. On new project, find k-nearest archived projects
4. Display comparison of estimates vs. actuals
