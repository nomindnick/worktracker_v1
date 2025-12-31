"""Tests for app/routes/export.py - CSV export route."""
from datetime import date, timedelta
import csv
from io import StringIO


class TestExportCSV:
    """Test GET /export/ route."""

    def test_export_returns_200(self, client, db_session):
        """Export returns 200 OK."""
        response = client.get('/export/')
        assert response.status_code == 200

    def test_export_content_type_is_csv(self, client, db_session):
        """Export returns CSV content type."""
        response = client.get('/export/')
        assert response.content_type == 'text/csv; charset=utf-8'

    def test_export_has_content_disposition(self, client, db_session):
        """Export has attachment Content-Disposition header."""
        response = client.get('/export/')

        assert 'Content-Disposition' in response.headers
        assert 'attachment' in response.headers['Content-Disposition']
        assert f'worklist_{date.today()}' in response.headers['Content-Disposition']

    def test_export_csv_has_header_row(self, client, db_session):
        """Export CSV includes header row."""
        response = client.get('/export/')

        reader = csv.reader(StringIO(response.data.decode('utf-8')))
        headers = next(reader)

        assert 'Client' in headers
        assert 'Project' in headers
        assert 'Matter #' in headers
        assert 'Priority' in headers

    def test_export_csv_includes_active_projects(self, client, sample_project, db_session):
        """Export CSV includes active projects."""
        response = client.get('/export/')

        csv_content = response.data.decode('utf-8')
        assert 'Acme Corp' in csv_content
        assert 'Patent Application' in csv_content

    def test_export_csv_excludes_archived_projects(self, client, sample_project, db_session):
        """Export CSV excludes archived projects."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get('/export/')

        csv_content = response.data.decode('utf-8')
        assert 'Acme Corp' not in csv_content

    def test_export_csv_includes_latest_status(self, client, sample_project_with_updates, db_session):
        """Export CSV includes latest status update."""
        response = client.get('/export/')

        csv_content = response.data.decode('utf-8')
        assert 'Draft in progress' in csv_content

    def test_export_csv_includes_next_followup(self, client, sample_followup, db_session):
        """Export CSV includes next follow-up date."""
        response = client.get('/export/')

        csv_content = response.data.decode('utf-8')
        expected_date = (date.today() + timedelta(days=3)).isoformat()
        assert expected_date in csv_content

    def test_export_csv_handles_null_hard_deadline(self, client, db_session):
        """Export CSV handles projects without hard deadline."""
        from app.models import Project

        project = Project(
            client_name='No Deadline Corp',
            project_name='No Deadline Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/export/')

        assert response.status_code == 200
        csv_content = response.data.decode('utf-8')
        assert 'No Deadline Corp' in csv_content

    def test_export_csv_handles_null_matter_number(self, client, db_session):
        """Export CSV handles projects without matter number."""
        from app.models import Project

        project = Project(
            client_name='No Matter Corp',
            project_name='No Matter Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/export/')

        assert response.status_code == 200

    def test_export_csv_handles_project_without_updates(self, client, sample_project, db_session):
        """Export CSV handles projects with no status updates."""
        response = client.get('/export/')

        assert response.status_code == 200

    def test_export_csv_handles_project_without_followups(self, client, sample_project, db_session):
        """Export CSV handles projects with no follow-ups."""
        response = client.get('/export/')

        assert response.status_code == 200
