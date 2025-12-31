from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Project, StatusUpdate
from datetime import datetime

bp = Blueprint('projects', __name__)


@bp.route('/')
def list():
    """List all active projects."""
    projects = Project.query.filter_by(status='active').all()
    return render_template('projects/list.html', projects=projects)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new project."""
    if request.method == 'POST':
        # Parse date fields
        hard_deadline = None
        if request.form.get('hard_deadline'):
            hard_deadline = datetime.strptime(request.form['hard_deadline'], '%Y-%m-%d').date()

        internal_deadline = datetime.strptime(request.form['internal_deadline'], '%Y-%m-%d').date()

        # Parse optional estimated_hours
        estimated_hours = None
        if request.form.get('estimated_hours'):
            estimated_hours = float(request.form['estimated_hours'])

        # Create project
        project = Project(
            client_name=request.form['client_name'],
            project_name=request.form['project_name'],
            matter_number=request.form.get('matter_number') or None,
            hard_deadline=hard_deadline,
            internal_deadline=internal_deadline,
            assigner=request.form['assigner'],
            assigned_attorneys=request.form['assigned_attorneys'],
            priority=request.form['priority'],
            estimated_hours=estimated_hours
        )
        db.session.add(project)
        db.session.flush()  # Get the project ID before committing

        # Create initial status update if provided
        if request.form.get('initial_update'):
            status_update = StatusUpdate(
                project_id=project.id,
                notes=request.form['initial_update']
            )
            db.session.add(status_update)

        db.session.commit()
        flash(f'Project "{project.project_name}" created successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    return render_template('projects/form.html', project=None)


@bp.route('/<int:id>')
def detail(id):
    """View project detail."""
    project = Project.query.get_or_404(id)
    return render_template('projects/detail.html', project=project)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit a project."""
    project = Project.query.get_or_404(id)
    if request.method == 'POST':
        # Parse date fields
        hard_deadline = None
        if request.form.get('hard_deadline'):
            hard_deadline = datetime.strptime(request.form['hard_deadline'], '%Y-%m-%d').date()

        internal_deadline = datetime.strptime(request.form['internal_deadline'], '%Y-%m-%d').date()

        # Parse optional float fields
        estimated_hours = None
        if request.form.get('estimated_hours'):
            try:
                estimated_hours = float(request.form['estimated_hours'])
            except ValueError:
                pass

        actual_hours = None
        if request.form.get('actual_hours'):
            try:
                actual_hours = float(request.form['actual_hours'])
            except ValueError:
                pass

        # Update project fields
        project.client_name = request.form['client_name']
        project.project_name = request.form['project_name']
        project.matter_number = request.form.get('matter_number') or None
        project.hard_deadline = hard_deadline
        project.internal_deadline = internal_deadline
        project.assigner = request.form['assigner']
        project.assigned_attorneys = request.form['assigned_attorneys']
        project.priority = request.form['priority']
        project.estimated_hours = estimated_hours
        project.actual_hours = actual_hours
        project.updated_at = datetime.utcnow()

        db.session.commit()
        flash(f'Project "{project.project_name}" updated successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    return render_template('projects/form.html', project=project)


@bp.route('/<int:id>/archive', methods=['POST'])
def archive(id):
    """Archive a project."""
    project = Project.query.get_or_404(id)
    project.status = 'archived'
    project.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Project "{project.project_name}" has been archived.', 'success')
    return redirect(url_for('projects.list'))


@bp.route('/<int:id>/updates/new')
def updates_new(id):
    """Redirect to status update form with project pre-selected."""
    # Verify project exists
    Project.query.get_or_404(id)
    return redirect(url_for('updates.new', project_id=id))


@bp.route('/<int:id>/followups/new')
def followups_new(id):
    """Redirect to follow-up form with project pre-selected."""
    # Verify project exists
    Project.query.get_or_404(id)
    return redirect(url_for('followups.new', project_id=id))
