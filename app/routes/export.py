from flask import Blueprint, Response
from datetime import date
import csv
from io import StringIO
from app.models import Project, StatusUpdate, Task

bp = Blueprint('export', __name__)


@bp.route('/')
def export_csv():
    """Export active projects to CSV."""
    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'Client', 'Project', 'Client #', 'Matter #',
        'Attorneys', 'Priority',
        'Current Status', 'Next Task', 'Next Milestone'
    ])

    # Data rows
    for project in Project.query.filter_by(status='active').all():
        latest_update = StatusUpdate.query.filter_by(project_id=project.id)\
            .order_by(StatusUpdate.created_at.desc()).first()
        next_task = Task.query.filter_by(project_id=project.id, completed=False)\
            .order_by(Task.due_date.asc()).first()
        next_milestone = project.next_milestone

        writer.writerow([
            project.client_name,
            project.project_name,
            project.client_number or '',
            project.matter_number or '',
            project.assigned_attorneys,
            project.priority,
            latest_update.notes if latest_update else '',
            next_task.due_date.isoformat() if next_task else '',
            f"{next_milestone.name} ({next_milestone.date.isoformat()})" if next_milestone else ''
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=worklist_{date.today()}.csv'}
    )
