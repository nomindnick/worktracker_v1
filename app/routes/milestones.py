from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime
from app import db
from app.models import Milestone, Project

bp = Blueprint('milestones', __name__)


@bp.route('/')
def list():
    """List all pending milestones."""
    milestones = Milestone.query.filter_by(completed=False).order_by(Milestone.date).all()
    return render_template('milestones/list.html', milestones=milestones)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new milestone."""
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()

        # Validate project exists and is active
        project = Project.query.filter_by(id=project_id, status='active').first()
        if not project:
            abort(404)

        # Validate required fields
        errors = []
        if not name:
            errors.append('Milestone name is required.')
        if not date_str:
            errors.append('Date is required.')

        # Parse date
        milestone_date = None
        if date_str:
            try:
                milestone_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Date must be a valid date (YYYY-MM-DD).')

        # If validation errors, flash them and re-render form
        if errors:
            for error in errors:
                flash(error, 'error')
            projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
            return render_template('milestones/form.html',
                                   milestone=None,
                                   projects=projects,
                                   selected_project_id=project.id)

        # Create milestone
        milestone = Milestone(
            project_id=project.id,
            name=name,
            description=description or None,
            date=milestone_date
        )
        db.session.add(milestone)
        db.session.commit()

        flash('Milestone created successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    # GET request - show form
    projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
    selected_project_id = request.args.get('project_id', type=int)
    return render_template('milestones/form.html',
                           milestone=None,
                           projects=projects,
                           selected_project_id=selected_project_id)


@bp.route('/<int:id>/complete', methods=['POST'])
def complete(id):
    """Mark a milestone as complete."""
    milestone = Milestone.query.get_or_404(id)
    milestone.completed = True
    db.session.commit()
    flash('Milestone marked as complete.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/<int:id>/uncomplete', methods=['POST'])
def uncomplete(id):
    """Mark a milestone as incomplete."""
    milestone = Milestone.query.get_or_404(id)
    milestone.completed = False
    db.session.commit()
    flash('Milestone marked as incomplete.', 'success')
    return redirect(request.referrer or url_for('projects.detail', id=milestone.project_id))
