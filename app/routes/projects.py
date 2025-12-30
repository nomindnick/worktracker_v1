from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Project

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
        # TODO: Handle form submission
        pass
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
        # TODO: Handle form submission
        pass
    return render_template('projects/form.html', project=project)


@bp.route('/<int:id>/archive', methods=['POST'])
def archive(id):
    """Archive a project."""
    project = Project.query.get_or_404(id)
    # TODO: Handle archiving
    return redirect(url_for('projects.list'))
