from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from datetime import datetime, timedelta
from app import db
from app.models import Task, Project

bp = Blueprint('tasks', __name__)


@bp.route('/')
def list():
    """List all pending tasks."""
    tasks = Task.query.filter_by(completed=False).order_by(Task.due_date, Task.priority).all()
    return render_template('tasks/list.html', tasks=tasks)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new task."""
    if request.method == 'POST':
        project_id = request.form.get('project_id')
        target_type = request.form.get('target_type', '').strip()
        target_name = request.form.get('target_name', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', '').strip()

        # Validate project exists and is active
        project = Project.query.filter_by(id=project_id, status='active').first()
        if not project:
            abort(404)

        # Validate required fields
        errors = []
        if not target_name:
            errors.append('Target name is required.')
        if not due_date_str:
            errors.append('Due date is required.')
        if target_type and target_type not in ('self', 'associate', 'client', 'opposing_counsel', 'assigning_attorney'):
            errors.append('Invalid target type.')
        if priority and priority not in ('high', 'medium', 'low'):
            errors.append('Invalid priority.')

        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Due date must be a valid date (YYYY-MM-DD).')

        # If validation errors, flash them and re-render form
        if errors:
            for error in errors:
                flash(error, 'error')
            projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
            return render_template('tasks/form.html',
                                   task=None,
                                   projects=projects,
                                   selected_project_id=project.id)

        # Create task
        task = Task(
            project_id=project.id,
            target_type=target_type or 'self',
            target_name=target_name,
            due_date=due_date,
            description=description or None,
            priority=priority or 'medium'
        )
        db.session.add(task)
        db.session.commit()

        flash('Task created successfully.', 'success')
        return redirect(url_for('projects.detail', id=project.id))

    # GET request - show form
    projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
    selected_project_id = request.args.get('project_id', type=int)
    return render_template('tasks/form.html',
                           task=None,
                           projects=projects,
                           selected_project_id=selected_project_id)


@bp.route('/<int:id>/complete', methods=['POST'])
def complete(id):
    """Mark a task as complete."""
    task = Task.query.get_or_404(id)
    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    flash('Task marked as complete.', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/<int:id>/snooze', methods=['POST'])
def snooze(id):
    """Snooze a task (push due date)."""
    task = Task.query.get_or_404(id)
    days = request.form.get('days', type=int, default=1)
    days = max(1, min(days, 365))  # Ensure days is between 1 and 365
    task.due_date = task.due_date + timedelta(days=days)
    db.session.commit()
    flash(f'Task snoozed by {days} day(s).', 'success')
    return redirect(request.referrer or url_for('dashboard.index'))


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing task."""
    task = Task.query.get_or_404(id)

    if request.method == 'POST':
        project_id = request.form.get('project_id')
        target_type = request.form.get('target_type', '').strip()
        target_name = request.form.get('target_name', '').strip()
        due_date_str = request.form.get('due_date', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', '').strip()

        # Validate project exists and is active
        project = Project.query.filter_by(id=project_id, status='active').first()
        if not project:
            abort(404)

        # Validate required fields
        errors = []
        if not target_name:
            errors.append('Target name is required.')
        if not due_date_str:
            errors.append('Due date is required.')
        if target_type and target_type not in ('self', 'associate', 'client', 'opposing_counsel', 'assigning_attorney'):
            errors.append('Invalid target type.')
        if priority and priority not in ('high', 'medium', 'low'):
            errors.append('Invalid priority.')

        # Parse due date
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append('Due date must be a valid date (YYYY-MM-DD).')

        # If validation errors, flash them and re-render form
        if errors:
            for error in errors:
                flash(error, 'error')
            projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
            return render_template('tasks/form.html',
                                   task=task,
                                   projects=projects,
                                   selected_project_id=int(project_id) if project_id else task.project_id)

        # Update task
        task.project_id = project.id
        task.target_type = target_type or 'self'
        task.target_name = target_name
        task.due_date = due_date
        task.description = description or None
        task.priority = priority or 'medium'
        db.session.commit()

        flash('Task updated successfully.', 'success')
        return redirect(url_for('projects.detail', id=task.project_id))

    # GET request - show form with current values
    projects = Project.query.filter_by(status='active').order_by(Project.client_name).all()
    return render_template('tasks/form.html',
                           task=task,
                           projects=projects,
                           selected_project_id=task.project_id)
