# Legal Worklist Application — Specification

## Overview

A local-first web application for managing legal matters, follow-ups, and status tracking. Designed for a partner at a law firm who manages multiple projects, delegates to associates, and needs to stay on top of deadlines and follow-ups without being purely reactive to inbox demands.

## Problem Statement

Current state: An Excel spreadsheet that is rarely updated, with the email inbox functioning as the de facto task manager. This leads to:

1. **Overwhelm** — 20+ projects in a flat list make it hard to identify what needs attention now
2. **Reactive workflow** — Priority is set by whoever is asking, not by actual urgency or importance
3. **Forgotten follow-ups** — Follow-ups with associates, clients, and opposing counsel live in memory or scattered notes
4. **Dusty projects** — Low-priority items slide indefinitely until they become problems
5. **Update friction** — Editing Excel row-by-row is tedious, so status updates lag behind reality
6. **Lost context** — When returning to a project after time away, hard to remember where things stood

## Goals

1. **Proactive visibility** — Surface what needs attention today: due follow-ups, approaching deadlines, stale projects
2. **Low-friction status capture** — Make it easy to log quick updates as work happens
3. **Follow-up management** — Track who you're waiting on and when to poke them
4. **Context preservation** — Maintain a log of updates so you can quickly get back up to speed on any matter
5. **Backup and portability** — Export to CSV/Excel for firm document management system backup
6. **Retrospective support** — Archived projects with update history support annual self-evaluation

## Non-Goals (v1)

- LLM-powered natural language input (v2)
- Automated scheduling suggestions (v2)
- Time estimation learning based on similar past projects (v2)
- Integration with email, calendar, or billing systems
- Multi-user collaboration

---

## Data Model

### Projects

The core entity representing a legal matter.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | auto | Primary key |
| client_name | string | yes | Client name (e.g., "Lincoln USD") |
| project_name | string | yes | Brief description (e.g., "Facilities construction dispute") |
| matter_number | string | no | Firm's client/matter number (e.g., "2024-156") |
| hard_deadline | date | no | Court filing, statutory deadline, etc. |
| internal_deadline | date | yes | Target completion date |
| assigner | string | yes | Who assigned the work (self or another partner) |
| assigned_attorneys | string | yes | Comma-separated list of attorneys working on it |
| priority | enum | yes | "high", "medium", "low" |
| status | enum | yes | "active", "archived" |
| estimated_hours | decimal | no | Initial estimate of hours to complete |
| actual_hours | decimal | no | Logged when project is archived |
| created_at | datetime | auto | When project was created |
| updated_at | datetime | auto | Last modification timestamp |

### Follow-ups

Reminders to check in with someone about a project.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | auto | Primary key |
| project_id | integer | yes | Foreign key to Projects |
| target_type | enum | yes | "associate", "client", "opposing_counsel", "other" |
| target_name | string | yes | Name of person to follow up with |
| due_date | date | yes | When to follow up |
| notes | text | no | Context for the follow-up |
| completed | boolean | yes | Default false |
| completed_at | datetime | no | When marked complete |
| created_at | datetime | auto | When follow-up was created |

### Status Updates

Log of work done and current state of a project.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | auto | Primary key |
| project_id | integer | yes | Foreign key to Projects |
| notes | text | yes | What was done, where things stand, next steps |
| created_at | datetime | auto | Timestamp of the update |

---

## Features

### 1. Dashboard / "Today" View

The landing page showing what needs attention.

**Sections:**

1. **Follow-ups Due Today** — List of follow-ups with due_date = today, showing project name, target, and notes. Click to mark complete or snooze.

2. **Upcoming Deadlines** — Projects with hard_deadline or internal_deadline within the next 7 days, sorted by date. Show client, project name, deadline type, and date.

3. **Dusty Projects Warning** — Active projects with no status updates in:
   - 7-13 days: Yellow warning ("Getting stale")
   - 14+ days: Red warning ("Needs attention")
   
   Sorted by staleness. Excludes projects explicitly marked as "waiting on external" if we add that status.

4. **Overdue Follow-ups** — Follow-ups with due_date < today that aren't completed. Red highlight.

### 2. Projects List

Full list of active projects with filtering and sorting.

**Display columns:**
- Client name
- Project name
- Matter number
- Hard deadline
- Internal deadline
- Assigned attorneys
- Priority
- Last update (date of most recent status update)
- Days since last update

**Filtering:**
- By assigned attorney
- By priority
- By assigner
- By deadline range

**Sorting:**
- By deadline (hard or internal)
- By priority
- By last update (staleness)
- By client name

**Actions:**
- Click row to view project detail
- Quick button to add status update
- Quick button to add follow-up

### 3. Project Detail View

Full view of a single project with all its data.

**Sections:**

1. **Project Info** — All fields from the data model, editable
2. **Status Update Log** — Chronological list of all updates (newest first), with timestamp and notes
3. **Follow-ups** — List of follow-ups for this project, showing status (pending/completed/overdue)
4. **Actions:**
   - Add status update
   - Add follow-up
   - Archive project (prompts for actual_hours)
   - Edit project details

### 4. Add/Edit Project

Form for creating or editing a project.

**Fields:**
- Client name (text, required)
- Project name (text, required)
- Matter number (text, optional)
- Hard deadline (date picker, optional)
- Internal deadline (date picker, required, default = 2 weeks from today)
- Assigner (text, required, default = "Self")
- Assigned attorneys (text, required — comma-separated or multi-select)
- Priority (dropdown: high/medium/low, required, default = medium)
- Estimated hours (number, optional)
- Initial status update (text area, optional — becomes first status update entry)

### 5. Add Status Update

Low-friction form for logging work.

**From Dashboard or Project List:**
- Dropdown or search to select project
- Text area for notes
- Submit button

**From Project Detail:**
- Text area for notes (project already selected)
- Submit button

**Guidance text:** "What did you do? Where does it stand? What's next?"

### 6. Add/Edit Follow-up

Form for creating a follow-up reminder.

**Fields:**
- Project (dropdown/search, required — pre-filled if coming from project detail)
- Target type (dropdown: associate/client/opposing counsel/other, required)
- Target name (text, required)
- Due date (date picker, required)
- Notes (text area, optional)

**Quick-set buttons for due date:**
- Tomorrow
- 3 days
- 1 week
- 2 weeks
- Custom

### 7. Archive Project

When archiving a completed project:

1. Prompt for actual hours spent
2. Confirm archive action
3. Project moves to "archived" status
4. Project no longer appears in active views but remains in database

### 8. Archived Projects View

List of archived projects for retrospective purposes.

**Display:** Same columns as active projects list, plus actual_hours and archived_at date

**Use cases:**
- Year-end self-evaluation: review significant matters
- Time estimation reference: see how long similar past projects took
- Search for old matters if needed

### 9. Export

Export active projects to CSV for backup and sharing with legal assistant.

**Export includes:**
- Client name
- Project name
- Matter number
- Hard deadline
- Internal deadline
- Assigned attorneys
- Priority
- Current status (most recent status update notes)
- Next follow-up date (earliest pending follow-up)

**Export excludes:**
- Full status update history
- Archived projects
- Internal IDs

**Format:** CSV file download, filename includes date (e.g., `worklist_2025-01-06.csv`)

---

## UI/UX Requirements

### General

- Clean, minimal interface — not cluttered with features
- Color coding for urgency:
  - Red: Overdue, 14+ days stale
  - Yellow/Orange: Due today, 7-13 days stale
  - Green: On track
- Responsive but primarily designed for laptop use
- Fast — no unnecessary loading states for local data
- Keyboard shortcuts for common actions (stretch goal)

### Navigation

Simple top nav or sidebar:
- Dashboard (Today)
- Projects
- Follow-ups (optional standalone view)
- Archived
- Export

### Forms

- Auto-save or clear confirmation before navigating away
- Date pickers should default to sensible values
- Text areas should be reasonably sized (not tiny single-line inputs for notes)

---

## Technical Requirements

### Local-First

- All data stored locally in SQLite database
- No external network calls in v1
- Application runs on localhost

### Backup

- SQLite database file can be manually copied as backup
- CSV export for firm DMS upload
- Database location should be user-accessible (not buried in app directories)

### Security

- No authentication in v1 (single-user local app)
- No logging of sensitive content beyond what's in the database
- No cloud sync or telemetry

### Performance

- Should handle 100+ active projects without slowdown
- Status update log could grow large over time; paginate if needed

---

## v2 Roadmap (Deferred)

### LLM Natural Language Input

Add a chat/command input that accepts natural language:
- "New project for Lincoln USD, facilities issue, deadline Jan 15, assign to Rebecca"
- "Update on the Oakland construction matter — received docs from client, reviewing this week"
- "Follow up with Rebecca in 3 days on the Lincoln research"

Requires: Local LLM integration (Ollama), parsing logic, confidence thresholds, fallback to form-based input.

### Scheduling Suggestions

Based on deadlines, estimated hours, and priority:
- Suggest daily focus areas
- Reflow when disruptions hit (new urgent matter, sick day)
- "You have 6 hours of work due by Friday and it's Wednesday — here's a suggested plan"

Requires: Constraint satisfaction logic, estimate vs. actual tracking, disruption handling.

### Time Estimation Learning

When creating a new project:
- Search archived projects for similar matters (by client, project type, keywords)
- Show: "Similar project X took 15 hours, you estimated 8. Consider adjusting?"

Requires: Embedding-based similarity search or keyword matching, sufficient historical data.

---

## Success Criteria

The application is successful if:

1. Daily use is sustainable — opening the dashboard becomes a morning habit
2. Follow-ups stop falling through the cracks
3. Projects don't go dusty without awareness
4. Status updates are captured regularly (even if brief)
5. Weekly CSV export to firm DMS happens consistently
6. Year-end self-eval is easier because project history is documented
