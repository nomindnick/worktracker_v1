from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import StatusUpdate

bp = Blueprint('updates', __name__)


@bp.route('/new', methods=['GET', 'POST'])
def new():
    """Create a new status update."""
    if request.method == 'POST':
        # TODO: Handle form submission
        pass
    return render_template('updates/form.html')
