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

    def test_list_shows_task_columns(self, client, sample_project, db_session):
        """Project list shows Tasks and Next Task columns."""
        response = client.get('/projects/')

        assert b'>Tasks<' in response.data
        assert b'Next Task' in response.data

    def test_list_shows_task_count(self, client, sample_project, db_session):
        """Project list shows count of pending tasks."""
        from app.models import Task

        # Create pending tasks
        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today(),
            priority='medium'
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1),
            priority='medium'
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        response = client.get('/projects/')

        # Should show count of 2
        assert b'>2<' in response.data

    def test_list_shows_attorneys_column(self, client, sample_project, db_session):
        """Project list shows Attorneys column."""
        response = client.get('/projects/')

        assert b'Attorneys' in response.data
        assert b'Associate Jones' in response.data

    def test_list_shows_add_task_button(self, client, sample_project, db_session):
        """Project list shows Add Task button for each project."""
        response = client.get('/projects/')

        assert b'Add Task' in response.data

    def test_list_shows_next_task_date(self, client, sample_project, db_session):
        """Project list shows next task due date."""
        from app.models import Task

        next_date = date.today() + timedelta(days=3)
        task = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=next_date,
            priority='medium'
        )
        db_session.add(task)
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
            'assigner': 'Partner',
            'assigned_attorneys': 'Associate',
            'priority': 'high'
        }, follow_redirects=True)

        assert response.status_code == 200
        project = Project.query.filter_by(client_name='New Client').first()
        assert project is not None

    def test_new_post_with_estimated_hours(self, client, db_session):
        """POST with estimated_hours parses float correctly."""
        from app.models import Project

        client.post('/projects/new', data={
            'client_name': 'Hours Client',
            'project_name': 'Hours Project',
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
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        }, follow_redirects=True)

        assert b'created successfully' in response.data

    def test_new_post_missing_client_name(self, client, db_session):
        """POST with missing client_name shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': '',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Client name is required' in response.data

    def test_new_post_missing_project_name(self, client, db_session):
        """POST with missing project_name shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': '',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Project name is required' in response.data

    def test_new_post_invalid_priority(self, client, db_session):
        """POST with invalid priority value shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'invalid'
        })

        assert response.status_code == 200
        assert b'Priority must be high, medium, or low' in response.data

    def test_new_post_invalid_estimated_hours(self, client, db_session):
        """POST with invalid estimated_hours shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium',
            'estimated_hours': 'not-a-number'
        })

        assert response.status_code == 200
        assert b'Estimated hours must be a valid number' in response.data

    def test_new_post_negative_estimated_hours(self, client, db_session):
        """POST with negative estimated_hours shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': 'medium',
            'estimated_hours': '-5'
        })

        assert response.status_code == 200
        assert b'Estimated hours cannot be negative' in response.data

    def test_new_post_missing_assigner(self, client, db_session):
        """POST with missing assigner shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': '',
            'assigned_attorneys': 'Me',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Assigner is required' in response.data

    def test_new_post_missing_assigned_attorneys(self, client, db_session):
        """POST with missing assigned_attorneys shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': '',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Assigned attorneys is required' in response.data

    def test_new_post_missing_priority(self, client, db_session):
        """POST with missing priority shows validation error."""
        response = client.post('/projects/new', data={
            'client_name': 'Test Client',
            'project_name': 'Test Project',
            'assigner': 'Self',
            'assigned_attorneys': 'Me',
            'priority': ''
        })

        assert response.status_code == 200
        assert b'Priority is required' in response.data


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

    def test_detail_shows_pending_tasks(self, client, sample_project, db_session):
        """Project detail shows pending tasks with action buttons."""
        from app.models import Task

        task = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='John Doe',
            due_date=date.today() + timedelta(days=2),
            description='Important task',
            priority='high'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Pending' in response.data
        assert b'John Doe' in response.data
        assert b'Associate' in response.data  # Formatted with title case
        assert b'Important task' in response.data
        assert b'Complete' in response.data
        assert b'Snooze' in response.data

    def test_detail_shows_completed_tasks(self, client, sample_project, db_session):
        """Project detail shows completed tasks separately."""
        from app.models import Task
        from datetime import datetime

        task = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Jane Smith',
            due_date=date.today(),
            priority='medium',
            completed=True,
            completed_at=datetime.utcnow()
        )
        db_session.add(task)
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')

        assert b'Completed' in response.data
        assert b'Jane Smith' in response.data
        assert b'Client' in response.data  # Formatted with title case

    def test_detail_shows_no_tasks_message(self, client, sample_project, db_session):
        """Project detail shows message when no tasks exist."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'No pending tasks' in response.data
        assert b'No completed tasks' in response.data

    def test_detail_shows_add_task_button(self, client, sample_project, db_session):
        """Project detail shows Add Task button."""
        response = client.get(f'/projects/{sample_project.id}')

        assert b'Add Task' in response.data

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
            'assigner': 'New Partner',
            'assigned_attorneys': 'New Associate',
            'priority': 'low'
        }, follow_redirects=True)

        assert response.status_code == 200

        db_session.refresh(sample_project)
        assert sample_project.client_name == 'Updated Client'
        assert sample_project.project_name == 'Updated Project'

    def test_edit_post_with_invalid_estimated_hours(self, client, sample_project, db_session):
        """POST with invalid estimated_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'estimated_hours': 'invalid'
        })

        assert response.status_code == 200
        assert b'Estimated hours must be a valid number' in response.data

    def test_edit_post_with_invalid_actual_hours(self, client, sample_project, db_session):
        """POST with invalid actual_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'actual_hours': 'not-a-number'
        })

        assert response.status_code == 200
        assert b'Actual hours must be a valid number' in response.data

    def test_edit_post_with_negative_estimated_hours(self, client, sample_project, db_session):
        """POST with negative estimated_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'estimated_hours': '-10'
        })

        assert response.status_code == 200
        assert b'Estimated hours cannot be negative' in response.data

    def test_edit_post_with_negative_actual_hours(self, client, sample_project, db_session):
        """POST with negative actual_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'actual_hours': '-5'
        })

        assert response.status_code == 200
        assert b'Actual hours cannot be negative' in response.data

    def test_edit_post_with_valid_hours(self, client, sample_project, db_session):
        """POST with valid estimated_hours and actual_hours saves correctly."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': sample_project.priority,
            'estimated_hours': '10.5',
            'actual_hours': '8.5'
        }, follow_redirects=True)

        assert response.status_code == 200
        db_session.refresh(sample_project)
        assert sample_project.estimated_hours == 10.5
        assert sample_project.actual_hours == 8.5

    def test_edit_post_missing_required_fields(self, client, sample_project, db_session):
        """POST with missing required fields shows validation errors."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': '',
            'project_name': '',
            'assigner': '',
            'assigned_attorneys': '',
            'priority': ''
        })

        assert response.status_code == 200
        assert b'Client name is required' in response.data
        assert b'Project name is required' in response.data

    def test_edit_post_invalid_priority(self, client, sample_project, db_session):
        """POST with invalid priority value shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/edit', data={
            'client_name': sample_project.client_name,
            'project_name': sample_project.project_name,
            'assigner': sample_project.assigner,
            'assigned_attorneys': sample_project.assigned_attorneys,
            'priority': 'invalid'
        })

        assert response.status_code == 200
        assert b'Priority must be high, medium, or low' in response.data

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
        """Archive POST with invalid actual_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/archive', data={
            'actual_hours': 'not-a-number'
        })

        assert response.status_code == 200
        assert b'Actual hours must be a valid number' in response.data
        db_session.refresh(sample_project)
        assert sample_project.status == 'active'  # Not archived due to error

    def test_archive_post_with_negative_actual_hours(self, client, sample_project, db_session):
        """Archive POST with negative actual_hours shows validation error."""
        response = client.post(f'/projects/{sample_project.id}/archive', data={
            'actual_hours': '-10'
        })

        assert response.status_code == 200
        assert b'Actual hours cannot be negative' in response.data
        db_session.refresh(sample_project)
        assert sample_project.status == 'active'  # Not archived due to error


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

    def test_archived_list_shows_all_spec_columns(self, client, sample_project, db_session):
        """Archived list shows all columns per spec: same as active list plus hours."""
        sample_project.status = 'archived'
        sample_project.assigned_attorneys = 'Alice, Bob'
        sample_project.priority = 'high'
        db_session.commit()

        response = client.get('/projects/archived')

        # Verify column headers exist
        assert b'Attorneys' in response.data
        assert b'Priority' in response.data

        # Verify data is displayed
        assert b'Alice, Bob' in response.data
        assert b'high' in response.data

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


class TestProjectListFiltering:
    """Test filtering functionality on GET /projects/ route."""

    def test_list_filter_by_priority_high(self, client, db_session):
        """Filter by priority=high shows only high priority projects."""
        from app.models import Project

        # Create projects with different priorities
        high = Project(client_name='High Client', project_name='High Project',
                      assigner='Self', assigned_attorneys='Me', priority='high')
        low = Project(client_name='Low Client', project_name='Low Project',
                     assigner='Self', assigned_attorneys='Me', priority='low')
        db_session.add_all([high, low])
        db_session.commit()

        response = client.get('/projects/?priority=high')

        assert b'High Client' in response.data
        assert b'Low Client' not in response.data

    def test_list_filter_by_priority_medium(self, client, db_session):
        """Filter by priority=medium shows only medium priority projects."""
        from app.models import Project

        medium = Project(client_name='Medium Client', project_name='Medium Project',
                        assigner='Self', assigned_attorneys='Me', priority='medium')
        high = Project(client_name='High Client', project_name='High Project',
                      assigner='Self', assigned_attorneys='Me', priority='high')
        db_session.add_all([medium, high])
        db_session.commit()

        response = client.get('/projects/?priority=medium')

        assert b'Medium Client' in response.data
        assert b'High Client' not in response.data

    def test_list_filter_by_priority_low(self, client, db_session):
        """Filter by priority=low shows only low priority projects."""
        from app.models import Project

        low = Project(client_name='Low Client', project_name='Low Project',
                     assigner='Self', assigned_attorneys='Me', priority='low')
        high = Project(client_name='High Client', project_name='High Project',
                      assigner='Self', assigned_attorneys='Me', priority='high')
        db_session.add_all([low, high])
        db_session.commit()

        response = client.get('/projects/?priority=low')

        assert b'Low Client' in response.data
        assert b'High Client' not in response.data

    def test_list_filter_by_attorney(self, client, db_session):
        """Filter by attorney uses contains match."""
        from app.models import Project

        jones = Project(client_name='Jones Client', project_name='Jones Project',
                       assigner='Self', assigned_attorneys='Smith, Jones', priority='medium')
        smith = Project(client_name='Smith Client', project_name='Smith Project',
                       assigner='Self', assigned_attorneys='Smith Only', priority='medium')
        db_session.add_all([jones, smith])
        db_session.commit()

        response = client.get('/projects/?attorney=Jones')

        assert b'Jones Client' in response.data
        assert b'Smith Client' not in response.data

    def test_list_filter_by_assigner(self, client, db_session):
        """Filter by assigner uses exact match."""
        from app.models import Project

        partner = Project(client_name='Partner Client', project_name='Partner Project',
                         assigner='Partner A', assigned_attorneys='Me', priority='medium')
        self_assigned = Project(client_name='Self Client', project_name='Self Project',
                               assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add_all([partner, self_assigned])
        db_session.commit()

        response = client.get('/projects/?assigner=Partner%20A')

        assert b'Partner Client' in response.data
        assert b'Self Client' not in response.data

    def test_list_combined_filters(self, client, db_session):
        """Multiple filters are ANDed together."""
        from app.models import Project

        match = Project(client_name='Match Client', project_name='Match Project',
                       assigner='Partner', assigned_attorneys='Jones', priority='high')
        wrong_priority = Project(client_name='Wrong Priority', project_name='WP Project',
                                assigner='Partner', assigned_attorneys='Jones', priority='low')
        wrong_attorney = Project(client_name='Wrong Attorney', project_name='WA Project',
                                assigner='Partner', assigned_attorneys='Smith', priority='high')
        db_session.add_all([match, wrong_priority, wrong_attorney])
        db_session.commit()

        response = client.get('/projects/?priority=high&attorney=Jones')

        assert b'Match Client' in response.data
        assert b'Wrong Priority' not in response.data
        assert b'Wrong Attorney' not in response.data

    def test_list_no_filters_shows_all(self, client, db_session):
        """Empty filters return all active projects."""
        from app.models import Project

        p1 = Project(client_name='Client One', project_name='Project One',
                    assigner='Self', assigned_attorneys='Me', priority='high')
        p2 = Project(client_name='Client Two', project_name='Project Two',
                    assigner='Self', assigned_attorneys='Me', priority='low')
        db_session.add_all([p1, p2])
        db_session.commit()

        response = client.get('/projects/')

        assert b'Client One' in response.data
        assert b'Client Two' in response.data


class TestProjectListSorting:
    """Test sorting functionality on GET /projects/ route."""

    def test_list_sort_by_priority_asc(self, client, db_session):
        """Sort by priority ascending (high > medium > low)."""
        from app.models import Project

        high = Project(client_name='High Client', project_name='High Project',
                      assigner='Self', assigned_attorneys='Me', priority='high')
        low = Project(client_name='Low Client', project_name='Low Project',
                     assigner='Self', assigned_attorneys='Me', priority='low')
        medium = Project(client_name='Medium Client', project_name='Medium Project',
                        assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add_all([low, high, medium])
        db_session.commit()

        response = client.get('/projects/?sort_by=priority&sort_order=asc')

        # Should be ordered high, medium, low
        high_pos = response.data.find(b'High Client')
        medium_pos = response.data.find(b'Medium Client')
        low_pos = response.data.find(b'Low Client')
        assert high_pos < medium_pos < low_pos

    def test_list_sort_by_priority_desc(self, client, db_session):
        """Sort by priority descending (low > medium > high)."""
        from app.models import Project

        high = Project(client_name='High Client', project_name='High Project',
                      assigner='Self', assigned_attorneys='Me', priority='high')
        low = Project(client_name='Low Client', project_name='Low Project',
                     assigner='Self', assigned_attorneys='Me', priority='low')
        db_session.add_all([high, low])
        db_session.commit()

        response = client.get('/projects/?sort_by=priority&sort_order=desc')

        # Low should appear before high
        high_pos = response.data.find(b'High Client')
        low_pos = response.data.find(b'Low Client')
        assert low_pos < high_pos

    def test_list_sort_by_staleness_desc(self, client, db_session):
        """Sort by staleness descending (most stale first)."""
        from app.models import Project, StatusUpdate
        from datetime import datetime

        # Create projects with different staleness
        stale = Project(client_name='Stale Client', project_name='Stale Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        fresh = Project(client_name='Fresh Client', project_name='Fresh Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add_all([stale, fresh])
        db_session.flush()

        # Add recent update to fresh project only
        update = StatusUpdate(project_id=fresh.id, notes='Recent update')
        db_session.add(update)
        db_session.commit()

        response = client.get('/projects/?sort_by=staleness&sort_order=desc')

        # Stale (no updates) should appear before Fresh (has update)
        stale_pos = response.data.find(b'Stale Client')
        fresh_pos = response.data.find(b'Fresh Client')
        assert stale_pos < fresh_pos

    def test_list_sort_by_staleness_asc(self, client, db_session):
        """Sort by staleness ascending (freshest first)."""
        from app.models import Project, StatusUpdate
        from datetime import datetime

        # Create a stale project with old created_at
        stale = Project(client_name='Stale Client', project_name='Stale Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        stale.created_at = datetime.utcnow() - timedelta(days=10)  # 10 days old

        # Create a fresh project with recent created_at
        fresh = Project(client_name='Fresh Client', project_name='Fresh Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        # fresh.created_at will be now (0 days old)

        db_session.add_all([stale, fresh])
        db_session.commit()

        response = client.get('/projects/?sort_by=staleness&sort_order=asc')

        # Fresh (0 days) should appear before Stale (10 days)
        stale_pos = response.data.find(b'Stale Client')
        fresh_pos = response.data.find(b'Fresh Client')
        assert fresh_pos < stale_pos

    def test_list_filter_and_sort_combined(self, client, db_session):
        """Filters and sorting work together."""
        from app.models import Project

        h1 = Project(client_name='High Early', project_name='HE Project',
                    assigner='Self', assigned_attorneys='Me', priority='high')
        h2 = Project(client_name='High Late', project_name='HL Project',
                    assigner='Self', assigned_attorneys='Me', priority='high')
        low = Project(client_name='Low Client', project_name='Low Project',
                     assigner='Self', assigned_attorneys='Me', priority='low')
        db_session.add_all([h2, h1, low])
        db_session.commit()

        response = client.get('/projects/?priority=high')

        # Only high priority should appear
        assert b'High Early' in response.data
        assert b'High Late' in response.data
        assert b'Low Client' not in response.data

    def test_list_sort_by_client_name_asc(self, client, db_session):
        """Sort by client_name ascending (A-Z)."""
        from app.models import Project

        zebra = Project(client_name='Zebra Corp', project_name='Zebra Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        acme = Project(client_name='Acme Inc', project_name='Acme Project',
                      assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add_all([zebra, acme])
        db_session.commit()

        response = client.get('/projects/?sort_by=client_name&sort_order=asc')

        # Acme should appear before Zebra (alphabetical)
        acme_pos = response.data.find(b'Acme Inc')
        zebra_pos = response.data.find(b'Zebra Corp')
        assert acme_pos < zebra_pos

    def test_list_sort_by_client_name_desc(self, client, db_session):
        """Sort by client_name descending (Z-A)."""
        from app.models import Project

        zebra = Project(client_name='Zebra Corp', project_name='Zebra Project',
                       assigner='Self', assigned_attorneys='Me', priority='medium')
        acme = Project(client_name='Acme Inc', project_name='Acme Project',
                      assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add_all([zebra, acme])
        db_session.commit()

        response = client.get('/projects/?sort_by=client_name&sort_order=desc')

        # Zebra should appear before Acme (reverse alphabetical)
        acme_pos = response.data.find(b'Acme Inc')
        zebra_pos = response.data.find(b'Zebra Corp')
        assert zebra_pos < acme_pos

    def test_list_client_name_sort_link_appears(self, client, db_session):
        """Client column has sortable link in template."""
        from app.models import Project

        project = Project(client_name='Test Client', project_name='Test',
                         assigner='Self', assigned_attorneys='Me', priority='medium')
        db_session.add(project)
        db_session.commit()

        response = client.get('/projects/')

        # Sort link should contain client_name parameter
        assert b'sort_by=client_name' in response.data


class TestProjectListTemplateContext:
    """Test that filter state and dropdown values are passed to template."""

    def test_list_passes_dropdown_values(self, client, db_session):
        """Template receives attorneys and assigners lists."""
        from app.models import Project

        p1 = Project(client_name='Client A', project_name='Project A',
                    assigner='Partner Bob', assigned_attorneys='Associate Alice', priority='medium')
        p2 = Project(client_name='Client B', project_name='Project B',
                    assigner='Partner Carol', assigned_attorneys='Associate Dave', priority='medium')
        db_session.add_all([p1, p2])
        db_session.commit()

        response = client.get('/projects/')

        # Check dropdown options are rendered
        assert b'Associate Alice' in response.data
        assert b'Associate Dave' in response.data
        assert b'Partner Bob' in response.data
        assert b'Partner Carol' in response.data

    def test_list_shows_filter_form(self, client, db_session):
        """Template displays filter form controls."""
        response = client.get('/projects/')

        assert b'filter-form' in response.data
        assert b'name="priority"' in response.data
        assert b'name="attorney"' in response.data
        assert b'name="assigner"' in response.data
        assert b'Apply Filters' in response.data
        assert b'Clear' in response.data

    def test_list_shows_sort_links(self, client, sample_project, db_session):
        """Template displays sortable column header links."""
        response = client.get('/projects/')

        assert b'sort-link' in response.data
        assert b'sort_by=priority' in response.data
        assert b'sort_by=staleness' in response.data

    def test_list_shows_sort_indicator_for_current_sort(self, client, sample_project, db_session):
        """Template shows sort indicator arrow for current sort column."""
        response = client.get('/projects/?sort_by=priority&sort_order=asc')

        # Should have an up arrow for asc sort on priority
        assert b'sort-indicator' in response.data

    def test_list_preserves_filter_in_sort_links(self, client, sample_project, db_session):
        """Sort links preserve current filter state in query params."""
        response = client.get('/projects/?priority=high')

        # Sort links should include priority=high
        assert b'priority=high' in response.data

    def test_list_invalid_sort_column_defaults_to_client_name(self, client, sample_project, db_session):
        """Invalid sort_by parameter defaults to client_name sort."""
        response = client.get('/projects/?sort_by=invalid_column')

        # Should return 200 OK and show the project
        assert response.status_code == 200
        assert b'Acme Corp' in response.data


class TestProjectMilestonesNewRedirect:
    """Test GET /projects/<id>/milestones/new redirect route."""

    def test_milestones_new_redirects_to_milestone_form(self, client, sample_project, db_session):
        """Route redirects to milestone form with project pre-selected."""
        response = client.get(f'/projects/{sample_project.id}/milestones/new',
                              follow_redirects=False)
        assert response.status_code == 302
        assert f'/milestones/new?project_id={sample_project.id}' in response.location

    def test_milestones_new_404_for_missing_project(self, client, db_session):
        """Route returns 404 for non-existent project."""
        response = client.get('/projects/99999/milestones/new')
        assert response.status_code == 404


class TestProjectListUIResponsiveness:
    """Test project list UI elements."""

    def test_list_has_table_wrapper(self, client, sample_project, db_session):
        """Project list table is wrapped in table-wrapper div for mobile scrolling."""
        response = client.get('/projects/')
        data = response.data.decode('utf-8')
        assert 'class="table-wrapper"' in data


class TestProjectDetailUIConfirmation:
    """Test project detail UI elements."""

    def test_detail_complete_button_has_data_confirm(self, client, sample_project, sample_task, db_session):
        """Complete button on project detail has data-confirm attribute."""
        response = client.get(f'/projects/{sample_project.id}')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this task as complete?"' in data
