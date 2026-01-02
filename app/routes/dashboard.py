from datetime import date, timedelta

from flask import Blueprint, render_template

from app.models import Project

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Dashboard - projects organized by next task due date."""
    today = date.today()

    # Date boundaries
    tomorrow = today + timedelta(days=1)
    day_7 = today + timedelta(days=7)
    day_14 = today + timedelta(days=14)

    # Get all active projects
    active_projects = Project.query.filter_by(status='active').all()

    # Categorize projects by their next task due date
    due_today = []       # Next task due today or overdue
    due_tomorrow = []    # Next task due tomorrow
    due_this_week = []   # Next task due in 2-7 days
    due_later = []       # Next task due in 8-14 days
    no_tasks = []        # Projects with no pending tasks

    for project in active_projects:
        next_task = project.next_task

        if next_task is None:
            no_tasks.append(project)
        elif next_task.due_date <= today:
            due_today.append(project)
        elif next_task.due_date == tomorrow:
            due_tomorrow.append(project)
        elif next_task.due_date <= day_7:
            due_this_week.append(project)
        elif next_task.due_date <= day_14:
            due_later.append(project)
        # Projects with next task > 14 days out are not shown on dashboard

    # Sort each category by next task due date, then by task priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}

    def sort_key(p):
        # All projects in these lists have a next_task (they were categorized based on it)
        next_task = p.next_task
        return (next_task.due_date, priority_order.get(next_task.priority, 1))

    due_today.sort(key=sort_key)
    due_tomorrow.sort(key=sort_key)
    due_this_week.sort(key=sort_key)
    due_later.sort(key=sort_key)

    # Sort no_tasks projects by staleness (most stale first)
    no_tasks.sort(key=lambda p: -p.days_since_update)

    return render_template('dashboard.html',
        due_today=due_today,
        due_tomorrow=due_tomorrow,
        due_this_week=due_this_week,
        due_later=due_later,
        no_tasks=no_tasks,
        today=today
    )
