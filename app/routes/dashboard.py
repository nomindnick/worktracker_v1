from datetime import date, timedelta

from flask import Blueprint, render_template
from sqlalchemy import or_, and_

from app import db
from app.models import Project, FollowUp

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Dashboard / Today view - shows what needs attention."""
    today = date.today()
    next_week = today + timedelta(days=7)

    # 1. Follow-ups due today (uncompleted, due_date == today, active projects only)
    followups_today = FollowUp.query.join(Project).filter(
        FollowUp.completed == False,
        FollowUp.due_date == today,
        Project.status == 'active'
    ).order_by(FollowUp.due_date.asc()).all()

    # 2. Overdue follow-ups (uncompleted, due_date < today, active projects only)
    followups_overdue = FollowUp.query.join(Project).filter(
        FollowUp.completed == False,
        FollowUp.due_date < today,
        Project.status == 'active'
    ).order_by(FollowUp.due_date.asc()).all()

    # 3. Projects with deadlines in next 7 days (active only)
    upcoming_deadlines = Project.query.filter(
        Project.status == 'active',
        or_(
            and_(Project.hard_deadline != None, Project.hard_deadline <= next_week),
            and_(Project.internal_deadline != None, Project.internal_deadline <= next_week)
        )
    ).order_by(
        db.func.coalesce(Project.hard_deadline, Project.internal_deadline).asc()
    ).all()

    # 4. Dusty projects (active, 7+ days since last update)
    active_projects = Project.query.filter_by(status='active').all()
    dusty_projects = [p for p in active_projects if p.staleness_level in ('warning', 'critical')]
    dusty_projects.sort(key=lambda p: p.days_since_update, reverse=True)

    return render_template('dashboard.html',
        followups_today=followups_today,
        followups_overdue=followups_overdue,
        upcoming_deadlines=upcoming_deadlines,
        dusty_projects=dusty_projects
    )
