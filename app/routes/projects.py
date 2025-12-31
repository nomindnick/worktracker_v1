from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Project, StatusUpdate
from datetime import datetime

bp = Blueprint('projects', __name__)


@bp.route('/')
def list():
    """List all active projects with optional filtering and sorting."""
    # Get filter parameters
    priority = request.args.get('priority', '')
    attorney = request.args.get('attorney', '')
    assigner = request.args.get('assigner', '')
    sort_by = request.args.get('sort_by', 'internal_deadline')
    sort_order = request.args.get('sort_order', 'asc')

    # Build query with filters
    query = Project.query.filter_by(status='active')

    if priority:
        query = query.filter(Project.priority == priority)
    if attorney:
        query = query.filter(Project.assigned_attorneys.contains(attorney))
    if assigner:
        query = query.filter(Project.assigner == assigner)

    # Validate sort column - only allow specific columns
    allowed_sort_columns = ['internal_deadline', 'priority', 'staleness']
    if sort_by not in allowed_sort_columns:
        sort_by = 'internal_deadline'

    # Apply sorting
    if sort_by == 'staleness':
        # Staleness is a computed property, sort in Python after fetching
        projects = query.all()
        reverse = (sort_order == 'desc')
        projects.sort(key=lambda p: p.days_since_update, reverse=reverse)
    elif sort_by == 'priority':
        # Custom priority order: high > medium > low
        projects = query.all()
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        reverse = (sort_order == 'desc')
        projects.sort(key=lambda p: priority_order.get(p.priority, 1), reverse=reverse)
    else:
        # Database sorting for deadline
        sort_column = getattr(Project, sort_by, Project.internal_deadline)
        if sort_order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        projects = query.all()

    # Get distinct values for filter dropdowns from all active projects
    all_projects = Project.query.filter_by(status='active').all()
    attorneys = sorted(set(p.assigned_attorneys for p in all_projects if p.assigned_attorneys))
    assigners = sorted(set(p.assigner for p in all_projects if p.assigner))

    return render_template('projects/list.html',
                          projects=projects,
                          attorneys=attorneys,
                          assigners=assigners,
                          current_filters={
                              'priority': priority,
                              'attorney': attorney,
                              'assigner': assigner,
                              'sort_by': sort_by,
                              'sort_order': sort_order
                          })


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


@bp.route('/<int:id>/archive', methods=['GET', 'POST'])
def archive(id):
    """Archive a project."""
    project = Project.query.get_or_404(id)

    if request.method == 'POST':
        # Parse optional actual_hours
        if request.form.get('actual_hours'):
            try:
                project.actual_hours = float(request.form['actual_hours'])
            except ValueError:
                pass

        project.status = 'archived'
        project.updated_at = datetime.utcnow()
        db.session.commit()
        flash(f'Project "{project.project_name}" has been archived.', 'success')
        return redirect(url_for('projects.list'))

    return render_template('projects/archive_form.html', project=project)


@bp.route('/<int:id>/unarchive', methods=['POST'])
def unarchive(id):
    """Unarchive a project (reactivate)."""
    project = Project.query.get_or_404(id)
    project.status = 'active'
    project.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Project "{project.project_name}" has been reactivated.', 'success')
    return redirect(url_for('projects.detail', id=project.id))


@bp.route('/archived')
def archived():
    """List all archived projects."""
    projects = Project.query.filter_by(status='archived').all()
    return render_template('archived.html', projects=projects)


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
