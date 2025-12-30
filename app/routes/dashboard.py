from flask import Blueprint, render_template

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def index():
    """Dashboard / Today view - shows what needs attention."""
    return render_template('dashboard.html')
