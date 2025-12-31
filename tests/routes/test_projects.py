"""Tests for app/routes/projects.py - Project CRUD routes."""
from datetime import date, timedelta


class TestProjectList:
    """Test GET /projects/ route."""

    def test_list_returns_200(self, client, db_session):
        """Project list page returns 200 OK."""
        response = client.get('/projects/')
        assert response.status_code == 200

    def test_list_shows_active_projects(self, client, sample_project, db_session):
        """Project list shows active projects."""
        response = client.get('/projects/')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_list_excludes_archived_projects(self, client, sample_project, db_session):
        """Project list excludes archived projects."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get('/projects/')

        assert b'Acme Corp' not in response.data

    def test_list_shows_staleness_column(self, client, sample_project, db_session):
        """Project list shows Days Stale column with staleness indicator."""
        response = client.get('/projects/')

        assert b'Days Stale' in response.data
        assert b'staleness-ok' in response.data

    def test_list_shows_add_update_button(self, client, sample_project, db_session):
        """Project list shows Add Update button for each project."""
        response = client.get('/projects/')

        assert b'Add Update' in response.data

    def test_list_shows_followup_columns(self, client, sample_project, db_session):
        """Project list shows Follow-ups and Next Follow-up columns."""
        response = client.get('/projects/')

        assert b'>Follow-ups<' in response.data
        assert b'Next Follow-up' in response.data

    def test_list_shows_followup_count(self, client, sample_project, db_session):
        """Project list shows count of pending follow-ups."""
        from app.models import FollowUp

        # Create pending follow-ups
        followup1 = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today()
        )
        followup2 = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1)
        )
        db_session.add_all([followup1, followup2])
        db_session.commit()

        response = client.get('/projects/')

        # Should show count of 2
        assert b'>2<' in response.data

    def test_list_shows_hard_deadline_column(self, client, sample_project, db_session):
        """Project list shows Hard Deadline column."""
        response = client.get('/projects/')

        assert b'Hard Deadline' in response.data

    def test_list_shows_attorneys_column(self, client, sample_project, db_session):
        """Project list shows Attorneys column."""
        response = client.get('/projects/')

        assert b'Attorneys' in response.data
        assert b'Associate Jones' in response.data

    def test_list_shows_add_followup_button(self, client, sample_project, db_session):
        """Project list shows Add Follow-up button for each project."""
        response = client.get('/projects/')

        assert b'Add Follow-up' in response.data

    def test_list_shows_next_followup_date(self, client, sample_project, db_session):
        """Project list shows next follow-up due date."""
        from app.models import FollowUp

        next_date = date.today() + timedelta(days=3)
        followup = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=next_date
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/projects/')

        assert next_date.isoformat().encode() in response.data


class TestProjectNew:
    """Test GET/POST /projects/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New project form returns 200 OK."""
        response = client.get('/projects/new')
        assert response.status_code == 200

    def test_new_post_creates_project(self, client, db_session):
        """POST to new creates a project."""
        from app.models import Project

        response = client.post('/projects/new', data={
            'client_name': 'New Client',
            'project_name': 'New Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Partner',
            'assigned_attorneys': 'Associate',
            'priority': 'high'
        }, follow_redirects=True)

        assert response.status_code == 200
        project = Project.query.filter_by(client_name='New Client').first()
        assert project is not None

    def test_new_post_with_hard_deadline(self, client, db_session):
        """POST with hard_deadline parses date correctly."""
        from app.models import Project

        hard_deadline = (date.today() + timedelta(days=30)).isoformat()

        client.post('/projects/new', data={
            'client_name': 'Deadline Client',
            'project_name': 'Deadline Project',
            'hard_deadline': hard_deadline,
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        project = Project.query.filter_by(client_name='Deadline Client').first()
        assert project.hard_deadline == date.today() + timedelta(days=30)

    def test_new_post_without_hard_deadline(self, client, db_session):
        """POST without hard_deadline leaves it as None."""
        from app.models import Project

        client.post('/projects/new', data={
            'client_name': 'No Deadline',
            'project_name': 'No Hard Deadline',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'low'
        })

        project = Project.query.filter_by(client_name='No Deadline').first()
        assert project.hard_deadline is None

    def test_new_post_with_estimated_hours(self, client, db_session):
        """POST with estimated_hours parses float correctly."""
        from app.models import Project

        client.post('/projects/new', data={
            'client_name': 'Hours Client',
            'project_name': 'Hours Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium',
            'estimated_hours': '25.5'
        })

        project = Project.query.filter_by(client_name='Hours Client').first()
        assert project.estimated_hours == 25.5

    def test_new_post_without_estimated_hours(self, client, db_session):
        """POST without estimated_hours leaves it as None."""
        from app.models import Project

        client.post('/projects/new', data={
            'client_name': 'No Hours',
            'project_name': 'No Hours Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        project = Project.query.filter_by(client_name='No Hours').first()
        assert project.estimated_hours is None

    def test_new_post_with_empty_matter_number(self, client, db_session):
        """POST with empty matter_number stores None."""
        from app.models import Project

        client.post('/projects/new', data={
            'client_name': 'Empty Matter',
            'project_name': 'Empty Matter Project',
            'matter_number': '',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        project = Project.query.filter_by(client_name='Empty Matter').first()
        assert project.matter_number is None

    def test_new_post_with_initial_update(self, client, db_session):
        """POST with initial_update creates StatusUpdate."""
        from app.models import Project, StatusUpdate

        client.post('/projects/new', data={
            'client_name': 'Update Client',
            'project_name': 'Update Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium',
            'initial_update': 'Starting work on this project'
        })

        project = Project.query.filter_by(client_name='Update Client').first()
        updates = StatusUpdate.query.filter_by(project_id=project.id).all()
        assert len(updates) == 1
        assert updates[0].notes == 'Starting work on this project'

    def test_new_post_redirects_to_detail(self, client, db_session):
        """POST redirects to project detail page."""
        response = client.post('/projects/new', data={
            'client_name': 'Redirect Client',
            'project_name': 'Redirect Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/projects/' in response.location

    def test_new_post_sets_flash_message(self, client, db_session):
        """POST sets success flash message."""
        response = client.post('/projects/new', data={
            'client_name': 'Flash Client',
            'project_name': 'Flash Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        }, follow_redirects=True)

        assert b'created successfully' in response.data


class TestProjectDetail:
    """Test GET /projects/<id> route."""

    def test_detail_returns_200(self, client, sample_project, db_session):
        """Project detail page returns 200 OK."""
        response = client.get(f'/projects/{sample_project.id}')
        assert response.status_code == 200

    def test_detail_shows_project_info(self, client, sample_project, db_session):
        """Project detail shows project information."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_detail_404_for_missing_project(self, client, db_session):
        """Project detail returns 404 for non-existent project."""
        response = client.get('/projects/99999')
        assert response.status_code == 404

    def test_detail_shows_status_updates(self, client, sample_project_with_updates, db_session):
        """Project detail shows status updates newest-first."""
        response = client.get(f'/projects/{sample_project_with_updates.id}')

        assert b'Draft in progress' in response.data
        assert b'Initial research completed' in response.data
        # Check order: 'Draft' should appear before 'Initial' (newest first)
        draft_pos = response.data.find(b'Draft in progress')
        initial_pos = response.data.find(b'Initial research completed')
        assert draft_pos < initial_pos

    def test_detail_shows_no_updates_message(self, client, sample_project, db_session):
        """Project detail shows message when no updates exist."""
        response = client.get(f'/projects/{sample_project.id}')
        assert b'No status updates yet' in response.data

    def test_detail_shows_pending_followups(self, client, sample_project, db_session):
        """Project detail shows pending follow-ups with action buttons."""
        from app.models import FollowUp

        followup = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='John Doe',
            due_date=date.today() + timedelta(days=2),
            notes='Important follow-up'
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Pending' in response.data
        assert b'John Doe' in response.data
        assert b'associate' in response.data
        assert b'Important follow-up' in response.data
        assert b'Complete' in response.data
        assert b'Snooze' in response.data

    def test_detail_shows_completed_followups(self, client, sample_project, db_session):
        """Project detail shows completed follow-ups separately."""
        from app.models import FollowUp
        from datetime import datetime

        followup = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Jane Smith',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Completed' in response.data
        assert b'Jane Smith' in response.data
        assert b'client' in response.data

    def test_detail_shows_no_followups_message(self, client, sample_project, db_session):
        """Project detail shows message when no follow-ups exist."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'No pending follow-ups' in response.data
        assert b'No completed follow-ups' in response.data

    def test_detail_shows_add_followup_button(self, client, sample_project, db_session):
        """Project detail shows Add Follow-up button."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'Add Follow-up' in response.data

    def test_detail_shows_actual_hours(self, client, sample_project, db_session):
        """Project detail shows actual hours when set."""
        sample_project.actual_hours = 42.5
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Actual Hours' in response.data
        assert b'42.5' in response.data

    def test_detail_shows_archive_button_for_active(self, client, sample_project, db_session):
        """Project detail shows Archive button for active projects."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'Archive' in response.data
        assert b'Unarchive' not in response.data

    def test_detail_shows_unarchive_button_for_archived(self, client, sample_project, db_session):
        """Project detail shows Unarchive button for archived projects."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Unarchive' in response.data


class TestProjectEdit:
    """Test GET/POST /projects/<id>/edit routes."""

    def test_edit_get_returns_200(self, client, sample_project, db_session):
        """Edit project form returns 200 OK."""
        response = client.get(f'/projects/{sample_project.id}/edit')
        assert response.status_code == 200

    def test_edit_get_404_for_missing_project(self, client, db_session):
        """Edit returns 404 for non-existent project."""
        response = client.get('/projects/99999/edit')
        assert response.status_code == 404

    def test_edit_post_updates_project(self, client, sample_project, db_session):
        """POST to edit updates project fields."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': 'Updated Client',
            'project_name': 'Updated Project',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'New Partner',
            'assigned_attorneys': 'New Associate',
            'priority': 'low'
        }, follow_redirects=True)

        assert response.status_code == 200

        db_session.refresh(sample_project)
        assert sample_project.client_name == 'Updated Client'
        assert sample_project.project_name == 'Updated Project'

    def test_edit_post_with_hard_deadline(self, client, sample_project, db_session):
        """POST with hard_deadline parses date correctly."""
        hard_deadline = (date.today() + timedelta(days=60)).isoformat()

        client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'hard_deadline': hard_deadline,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority
        })

        db_session.refresh(sample_project)
        assert sample_project.hard_deadline == date.today() + timedelta(days=60)

    def test_edit_post_with_invalid_estimated_hours(self, client, sample_project, db_session):
        """POST with invalid estimated_hours falls back to None."""
        client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'estimated_hours': 'invalid'
        })

        db_session.refresh(sample_project)
        assert sample_project.estimated_hours is None

    def test_edit_post_with_invalid_actual_hours(self, client, sample_project, db_session):
        """POST with invalid actual_hours falls back to None."""
        client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'actual_hours': 'not-a-number'
        })

        db_session.refresh(sample_project)
        assert sample_project.actual_hours is None

    def test_edit_form_shows_actual_hours_field(self, client, sample_project, db_session):
        """Edit form shows actual_hours field."""
        response = client.get(f'/projects/{sample_project.id}/edit')

        assert b'actual_hours' in response.data
        assert b'Actual Hours' in response.data

    def test_edit_post_updates_updated_at(self, client, sample_project, db_session):
        """POST updates the updated_at timestamp."""
        original_updated_at = sample_project.updated_at

        client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': 'Timestamp Test',
            'project_name': sample_project.project_name,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority
        })

        db_session.refresh(sample_project)
        assert sample_project.updated_at >= original_updated_at

    def test_edit_post_redirects_to_detail(self, client, sample_project, db_session):
        """POST redirects to project detail page."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority
        }, follow_redirects=False)

        assert response.status_code == 302
        assert f'/projects/{sample_project.id}' in response.location

    def test_edit_post_sets_flash_message(self, client, sample_project, db_session):
        """POST sets success flash message."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'internal_deadline': date.today().isoformat(),
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority
        }, follow_redirects=True)

        assert b'updated successfully' in response.data

    def test_edit_post_404_for_missing_project(self, client, db_session):
        """Edit POST returns 404 for non-existent project."""
        response = client.post('/projects/99999/edit', data={
            'client_name': 'Test',
            'project_name': 'Test',
            'internal_deadline': date.today().isoformat(),
            'assigner': 'Test',
            'assigned_attorneys': 'Test',
            'priority': 'medium'
        })
        assert response.status_code == 404


class TestProjectArchive:
    """Test GET/POST /projects/<id>/archive route."""

    def test_archive_get_returns_200(self, client, sample_project, db_session):
        """Archive GET shows confirmation form."""
        response = client.get(f'/projects/{sample_project.id}/archive')
        assert response.status_code == 200

    def test_archive_get_shows_project_name(self, client, sample_project, db_session):
        """Archive GET shows project name for confirmation."""
        response = client.get(f'/projects/{sample_project.id}/archive')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_archive_get_shows_actual_hours_field(self, client, sample_project, db_session):
        """Archive GET shows actual_hours input field."""
        response = client.get(f'/projects/{sample_project.id}/archive')

        assert b'actual_hours' in response.data

    def test_archive_get_404_for_missing_project(self, client, db_session):
        """Archive GET returns 404 for non-existent project."""
        response = client.get('/projects/99999/archive')
        assert response.status_code == 404

    def test_archive_changes_status(self, client, sample_project, db_session):
        """Archive changes project status to archived."""
        client.post(f'/projects/{sample_project.id}/archive')

        db_session.refresh(sample_project)
        assert sample_project.status == 'archived'

    def test_archive_redirects_to_list(self, client, sample_project, db_session):
        """Archive redirects to project list."""
        response = client.post(f'/projects/{sample_project.id}/archive',
                               follow_redirects=False)

        assert response.status_code == 302
        assert '/projects/' in response.location

    def test_archive_404_for_missing_project(self, client, db_session):
        """Archive returns 404 for non-existent project."""
        response = client.post('/projects/99999/archive')
        assert response.status_code == 404

    def test_archive_sets_flash_message(self, client, sample_project, db_session):
        """Archive sets success flash message."""
        response = client.post(f'/projects/{sample_project.id}/archive',
                               follow_redirects=True)

        assert b'archived' in response.data

    def test_archive_updates_updated_at(self, client, sample_project, db_session):
        """Archive updates the updated_at timestamp."""
        original_updated_at = sample_project.updated_at

        client.post(f'/projects/{sample_project.id}/archive')

        db_session.refresh(sample_project)
        assert sample_project.updated_at >= original_updated_at

    def test_archive_post_saves_actual_hours(self, client, sample_project, db_session):
        """Archive POST saves actual_hours value."""
        client.post(f'/projects/{sample_project.id}/archive', data={
            'actual_hours': '35.5'
        })

        db_session.refresh(sample_project)
        assert sample_project.actual_hours == 35.5

    def test_archive_post_without_actual_hours(self, client, sample_project, db_session):
        """Archive POST works without actual_hours."""
        client.post(f'/projects/{sample_project.id}/archive', data={})

        db_session.refresh(sample_project)
        assert sample_project.status == 'archived'
        assert sample_project.actual_hours is None

    def test_archive_post_with_invalid_actual_hours(self, client, sample_project, db_session):
        """Archive POST with invalid actual_hours ignores the value."""
        client.post(f'/projects/{sample_project.id}/archive', data={
            'actual_hours': 'not-a-number'
        })

        db_session.refresh(sample_project)
        assert sample_project.status == 'archived'
        assert sample_project.actual_hours is None


class TestProjectUnarchive:
    """Test POST /projects/<id>/unarchive route."""

    def test_unarchive_changes_status(self, client, sample_project, db_session):
        """Unarchive changes project status to active."""
        sample_project.status = 'archived'
        db_session.commit()

        client.post(f'/projects/{sample_project.id}/unarchive')

        db_session.refresh(sample_project)
        assert sample_project.status == 'active'

    def test_unarchive_redirects_to_detail(self, client, sample_project, db_session):
        """Unarchive redirects to project detail."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.post(f'/projects/{sample_project.id}/unarchive',
                               follow_redirects=False)

        assert response.status_code == 302
        assert f'/projects/{sample_project.id}' in response.location

    def test_unarchive_404_for_missing_project(self, client, db_session):
        """Unarchive returns 404 for non-existent project."""
        response = client.post('/projects/99999/unarchive')
        assert response.status_code == 404

    def test_unarchive_sets_flash_message(self, client, sample_project, db_session):
        """Unarchive sets success flash message."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.post(f'/projects/{sample_project.id}/unarchive',
                               follow_redirects=True)

        assert b'reactivated' in response.data

    def test_unarchive_updates_updated_at(self, client, sample_project, db_session):
        """Unarchive updates the updated_at timestamp."""
        sample_project.status = 'archived'
        db_session.commit()
        original_updated_at = sample_project.updated_at

        client.post(f'/projects/{sample_project.id}/unarchive')

        db_session.refresh(sample_project)
        assert sample_project.updated_at >= original_updated_at


class TestArchivedList:
    """Test GET /projects/archived route."""

    def test_archived_list_returns_200(self, client, db_session):
        """Archived list page returns 200 OK."""
        response = client.get('/projects/archived')
        assert response.status_code == 200

    def test_archived_list_shows_archived_projects(self, client, sample_project, db_session):
        """Archived list shows archived projects."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get('/projects/archived')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_archived_list_excludes_active_projects(self, client, sample_project, db_session):
        """Archived list excludes active projects."""
        response = client.get('/projects/archived')

        assert b'Acme Corp' not in response.data

    def test_archived_list_shows_hours_columns(self, client, sample_project, db_session):
        """Archived list shows estimated and actual hours columns."""
        sample_project.status = 'archived'
        sample_project.estimated_hours = 40.0
        sample_project.actual_hours = 45.5
        db_session.commit()

        response = client.get('/projects/archived')

        assert b'Estimated Hours' in response.data
        assert b'Actual Hours' in response.data
        assert b'40' in response.data
        assert b'45.5' in response.data

    def test_archived_list_shows_unarchive_button(self, client, sample_project, db_session):
        """Archived list shows Unarchive button."""
        sample_project.status = 'archived'
        db_session.commit()

        response = client.get('/projects/archived')

        assert b'Unarchive' in response.data

    def test_archived_list_empty_state(self, client, db_session):
        """Archived list shows empty state message."""
        response = client.get('/projects/archived')

        assert b'No archived projects' in response.data
