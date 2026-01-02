"""Tests for app/routes/milestones.py - Milestone routes."""

from datetime import date, timedelta
from app.models import Milestone


class TestMilestoneList:
    """Test GET /milestones/ route."""

    def test_list_returns_200(self, client, db_session):
        """Milestone list returns 200 OK."""
        response = client.get('/milestones/')
        assert response.status_code == 200

    def test_list_shows_pending_milestones(self, client, sample_milestone, db_session):
        """Milestone list shows pending (incomplete) milestones."""
        response = client.get('/milestones/')

        assert b'Initial Filing' in response.data

    def test_list_excludes_completed_milestones(self, client, sample_milestone, db_session):
        """Milestone list excludes completed milestones."""
        sample_milestone.completed = True
        db_session.commit()

        response = client.get('/milestones/')

        assert b'Initial Filing' not in response.data

    def test_list_shows_milestone_date(self, client, sample_milestone, db_session):
        """Milestone list shows milestone date."""
        response = client.get('/milestones/')

        expected_date = (date.today() + timedelta(days=14)).isoformat()
        assert expected_date.encode() in response.data

    def test_list_shows_project_info(self, client, sample_milestone, db_session):
        """Milestone list shows associated project information."""
        response = client.get('/milestones/')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data


class TestMilestoneNew:
    """Test GET/POST /milestones/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New milestone form returns 200 OK."""
        response = client.get('/milestones/new')
        assert response.status_code == 200

    def test_new_get_shows_project_dropdown(self, client, sample_project, db_session):
        """New milestone form shows projects in dropdown."""
        response = client.get('/milestones/new')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_new_get_preselects_project(self, client, sample_project, db_session):
        """New milestone form pre-selects project from query param."""
        response = client.get(f'/milestones/new?project_id={sample_project.id}')

        assert b'selected' in response.data

    def test_new_post_creates_milestone(self, client, sample_project, db_session):
        """POST creates a new milestone in database."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Final Submission',
            'description': 'Submit final patent documents',
            'date': milestone_date
        }, follow_redirects=False)

        assert response.status_code == 302

        # Verify milestone was created
        milestone = Milestone.query.filter_by(name='Final Submission').first()
        assert milestone is not None
        assert milestone.project_id == sample_project.id
        assert milestone.description == 'Submit final patent documents'

    def test_new_post_redirects_to_project(self, client, sample_project, db_session):
        """POST redirects to project detail page."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': milestone_date
        }, follow_redirects=False)

        assert f'/projects/{sample_project.id}' in response.location

    def test_new_post_flashes_success(self, client, sample_project, db_session):
        """POST flashes success message."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': milestone_date
        }, follow_redirects=True)

        assert b'Milestone created successfully' in response.data

    def test_new_post_validates_required_name(self, client, sample_project, db_session):
        """POST validates required name field."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': '',
            'date': milestone_date
        })

        assert response.status_code == 200
        assert b'Milestone name is required' in response.data

    def test_new_post_validates_required_date(self, client, sample_project, db_session):
        """POST validates required date field."""
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': ''
        })

        assert response.status_code == 200
        assert b'Date is required' in response.data

    def test_new_post_validates_date_format(self, client, sample_project, db_session):
        """POST with invalid date format shows validation error."""
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': 'not-a-date'
        })

        assert response.status_code == 200
        assert b'Date must be a valid date' in response.data

    def test_new_post_404_for_invalid_project(self, client, db_session):
        """POST returns 404 for non-existent project."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': 99999,
            'name': 'Test Milestone',
            'date': milestone_date
        })

        assert response.status_code == 404

    def test_new_post_404_for_archived_project(self, client, sample_project, db_session):
        """POST returns 404 for archived project."""
        sample_project.status = 'archived'
        db_session.commit()

        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': milestone_date
        })

        assert response.status_code == 404

    def test_new_post_handles_optional_description(self, client, sample_project, db_session):
        """POST handles missing description field gracefully."""
        milestone_date = (date.today() + timedelta(days=30)).isoformat()
        response = client.post('/milestones/new', data={
            'project_id': sample_project.id,
            'name': 'Test Milestone',
            'date': milestone_date
        }, follow_redirects=False)

        assert response.status_code == 302
        milestone = Milestone.query.filter_by(name='Test Milestone').first()
        assert milestone.description is None


class TestMilestoneComplete:
    """Test POST /milestones/<id>/complete route."""

    def test_complete_returns_redirect(self, client, sample_milestone, db_session):
        """Complete redirects."""
        response = client.post(f'/milestones/{sample_milestone.id}/complete',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_complete_404_for_missing_milestone(self, client, db_session):
        """Complete returns 404 for non-existent milestone."""
        response = client.post('/milestones/99999/complete')
        assert response.status_code == 404

    def test_complete_redirects_to_referrer(self, client, sample_milestone, db_session):
        """Complete redirects to referrer if available."""
        response = client.post(f'/milestones/{sample_milestone.id}/complete',
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'

    def test_complete_redirects_to_dashboard_without_referrer(self, client, sample_milestone, db_session):
        """Complete redirects to dashboard when no referrer."""
        response = client.post(f'/milestones/{sample_milestone.id}/complete',
                               follow_redirects=False)
        assert '/' in response.location

    def test_complete_marks_milestone_as_completed(self, client, sample_milestone, db_session):
        """Complete sets completed=True on the milestone."""
        assert sample_milestone.completed is False

        response = client.post(f'/milestones/{sample_milestone.id}/complete',
                               follow_redirects=False)

        db_session.refresh(sample_milestone)
        assert sample_milestone.completed is True

    def test_complete_flashes_success_message(self, client, sample_milestone, db_session):
        """Complete shows success flash message."""
        response = client.post(f'/milestones/{sample_milestone.id}/complete',
                               follow_redirects=True)
        assert b'Milestone marked as complete' in response.data

    def test_complete_removes_from_pending_list(self, client, sample_milestone, db_session):
        """Completed milestone no longer appears in pending list."""
        # Verify it's in the list initially
        response = client.get('/milestones/')
        assert b'Initial Filing' in response.data

        # Complete it
        client.post(f'/milestones/{sample_milestone.id}/complete')

        # Verify it's no longer in the list
        response = client.get('/milestones/')
        assert b'Initial Filing' not in response.data


class TestMilestoneUncomplete:
    """Test POST /milestones/<id>/uncomplete route."""

    def test_uncomplete_returns_redirect(self, client, sample_milestone, db_session):
        """Uncomplete redirects."""
        sample_milestone.completed = True
        db_session.commit()

        response = client.post(f'/milestones/{sample_milestone.id}/uncomplete',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_uncomplete_404_for_missing_milestone(self, client, db_session):
        """Uncomplete returns 404 for non-existent milestone."""
        response = client.post('/milestones/99999/uncomplete')
        assert response.status_code == 404

    def test_uncomplete_marks_milestone_as_incomplete(self, client, sample_milestone, db_session):
        """Uncomplete sets completed=False on the milestone."""
        sample_milestone.completed = True
        db_session.commit()

        response = client.post(f'/milestones/{sample_milestone.id}/uncomplete',
                               follow_redirects=False)

        db_session.refresh(sample_milestone)
        assert sample_milestone.completed is False

    def test_uncomplete_flashes_success_message(self, client, sample_milestone, db_session):
        """Uncomplete shows success flash message."""
        sample_milestone.completed = True
        db_session.commit()

        response = client.post(f'/milestones/{sample_milestone.id}/uncomplete',
                               follow_redirects=True)
        assert b'Milestone marked as incomplete' in response.data

    def test_uncomplete_redirects_to_project_detail(self, client, sample_milestone, db_session):
        """Uncomplete redirects to project detail page."""
        sample_milestone.completed = True
        db_session.commit()

        response = client.post(f'/milestones/{sample_milestone.id}/uncomplete',
                               follow_redirects=False)
        assert f'/projects/{sample_milestone.project_id}' in response.location


class TestMilestoneListUI:
    """Test milestone list UI elements."""

    def test_list_has_table_wrapper(self, client, sample_milestone, db_session):
        """Milestone list table is wrapped in table-wrapper div."""
        response = client.get('/milestones/')
        data = response.data.decode('utf-8')
        assert 'class="table-wrapper"' in data

    def test_list_complete_button_has_data_confirm(self, client, sample_milestone, db_session):
        """Complete button in milestone list has data-confirm attribute."""
        response = client.get('/milestones/')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this milestone as complete?"' in data
