from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from app import db
from app.models import FollowUp, Project

bp = Blueprint('followups', __name__)


@bp.route('/')
def list():
    """List all pending follow-ups."""
    followups = FollowUp.query.filter_by(completed=False).order_by(FollowUp.due_date).all()
    return render_template('followups/list.html', followups=followups)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new follow-up."""
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        target_type = request.form.get('target_type', '').strip()
        target_name = request.form.get('target_name', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        notes = request.form.get('notes', '').strip()

        # Validate project exists and is active
        project = Project.query.filter_by(id=project_id, status='active').first()
        if not project:
            abort(404)

        # Validate required fields
        if not target_name or not due_date_str:
            flash('Target name and due date are required.', 'error')
            projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
            return render_template('followups/form.html',
                                   followup=None,
                                   projects=projects,
                                   selected_project_id=int(project_id) if project_id else None)

        # Parse due date
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        # Create follow-up
        followup = FollowUp(
            project_id=project.id,
            target_type=target_type or 'other',
            target_name=target_name,
            due_date=due_date,
            notes=notes or None
        )
        db.session.add(followup)
        db.session.commit()

        flash('Follow-up created successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    # GET request - show form
    projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
    selected_project_id = request.args.get('project_id', type=int)
    return render_template('followups/form.html',
                           followup=None,
                           projects=projects,
                           selected_project_id=selected_project_id)


@bp.route('/<int:id>/complete', methods=['POST'])
def complete(id):
    """Mark a follow-up as complete."""
    followup = FollowUp.query.get_or_404(id)
    # TODO: Handle completion
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/<int:id>/snooze', methods=['POST'])
def snooze(id):
    """Snooze a follow-up (push due date)."""
    followup = FollowUp.query.get_or_404(id)
    # TODO: Handle snooze
    return redirect(request.referrer or url_for('dashboard.index'))
