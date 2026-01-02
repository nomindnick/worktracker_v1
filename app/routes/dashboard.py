from datetime import date, timedelta

from flask import Blueprint, render_template

from app.models import Project

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Dashboard - projects organized by deadline proximity."""
    today = date.today()

    # Date boundaries
    tomorrow = today + timedelta(days=1)
    day_2 = today + timedelta(days=2)
    day_6 = today + timedelta(days=6)
    day_15 = today + timedelta(days=15)

    # Get all active projects
    active_projects = Project.query.filter_by(status='active').all()

    # Categorize projects by effective deadline
    due_today = []
    due_tomorrow = []
    due_next_5_days = []  # days 2-5
    due_next_2_weeks = []  # days 6-14

    for project in active_projects:
        deadline = project.effective_deadline

        if deadline is None:  # pragma: no cover (internal_deadline is required)
            continue  # Skip projects without deadlines
        elif deadline <= today:
            due_today.append(project)
        elif deadline == tomorrow:
            due_tomorrow.append(project)
        elif deadline < day_6:  # days 2-5
            due_next_5_days.append(project)
        elif deadline < day_15:  # days 6-14
            due_next_2_weeks.append(project)
        # Projects with deadline > 14 days out are not shown

    # Sort each category by effective_deadline, then by staleness (most stale first)
    def sort_key(p):
        deadline = p.effective_deadline or date.max
        return (deadline, -p.days_since_update)

    due_today.sort(key=sort_key)
    due_tomorrow.sort(key=sort_key)
    due_next_5_days.sort(key=sort_key)
    due_next_2_weeks.sort(key=sort_key)

    return render_template('dashboard.html',
        due_today=due_today,
        due_tomorrow=due_tomorrow,
        due_next_5_days=due_next_5_days,
        due_next_2_weeks=due_next_2_weeks,
        today=today
    )
