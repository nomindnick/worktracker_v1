from flask import Blueprint, Response
from datetime import date
import csv
from io import StringIO
from app.models import Project, StatusUpdate, FollowUp

bp = Blueprint('export', __name__)


@bp.route('/')
def export_csv():
    """Export active projects to CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'Client', 'Project', 'Matter #', 'Hard Deadline',
        'Internal Deadline', 'Attorneys', 'Priority',
        'Current Status', 'Next Follow-up'
    ])

    # Data rows
    for project in Project.query.filter_by(status='active').all():
        latest_update = StatusUpdate.query.filter_by(project_id=project.id)\
            .order_by(StatusUpdate.created_at.desc()).first()
        next_followup = FollowUp.query.filter_by(project_id=project.id, completed=False)\
            .order_by(FollowUp.due_date.asc()).first()

        writer.writerow([
            project.client_name,
            project.project_name,
            project.matter_number or '',
            project.hard_deadline.isoformat() if project.hard_deadline else '',
            project.internal_deadline.isoformat(),
            project.assigned_attorneys,
            project.priority,
            latest_update.notes if latest_update else '',
            next_followup.due_date.isoformat() if next_followup else ''
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=worklist_{date.today()}.csv'}
    )
