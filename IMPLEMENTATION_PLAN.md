# Legal Worklist Application — Implementation Plan

---

## Instructions for Claude Code

**IMPORTANT:** After completing each sprint, you MUST:

### 1. Write/Update Tests
- Write tests for all new functionality
- Update existing tests if behavior changed
- Run: `pytest --cov=app --cov=config --cov-report=term-missing --cov-fail-under=100`
- **All tests must pass with 100% code coverage** before the sprint is complete

### 2. Update This Document
1. Mark the completed sprint checkbox as `[x]`
2. Add a completion entry in the **Progress Log** section with:
   - Date completed
   - Sprint ID
   - Brief summary of what was done
   - Any decisions made or deviations from the plan
   - Any issues encountered and how they were resolved
3. If you created files not listed in the plan, add them to the **Files Created** section
4. If you made architectural decisions, document them in **Decisions Log**

This ensures future Claude Code sessions understand what has been done and can continue work seamlessly.

---

## Progress Tracking

### Overall Status

| Phase | Status | Sprints Completed |
|-------|--------|-------------------|
| Phase 1: Foundation | Complete | 5/5 |
| Phase 2: Status Updates | Complete | 2/2 |
| Phase 3: Follow-ups | Complete | 3/3 |
| Phase 4: Dashboard | Not Started | 0/2 |
| Phase 5: Export & Archive | Not Started | 0/2 |
| Phase 6: Polish | Not Started | 0/3 |

### Sprint Checklist

#### Phase 1: Foundation
- [x] Sprint 1.1: Project setup
- [x] Sprint 1.2: Database models and initialization
- [x] Sprint 1.3: Project routes (Create/List)
- [x] Sprint 1.4: Project routes (Detail/Edit/Archive)
- [x] Sprint 1.5: Templates and styling

#### Phase 2: Status Updates
- [x] Sprint 2.1: Status update routes and form
- [x] Sprint 2.2: Integrate into project views

#### Phase 3: Follow-ups
- [x] Sprint 3.1: Follow-up routes (Create/List)
- [x] Sprint 3.2: Follow-up routes (Complete/Snooze) and form
- [x] Sprint 3.3: Integrate into project views

#### Phase 4: Dashboard
- [ ] Sprint 4.1: Dashboard route and query logic
- [ ] Sprint 4.2: Dashboard template and styling

#### Phase 5: Export & Archive
- [ ] Sprint 5.1: CSV export functionality
- [ ] Sprint 5.2: Archived projects view

#### Phase 6: Polish
- [ ] Sprint 6.1: Filtering and sorting
- [ ] Sprint 6.2: Form validation and flash messages
- [ ] Sprint 6.3: Confirmation dialogs and responsiveness

---

## Progress Log

<!-- Add entries here after completing each sprint -->

| Date | Sprint | Summary | Decisions/Notes |
|------|--------|---------|-----------------|
| 2025-12-30 | 1.1 | Project setup complete - directory structure, venv, requirements.txt, config.py, run.py all in place | Database models, routes, and templates also partially created (ahead of schedule) |
| 2025-12-30 | 1.2 | Database models and initialization complete - added 6 indexes to models.py (status, internal_deadline, due_date, completed, project_id, created_at), recreated database with indexes | All verification criteria met: flask init-db works, all 3 tables exist with correct columns, all 6 indexes created |
| 2025-12-30 | 1.3 | Project routes (Create/List) complete - implemented POST /projects handler with form parsing, date conversion, and optional initial status update creation | All verification criteria met: GET /projects returns 200, GET /projects/new shows form, POST creates project in database |
| 2025-12-30 | 1.4 | Project routes (Detail/Edit/Archive) complete - implemented POST handlers for edit (update all fields) and archive (set status='archived') | All verification criteria met: detail/edit pages return 200, edit POST updates project, archive removes from active list, invalid ID returns 404 |
| 2025-12-30 | 1.5 | Templates and styling verified complete - all templates (base.html, list.html, detail.html, form.html) and CSS (style.css, 395 lines) were created during earlier sprints | All verification criteria met: navigation renders on all pages, forms are styled, table displays correctly, priority colors work (high=red, medium=yellow, low=green). **Phase 1 Foundation complete.** |
| 2025-12-30 | Testing | Testing infrastructure complete - 88 tests with 100% code coverage. Added pytest, pytest-cov, pytest-flask to requirements.txt. Created pyproject.toml with coverage config. Test files for config, app factory, models, and all routes. | 100% coverage enforced via fail_under=100. In-memory SQLite for fast tests. Fixtures for app, client, db_session, sample data. |
| 2025-12-30 | 2.1 | Status update routes and form complete - GET /updates/new with project dropdown, POST /updates/new creates updates, GET /projects/<id>/updates/new redirects with pre-selection | All verification criteria met: standalone form works, project dropdown populated, pre-selection via query param, POST creates update and redirects. 100 tests, 100% coverage. |
| 2025-12-30 | 2.2 | Integrated status updates into project views - added staleness properties to Project model (last_update_date, days_since_update, staleness_level), updated detail template to show status update history (newest first), updated list template with Last Updated column, Days Stale badge with color coding, and Add Update button | All verification criteria met: detail shows updates, list shows staleness columns with color badges (green/yellow/red), quick add button works. 111 tests, 100% coverage. **Phase 2 Status Updates complete.** |
| 2025-12-30 | 3.1 | Follow-up routes (Create/List) complete - implemented GET/POST /followups/new with project dropdown, project pre-selection via query param, form validation, and database creation. Added GET /projects/<id>/followups/new redirect route. Updated form.html template with project dropdown. | All verification criteria met: can view pending followups list, create followup from standalone form, create followup from project context with pre-selection. 123 tests, 100% coverage. |
| 2025-12-31 | 3.2 | Follow-up routes (Complete/Snooze) and form complete - implemented POST /followups/<id>/complete to mark follow-ups complete (sets completed=True, completed_at timestamp). Implemented POST /followups/<id>/snooze to update due_date by specified days (defaults to 1 day). Form template with quick-set date buttons and JavaScript was already in place from previous work. | All verification criteria met: can mark follow-up complete, completed follow-ups disappear from pending list, snooze updates due_date correctly, quick-set buttons work. Added 6 new tests for complete/snooze functionality. 130 tests total, 100% coverage. |
| 2025-12-31 | 3.3 | Follow-ups integrated into project views - added helper methods to Project model (get_pending_followups, get_completed_followups, pending_followup_count, next_followup). Updated projects/detail.html to display pending and completed follow-ups with Complete/Snooze action buttons. Updated projects/list.html to show Pending Follow-ups count and Next Follow-up date columns. Add Follow-up button was already present. | All verification criteria met: project detail shows all follow-ups with action buttons, can complete/snooze directly from detail, project list shows follow-up summary columns. Added 14 new tests (8 model tests, 6 route tests). 144 tests total, 100% coverage. **Phase 3 Follow-ups complete.** |

---

## Files Created

<!-- Track files created during implementation -->

| File | Sprint | Purpose |
|------|--------|---------|
| requirements.txt | 1.1 | Python dependencies (updated with testing deps) |
| config.py | 1.1 | Database and Flask configuration |
| run.py | 1.1 | Application entry point |
| app/__init__.py | 1.2 | Flask app factory with init-db CLI command |
| app/models.py | 1.2 | SQLAlchemy models (Project, FollowUp, StatusUpdate) with indexes |
| pyproject.toml | Testing | pytest/coverage config with 100% threshold |
| tests/conftest.py | Testing | Shared fixtures (app, client, db_session, sample data) |
| tests/test_config.py | Testing | Configuration tests (6 tests) |
| tests/test_app_factory.py | Testing | App factory and CLI tests (10 tests) |
| tests/test_models.py | Testing | Model tests (14 tests) |
| tests/routes/test_dashboard.py | Testing | Dashboard route tests (2 tests) |
| tests/routes/test_projects.py | Testing | Project CRUD tests (31 tests) |
| tests/routes/test_followups.py | Testing | Follow-up route tests (11 tests) |
| tests/routes/test_updates.py | Testing | Status update route tests (2 tests) |
| tests/routes/test_export.py | Testing | CSV export tests (12 tests) |

---

## Decisions Log

<!-- Document architectural decisions and deviations from the plan -->

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-12-30 | 100% code coverage requirement | Ensures code quality and catches regressions as features are added in Phases 2-6 |
| 2025-12-30 | pytest + pytest-cov + pytest-flask | Standard Flask testing stack with good coverage integration |
| 2025-12-30 | In-memory SQLite for tests | Fast test execution, isolated from production database |
| 2025-12-30 | Test stubs for incomplete routes | Test current behavior of stub routes, update tests when implemented |

---

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

## Implementation Phases & Sprints

### Phase 1: Foundation

**Goal:** Runnable Flask app with database, basic CRUD for projects.

#### Sprint 1.1: Project Setup

**Tasks:**
1. Create project directory structure as defined above
2. Set up virtual environment
3. Create `requirements.txt`:
   ```
   flask>=3.0
   flask-sqlalchemy>=3.1
   python-dateutil>=2.8
   ```
4. Create `config.py` with database configuration
5. Create `run.py` entry point

**Verification:**
- [ ] Can activate virtual environment
- [ ] Can install dependencies with `pip install -r requirements.txt`
- [ ] Project structure matches plan

---

#### Sprint 1.2: Database Models and Initialization

**Tasks:**
1. Create `app/__init__.py` with Flask app factory
2. Create `app/models.py` with SQLAlchemy models:
   - Project model with all fields from schema
   - FollowUp model with foreign key to Project
   - StatusUpdate model with foreign key to Project
3. Add `flask init-db` CLI command to create tables
4. Create `data/` directory (add to .gitignore)

**Verification:**
- [ ] `flask init-db` creates `data/worklist.db`
- [ ] Database has all three tables with correct columns
- [ ] Indexes are created

---

#### Sprint 1.3: Project Routes (Create/List)

**Tasks:**
1. Create `app/routes/__init__.py`
2. Create `app/routes/projects.py` with:
   - `GET /projects` — List all active projects
   - `GET /projects/new` — New project form
   - `POST /projects` — Create project
3. Register blueprint in app factory

**Verification:**
- [ ] `/projects` returns 200 (empty list OK)
- [ ] `/projects/new` shows a form
- [ ] Form submission creates project in database

---

#### Sprint 1.4: Project Routes (Detail/Edit/Archive)

**Tasks:**
1. Add to `app/routes/projects.py`:
   - `GET /projects/<id>` — Project detail view
   - `GET /projects/<id>/edit` — Edit project form
   - `POST /projects/<id>` — Update project
   - `POST /projects/<id>/archive` — Archive project
2. Handle 404 for non-existent projects

**Verification:**
- [ ] Can view project detail page
- [ ] Can edit project and see changes saved
- [ ] Archive removes project from active list
- [ ] Invalid project ID shows 404

---

#### Sprint 1.5: Templates and Styling

**Tasks:**
1. Create `app/templates/base.html` with:
   - HTML5 structure
   - Navigation (Dashboard, Projects, Export)
   - Content block
   - CSS link
2. Create `app/templates/projects/list.html`
3. Create `app/templates/projects/detail.html`
4. Create `app/templates/projects/form.html` (for new and edit)
5. Create `app/static/css/style.css` with basic styling:
   - Clean typography
   - Table styling
   - Form styling
   - Priority color coding (high=red, medium=yellow, low=green)

**Verification:**
- [ ] All pages render with consistent navigation
- [ ] Forms are usable and styled
- [ ] Project list displays nicely as table
- [ ] Priority colors display correctly

**Phase 1 Deliverable:** Can create, view, edit, and archive projects through the web interface.

---

### Phase 2: Status Updates

**Goal:** Add status update logging to projects.

#### Sprint 2.1: Status Update Routes and Form

**Tasks:**
1. Create `app/routes/updates.py` with:
   - `GET /updates/new` — New update form (with project selector dropdown)
   - `GET /projects/<id>/updates/new` — New update form (project pre-selected)
   - `POST /updates` — Create update
2. Create `app/templates/updates/form.html`
3. Register blueprint

**Verification:**
- [ ] Can access standalone update form at `/updates/new`
- [ ] Can access project-specific form at `/projects/<id>/updates/new`
- [ ] Form submission creates status update in database

---

#### Sprint 2.2: Integrate Updates into Project Views

**Tasks:**
1. Add status update history to `projects/detail.html`:
   - List updates newest-first
   - Show timestamp and notes
2. Update `projects/list.html`:
   - Add "Last Updated" column with date
   - Add "Days Since Update" column with staleness indicator
   - Add quick "Add Update" button/link per row
3. Implement staleness calculation helper function

**Verification:**
- [ ] Project detail shows all status updates
- [ ] Project list shows last update date
- [ ] Days since update calculates correctly
- [ ] Quick add button navigates to update form

**Phase 2 Deliverable:** Can log status updates from dashboard or project detail, see update history on project detail.

---

### Phase 3: Follow-ups

**Goal:** Full follow-up management.

#### Sprint 3.1: Follow-up Routes (Create/List)

**Tasks:**
1. Create `app/routes/followups.py` with:
   - `GET /followups` — List all pending follow-ups (grouped by due date)
   - `GET /followups/new` — New follow-up form
   - `GET /projects/<id>/followups/new` — New follow-up (project pre-selected)
   - `POST /followups` — Create follow-up
2. Register blueprint

**Verification:**
- [ ] Can view list of all pending follow-ups
- [ ] Can create follow-up from standalone form
- [ ] Can create follow-up from project context

---

#### Sprint 3.2: Follow-up Routes (Complete/Snooze) and Form

**Tasks:**
1. Add to `app/routes/followups.py`:
   - `POST /followups/<id>/complete` — Mark complete (set completed=1, completed_at)
   - `POST /followups/<id>/snooze` — Snooze (accept days parameter, update due_date)
2. Create `app/templates/followups/form.html` with:
   - Project selector (or hidden field if pre-selected)
   - Target type dropdown (associate, client, opposing_counsel, other)
   - Target name text field
   - Due date picker
   - Quick-set date buttons: Tomorrow, +3 days, +1 week, +2 weeks
   - Notes textarea

**Verification:**
- [ ] Can mark follow-up complete
- [ ] Complete follow-up disappears from pending list
- [ ] Snooze updates due date correctly
- [ ] Quick-set buttons work in form

---

#### Sprint 3.3: Integrate Follow-ups into Project Views

**Tasks:**
1. Add follow-up list to `projects/detail.html`:
   - Pending follow-ups (with complete/snooze buttons)
   - Completed follow-ups (collapsed or separate section)
2. Update `projects/list.html`:
   - Show pending follow-up count
   - Show next follow-up date
3. Add "Add Follow-up" button to project detail

**Verification:**
- [ ] Project detail shows all follow-ups
- [ ] Can complete/snooze directly from project detail
- [ ] Project list shows follow-up summary
- [ ] Add button works

**Phase 3 Deliverable:** Can create, view, complete, and snooze follow-ups.

---

### Phase 4: Dashboard

**Goal:** The "Today" view that surfaces what needs attention.

#### Sprint 4.1: Dashboard Route and Query Logic

**Tasks:**
1. Create `app/routes/dashboard.py` with `GET /` or `GET /dashboard`
2. Implement query logic for:
   - Follow-ups due today
   - Overdue follow-ups (past due date, not completed)
   - Projects with deadlines in next 7 days
   - Dusty projects (no update in 7+ days):
     - Warning level: 7-13 days
     - Critical level: 14+ days
3. Use efficient subqueries for staleness calculation

**Verification:**
- [ ] Route returns correct data for each category
- [ ] Staleness calculation is efficient (single query)
- [ ] Edge cases handled (no updates, just created, etc.)

---

#### Sprint 4.2: Dashboard Template and Styling

**Tasks:**
1. Create `app/templates/dashboard.html` with sections:
   - Overdue follow-ups (red section)
   - Due today (yellow section)
   - Upcoming deadlines (blue section)
   - Dusty projects (orange/red gradient by severity)
2. Add CSS classes for urgency levels:
   - `.urgency-critical` (red)
   - `.urgency-warning` (yellow/orange)
   - `.urgency-info` (blue)
3. Add quick action buttons:
   - Complete follow-up (inline)
   - Add update (link to form)
   - View project (link)
4. Set dashboard as home page (`/`)

**Verification:**
- [ ] Dashboard is the landing page
- [ ] All sections render correctly
- [ ] Color coding works
- [ ] Quick actions function properly

**Phase 4 Deliverable:** Landing page shows actionable items at a glance.

---

### Phase 5: Export & Archive

**Goal:** CSV export and archived projects view.

#### Sprint 5.1: CSV Export Functionality

**Tasks:**
1. Create `app/routes/export.py` with `GET /export`
2. Generate CSV with columns:
   - Client, Project, Matter #
   - Hard Deadline, Internal Deadline
   - Attorneys, Priority
   - Current Status (most recent update notes)
   - Next Follow-up (date of next pending follow-up)
3. Return as file download with filename `worklist_YYYY-MM-DD.csv`
4. Create `exports/` directory for reference (actual download goes to browser)

**Verification:**
- [ ] CSV downloads with correct filename
- [ ] All active projects included
- [ ] Archived projects excluded
- [ ] All columns populated correctly

---

#### Sprint 5.2: Archived Projects View

**Tasks:**
1. Add `GET /archived` route to projects.py (or separate file)
2. Create `app/templates/archived.html`:
   - List archived projects
   - Show actual hours vs estimated
   - Option to unarchive (reactivate)
3. Update archive flow:
   - When archiving, prompt for actual_hours
   - Could be modal or intermediate page
4. Add "Archived" link to navigation

**Verification:**
- [ ] Archived projects visible at `/archived`
- [ ] Archive prompts for actual hours
- [ ] Can unarchive a project
- [ ] Navigation includes archived link

**Phase 5 Deliverable:** Can export active worklist to CSV, view archived projects.

---

### Phase 6: Polish

**Goal:** Refinements for daily usability.

#### Sprint 6.1: Filtering and Sorting

**Tasks:**
1. Add filter controls to project list:
   - Filter by attorney (dropdown from existing values)
   - Filter by priority (high/medium/low)
   - Filter by assigner
2. Add sorting options:
   - Sort by deadline (default)
   - Sort by priority
   - Sort by staleness (days since update)
3. Preserve filter/sort in URL query parameters

**Verification:**
- [ ] Filters work correctly
- [ ] Sorting works correctly
- [ ] Can combine filter and sort
- [ ] URL reflects current filter/sort state

---

#### Sprint 6.2: Form Validation and Flash Messages

**Tasks:**
1. Add server-side form validation:
   - Required fields checked
   - Date format validation
   - Reasonable value ranges
2. Add Flask flash messages:
   - Success: "Project created", "Update saved", etc.
   - Error: Validation failures
3. Display flash messages in base template
4. Add client-side validation (HTML5 required, pattern attributes)

**Verification:**
- [ ] Cannot submit invalid forms
- [ ] Error messages display clearly
- [ ] Success messages confirm actions
- [ ] Client-side validation provides immediate feedback

---

#### Sprint 6.3: Confirmation Dialogs and Responsiveness

**Tasks:**
1. Add confirmation dialogs for destructive actions:
   - Archive project
   - Complete follow-up
   - (Use simple JavaScript confirm() or modal)
2. Improve mobile responsiveness:
   - Responsive tables (horizontal scroll or card view)
   - Touch-friendly buttons
   - Readable on small screens
3. Create `app/static/js/app.js` for any JavaScript needs

**Verification:**
- [ ] Archive asks for confirmation
- [ ] Application usable on mobile device
- [ ] Tables don't break on small screens

**Phase 6 Deliverable:** Polished, usable application ready for daily use.

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
