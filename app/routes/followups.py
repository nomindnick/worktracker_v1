from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models import FollowUp

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
        # TODO: Handle form submission
        pass
    return render_template('followups/form.html', followup=None)


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
