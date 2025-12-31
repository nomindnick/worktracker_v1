"""Tests for app/routes/updates.py - Status update routes."""

from app.models import Project, StatusUpdate


class TestStatusUpdateNew:
    """Test GET/POST /updates/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New status update form returns 200 OK."""
        response = client.get('/updates/new')
        assert response.status_code == 200

    def test_new_get_shows_projects_in_dropdown(self, client, db_session, sample_project):
        """GET shows active projects in dropdown."""
        response = client.get('/updates/new')
        assert response.status_code == 200
        assert sample_project.client_name.encode() in response.data
        assert sample_project.project_name.encode() in response.data

    def test_new_get_with_project_id_preselects(self, client, db_session, sample_project):
        """GET with project_id query param pre-selects project."""
        response = client.get(f'/updates/new?project_id={sample_project.id}')
        assert response.status_code == 200
        # Check that the option is selected
        assert f'value="{sample_project.id}" selected'.encode() in response.data

    def test_new_get_excludes_archived_projects(self, client, db_session, sample_project):
        """GET excludes archived projects from dropdown."""
        # Archive the sample project
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get('/updates/new')
        assert response.status_code == 200
        assert sample_project.client_name.encode() not in response.data

    def test_new_post_creates_status_update(self, client, db_session, sample_project):
        """POST with valid data creates status update."""
        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': 'Made progress on the research phase.'
        })

        # Should redirect to project detail
        assert response.status_code == 302

        # Verify status update was created
        update = StatusUpdate.query.filter_by(project_id=sample_project.id).first()
        assert update is not None
        assert update.notes == 'Made progress on the research phase.'

    def test_new_post_redirects_to_project(self, client, db_session, sample_project):
        """POST redirects to project detail page."""
        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': 'Status update notes.'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert f'/projects/{sample_project.id}' in response.location

    def test_new_post_shows_success_flash(self, client, db_session, sample_project):
        """POST shows success flash message."""
        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': 'Status update notes.'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Status update added successfully.' in response.data

    def test_new_post_invalid_project_id_returns_404(self, client, db_session):
        """POST with non-existent project_id returns 404."""
        response = client.post('/updates/new', data={
            'project_id': 99999,
            'notes': 'Some notes.'
        })
        assert response.status_code == 404

    def test_new_post_archived_project_returns_404(self, client, db_session, sample_project):
        """POST with archived project returns 404."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': 'Some notes.'
        })
        assert response.status_code == 404

    def test_new_post_missing_notes_shows_error(self, client, db_session, sample_project):
        """POST with empty notes shows error and re-renders form."""
        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': ''
        })

        assert response.status_code == 200
        assert b'Status update notes are required.' in response.data
        # Should preserve selected project
        assert f'value="{sample_project.id}" selected'.encode() in response.data

    def test_new_post_whitespace_only_notes_shows_error(self, client, db_session, sample_project):
        """POST with whitespace-only notes shows error."""
        response = client.post('/updates/new', data={
            'project_id': sample_project.id,
            'notes': '   \n\t  '
        })

        assert response.status_code == 200
        assert b'Status update notes are required.' in response.data


class TestProjectUpdatesNew:
    """Test GET /projects/<id>/updates/new route."""

    def test_project_updates_new_redirects(self, client, db_session, sample_project):
        """GET /projects/<id>/updates/new redirects to /updates/new with project_id."""
        response = client.get(f'/projects/{sample_project.id}/updates/new', follow_redirects=False)

        assert response.status_code == 302
        assert '/updates/new' in response.location
        assert f'project_id={sample_project.id}' in response.location

    def test_project_updates_new_invalid_id_returns_404(self, client, db_session):
        """GET /projects/<id>/updates/new with invalid id returns 404."""
        response = client.get('/projects/99999/updates/new')
        assert response.status_code == 404

    def test_project_updates_new_full_flow(self, client, db_session, sample_project):
        """GET /projects/<id>/updates/new redirects to form with project pre-selected."""
        response = client.get(f'/projects/{sample_project.id}/updates/new', follow_redirects=True)

        assert response.status_code == 200
        assert f'value="{sample_project.id}" selected'.encode() in response.data
