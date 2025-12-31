from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from app import db
from app.models import Project, StatusUpdate

bp = Blueprint('updates', __name__)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new status update."""
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        notes = request.form.get('notes', '').strip()

        # Validate project exists and is active
        project = Project.query.filter_by(id=project_id, status='active').first()
        if not project:
            abort(404)

        # Validate notes provided
        if not notes:
            flash('Status update notes are required.', 'error')
            projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
            return render_template('updates/form.html', projects=projects, selected_project_id=project.id)

        # Create status update
        status_update = StatusUpdate(
            project_id=project.id,
            notes=notes
        )
        db.session.add(status_update)
        db.session.commit()

        flash('Status update added successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    # GET request - show form
    projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
    selected_project_id = request.args.get('project_id', type=int)
    return render_template('updates/form.html', projects=projects, selected_project_id=selected_project_id)
