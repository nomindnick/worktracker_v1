"""Tests for app/routes/followups.py - Follow-up routes."""

from datetime import date, timedelta
from app.models import FollowUp


class TestFollowUpList:
    """Test GET /followups/ route."""

    def test_list_returns_200(self, client, db_session):
        """Follow-up list returns 200 OK."""
        response = client.get('/followups/')
        assert response.status_code == 200

    def test_list_shows_pending_followups(self, client, sample_followup, db_session):
        """Follow-up list shows pending (incomplete) follow-ups."""
        response = client.get('/followups/')

        assert b'John Doe' in response.data

    def test_list_excludes_completed_followups(self, client, sample_followup, db_session):
        """Follow-up list excludes completed follow-ups."""
        sample_followup.completed = True
        db_session.commit()

        response = client.get('/followups/')

        assert b'John Doe' not in response.data


class TestFollowUpNew:
    """Test GET/POST /followups/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New follow-up form returns 200 OK."""
        response = client.get('/followups/new')
        assert response.status_code == 200

    def test_new_get_shows_project_dropdown(self, client, sample_project, db_session):
        """New follow-up form shows projects in dropdown."""
        response = client.get('/followups/new')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_new_get_preselects_project(self, client, sample_project, db_session):
        """New follow-up form pre-selects project from query param."""
        response = client.get(f'/followups/new?project_id={sample_project.id}')

        assert b'selected' in response.data

    def test_new_post_creates_followup(self, client, sample_project, db_session):
        """POST creates a new follow-up in database."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Jane Smith',
            'due_date': due_date,
            'notes': 'Follow up on contract'
        }, follow_redirects=False)

        assert response.status_code == 302

        # Verify follow-up was created
        followup = FollowUp.query.filter_by(target_name='Jane Smith').first()
        assert followup is not None
        assert followup.project_id == sample_project.id
        assert followup.target_type == 'client'
        assert followup.notes == 'Follow up on contract'

    def test_new_post_redirects_to_project(self, client, sample_project, db_session):
        """POST redirects to project detail page."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'associate',
            'target_name': 'Test Person',
            'due_date': due_date
        }, follow_redirects=False)

        assert f'/projects/{sample_project.id}' in response.location

    def test_new_post_flashes_success(self, client, sample_project, db_session):
        """POST flashes success message."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date
        }, follow_redirects=True)

        assert b'Follow-up created successfully' in response.data

    def test_new_post_validates_required_fields(self, client, sample_project, db_session):
        """POST validates required fields (target_name, due_date)."""
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': '',
            'due_date': ''
        })

        assert response.status_code == 200
        assert b'Target name is required' in response.data
        assert b'Due date is required' in response.data

    def test_new_post_validates_due_date_format(self, client, sample_project, db_session):
        """POST with invalid due_date format shows validation error."""
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': 'not-a-date'
        })

        assert response.status_code == 200
        assert b'Due date must be a valid date' in response.data

    def test_new_post_validates_target_type(self, client, sample_project, db_session):
        """POST with invalid target_type shows validation error."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'invalid_type',
            'target_name': 'Test Person',
            'due_date': due_date
        })

        assert response.status_code == 200
        assert b'Invalid target type' in response.data

    def test_new_post_404_for_invalid_project(self, client, db_session):
        """POST returns 404 for non-existent project."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': 99999,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date
        })

        assert response.status_code == 404

    def test_new_post_404_for_archived_project(self, client, sample_project, db_session):
        """POST returns 404 for archived project."""
        sample_project.status = 'archived'
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date
        })

        assert response.status_code == 404

    def test_new_post_defaults_target_type_to_other(self, client, sample_project, db_session):
        """POST defaults target_type to 'other' if empty."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': '',
            'target_name': 'Test Person',
            'due_date': due_date
        }, follow_redirects=False)

        assert response.status_code == 302
        followup = FollowUp.query.filter_by(target_name='Test Person').first()
        assert followup.target_type == 'other'

    def test_new_post_handles_optional_notes(self, client, sample_project, db_session):
        """POST handles missing notes field gracefully."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/followups/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date
        }, follow_redirects=False)

        assert response.status_code == 302
        followup = FollowUp.query.filter_by(target_name='Test Person').first()
        assert followup.notes is None


class TestFollowUpComplete:
    """Test POST /followups/<id>/complete route."""

    def test_complete_returns_redirect(self, client, sample_followup, db_session):
        """Complete redirects."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_complete_404_for_missing_followup(self, client, db_session):
        """Complete returns 404 for non-existent follow-up."""
        response = client.post('/followups/99999/complete')
        assert response.status_code == 404

    def test_complete_redirects_to_referrer(self, client, sample_followup, db_session):
        """Complete redirects to referrer if available."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'

    def test_complete_redirects_to_dashboard_without_referrer(self, client, sample_followup, db_session):
        """Complete redirects to dashboard when no referrer."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=False)
        assert '/' in response.location

    def test_complete_marks_followup_as_completed(self, client, sample_followup, db_session):
        """Complete sets completed=True on the follow-up."""
        assert sample_followup.completed is False

        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=False)

        db_session.refresh(sample_followup)
        assert sample_followup.completed is True
        assert sample_followup.completed_at is not None

    def test_complete_flashes_success_message(self, client, sample_followup, db_session):
        """Complete shows success flash message."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=True)
        assert b'Follow-up marked as complete' in response.data

    def test_complete_removes_from_pending_list(self, client, sample_followup, db_session):
        """Completed follow-up no longer appears in pending list."""
        # Verify it's in the list initially
        response = client.get('/followups/')
        assert b'John Doe' in response.data

        # Complete it
        client.post(f'/followups/{sample_followup.id}/complete')

        # Verify it's no longer in the list
        response = client.get('/followups/')
        assert b'John Doe' not in response.data


class TestFollowUpSnooze:
    """Test POST /followups/<id>/snooze route."""

    def test_snooze_returns_redirect(self, client, sample_followup, db_session):
        """Snooze redirects."""
        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_snooze_404_for_missing_followup(self, client, db_session):
        """Snooze returns 404 for non-existent follow-up."""
        response = client.post('/followups/99999/snooze')
        assert response.status_code == 404

    def test_snooze_updates_due_date(self, client, sample_followup, db_session):
        """Snooze updates the follow-up due date by specified days."""
        original_due_date = sample_followup.due_date

        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               data={'days': 3},
                               follow_redirects=False)

        db_session.refresh(sample_followup)
        assert sample_followup.due_date == original_due_date + timedelta(days=3)

    def test_snooze_defaults_to_one_day(self, client, sample_followup, db_session):
        """Snooze defaults to 1 day if days parameter not provided."""
        original_due_date = sample_followup.due_date

        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               follow_redirects=False)

        db_session.refresh(sample_followup)
        assert sample_followup.due_date == original_due_date + timedelta(days=1)

    def test_snooze_flashes_success_message(self, client, sample_followup, db_session):
        """Snooze shows success flash message."""
        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               data={'days': 7},
                               follow_redirects=True)
        assert b'Follow-up snoozed by 7 day(s)' in response.data

    def test_snooze_redirects_to_referrer(self, client, sample_followup, db_session):
        """Snooze redirects to referrer if available."""
        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               data={'days': 1},
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'


class TestProjectFollowupsNew:
    """Test GET /projects/<id>/followups/new route."""

    def test_project_followups_new_redirects(self, client, sample_project, db_session):
        """GET /projects/<id>/followups/new redirects to /followups/new with project_id."""
        response = client.get(f'/projects/{sample_project.id}/followups/new',
                              follow_redirects=False)

        assert response.status_code == 302
        assert '/followups/new' in response.location
        assert f'project_id={sample_project.id}' in response.location

    def test_project_followups_new_invalid_id_returns_404(self, client, db_session):
        """GET /projects/<id>/followups/new with invalid id returns 404."""
        response = client.get('/projects/99999/followups/new')
        assert response.status_code == 404

    def test_project_followups_new_full_flow(self, client, sample_project, db_session):
        """GET /projects/<id>/followups/new redirects to form with project pre-selected."""
        response = client.get(f'/projects/{sample_project.id}/followups/new',
                              follow_redirects=True)

        assert response.status_code == 200
        assert b'selected' in response.data


class TestFollowUpListUI:
    """Test follow-up list UI elements for Sprint 6.3."""

    def test_list_has_table_wrapper(self, client, sample_followup, db_session):
        """Follow-up list table is wrapped in table-wrapper div."""
        response = client.get('/followups/')
        data = response.data.decode('utf-8')
        assert 'class="table-wrapper"' in data

    def test_list_complete_button_has_data_confirm(self, client, sample_followup, db_session):
        """Complete button in follow-up list has data-confirm attribute."""
        response = client.get('/followups/')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this follow-up as complete?"' in data
