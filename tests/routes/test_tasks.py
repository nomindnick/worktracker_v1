"""Tests for app/routes/tasks.py - Task routes."""

from datetime import date, timedelta
from app.models import Task


class TestTaskList:
    """Test GET /tasks/ route."""

    def test_list_returns_200(self, client, db_session):
        """Task list returns 200 OK."""
        response = client.get('/tasks/')
        assert response.status_code == 200

    def test_list_shows_pending_tasks(self, client, sample_task, db_session):
        """Task list shows pending (incomplete) tasks."""
        response = client.get('/tasks/')

        assert b'John Doe' in response.data

    def test_list_excludes_completed_tasks(self, client, sample_task, db_session):
        """Task list excludes completed tasks."""
        sample_task.completed = True
        db_session.commit()

        response = client.get('/tasks/')

        assert b'John Doe' not in response.data


class TestTaskNew:
    """Test GET/POST /tasks/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New task form returns 200 OK."""
        response = client.get('/tasks/new')
        assert response.status_code == 200

    def test_new_get_shows_project_dropdown(self, client, sample_project, db_session):
        """New task form shows projects in dropdown."""
        response = client.get('/tasks/new')

        assert b'Acme Corp' in response.data
        assert b'Patent Application' in response.data

    def test_new_get_preselects_project(self, client, sample_project, db_session):
        """New task form pre-selects project from query param."""
        response = client.get(f'/tasks/new?project_id={sample_project.id}')

        assert b'selected' in response.data

    def test_new_post_creates_task(self, client, sample_project, db_session):
        """POST creates a new task in database."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Jane Smith',
            'due_date': due_date,
            'description': 'Follow up on contract',
            'priority': 'high'
        }, follow_redirects=False)

        assert response.status_code == 302

        # Verify task was created
        task = Task.query.filter_by(target_name='Jane Smith').first()
        assert task is not None
        assert task.project_id == sample_project.id
        assert task.target_type == 'client'
        assert task.description == 'Follow up on contract'
        assert task.priority == 'high'

    def test_new_post_redirects_to_project(self, client, sample_project, db_session):
        """POST redirects to project detail page."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'associate',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert f'/projects/{sample_project.id}' in response.location

    def test_new_post_flashes_success(self, client, sample_project, db_session):
        """POST flashes success message."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=True)

        assert b'Task created successfully' in response.data

    def test_new_post_validates_required_fields(self, client, sample_project, db_session):
        """POST validates required fields (target_name, due_date)."""
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': '',
            'due_date': '',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Target name is required' in response.data
        assert b'Due date is required' in response.data

    def test_new_post_validates_due_date_format(self, client, sample_project, db_session):
        """POST with invalid due_date format shows validation error."""
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': 'not-a-date',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Due date must be a valid date' in response.data

    def test_new_post_validates_target_type(self, client, sample_project, db_session):
        """POST with invalid target_type shows validation error."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'invalid_type',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Invalid target type' in response.data

    def test_new_post_validates_priority(self, client, sample_project, db_session):
        """POST with invalid priority shows validation error."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'invalid'
        })

        assert response.status_code == 200
        assert b'Invalid priority' in response.data

    def test_new_post_404_for_invalid_project(self, client, db_session):
        """POST returns 404 for non-existent project."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': 99999,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 404

    def test_new_post_404_for_archived_project(self, client, sample_project, db_session):
        """POST returns 404 for archived project."""
        sample_project.status = 'archived'
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 404

    def test_new_post_defaults_target_type_to_self(self, client, sample_project, db_session):
        """POST defaults target_type to 'self' if empty."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': '',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert response.status_code == 302
        task = Task.query.filter_by(target_name='Test Person').first()
        assert task.target_type == 'self'

    def test_new_post_defaults_priority_to_medium(self, client, sample_project, db_session):
        """POST defaults priority to 'medium' if empty."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': ''
        }, follow_redirects=False)

        assert response.status_code == 302
        task = Task.query.filter_by(target_name='Test Person').first()
        assert task.priority == 'medium'

    def test_new_post_handles_optional_description(self, client, sample_project, db_session):
        """POST handles missing description field gracefully."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/new', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert response.status_code == 302
        task = Task.query.filter_by(target_name='Test Person').first()
        assert task.description is None

    def test_new_post_accepts_all_target_types(self, client, sample_project, db_session):
        """POST accepts all valid target_type values."""
        valid_types = ['self', 'associate', 'client', 'opposing_counsel', 'assigning_attorney']

        for i, target_type in enumerate(valid_types):
            due_date = (date.today() + timedelta(days=7+i)).isoformat()
            response = client.post('/tasks/new', data={
                'project_id': sample_project.id,
                'target_type': target_type,
                'target_name': f'Person {i}',
                'due_date': due_date,
                'priority': 'medium'
            }, follow_redirects=False)

            assert response.status_code == 302
            task = Task.query.filter_by(target_name=f'Person {i}').first()
            assert task.target_type == target_type


class TestTaskComplete:
    """Test POST /tasks/<id>/complete route."""

    def test_complete_returns_redirect(self, client, sample_task, db_session):
        """Complete redirects."""
        response = client.post(f'/tasks/{sample_task.id}/complete',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_complete_404_for_missing_task(self, client, db_session):
        """Complete returns 404 for non-existent task."""
        response = client.post('/tasks/99999/complete')
        assert response.status_code == 404

    def test_complete_redirects_to_referrer(self, client, sample_task, db_session):
        """Complete redirects to referrer if available."""
        response = client.post(f'/tasks/{sample_task.id}/complete',
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'

    def test_complete_redirects_to_dashboard_without_referrer(self, client, sample_task, db_session):
        """Complete redirects to dashboard when no referrer."""
        response = client.post(f'/tasks/{sample_task.id}/complete',
                               follow_redirects=False)
        assert '/' in response.location

    def test_complete_marks_task_as_completed(self, client, sample_task, db_session):
        """Complete sets completed=True on the task."""
        assert sample_task.completed is False

        response = client.post(f'/tasks/{sample_task.id}/complete',
                               follow_redirects=False)

        db_session.refresh(sample_task)
        assert sample_task.completed is True
        assert sample_task.completed_at is not None

    def test_complete_flashes_success_message(self, client, sample_task, db_session):
        """Complete shows success flash message."""
        response = client.post(f'/tasks/{sample_task.id}/complete',
                               follow_redirects=True)
        assert b'Task marked as complete' in response.data

    def test_complete_removes_from_pending_list(self, client, sample_task, db_session):
        """Completed task no longer appears in pending list."""
        # Verify it's in the list initially
        response = client.get('/tasks/')
        assert b'John Doe' in response.data

        # Complete it
        client.post(f'/tasks/{sample_task.id}/complete')

        # Verify it's no longer in the list
        response = client.get('/tasks/')
        assert b'John Doe' not in response.data


class TestTaskSnooze:
    """Test POST /tasks/<id>/snooze route."""

    def test_snooze_returns_redirect(self, client, sample_task, db_session):
        """Snooze redirects."""
        response = client.post(f'/tasks/{sample_task.id}/snooze',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_snooze_404_for_missing_task(self, client, db_session):
        """Snooze returns 404 for non-existent task."""
        response = client.post('/tasks/99999/snooze')
        assert response.status_code == 404

    def test_snooze_updates_due_date(self, client, sample_task, db_session):
        """Snooze updates the task due date by specified days."""
        original_due_date = sample_task.due_date

        response = client.post(f'/tasks/{sample_task.id}/snooze',
                               data={'days': 3},
                               follow_redirects=False)

        db_session.refresh(sample_task)
        assert sample_task.due_date == original_due_date + timedelta(days=3)

    def test_snooze_defaults_to_one_day(self, client, sample_task, db_session):
        """Snooze defaults to 1 day if days parameter not provided."""
        original_due_date = sample_task.due_date

        response = client.post(f'/tasks/{sample_task.id}/snooze',
                               follow_redirects=False)

        db_session.refresh(sample_task)
        assert sample_task.due_date == original_due_date + timedelta(days=1)

    def test_snooze_flashes_success_message(self, client, sample_task, db_session):
        """Snooze shows success flash message."""
        response = client.post(f'/tasks/{sample_task.id}/snooze',
                               data={'days': 7},
                               follow_redirects=True)
        assert b'Task snoozed by 7 day(s)' in response.data

    def test_snooze_redirects_to_referrer(self, client, sample_task, db_session):
        """Snooze redirects to referrer if available."""
        response = client.post(f'/tasks/{sample_task.id}/snooze',
                               data={'days': 1},
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'


class TestProjectTasksNew:
    """Test GET /projects/<id>/tasks/new route."""

    def test_project_tasks_new_redirects(self, client, sample_project, db_session):
        """GET /projects/<id>/tasks/new redirects to /tasks/new with project_id."""
        response = client.get(f'/projects/{sample_project.id}/tasks/new',
                              follow_redirects=False)

        assert response.status_code == 302
        assert '/tasks/new' in response.location
        assert f'project_id={sample_project.id}' in response.location

    def test_project_tasks_new_invalid_id_returns_404(self, client, db_session):
        """GET /projects/<id>/tasks/new with invalid id returns 404."""
        response = client.get('/projects/99999/tasks/new')
        assert response.status_code == 404

    def test_project_tasks_new_full_flow(self, client, sample_project, db_session):
        """GET /projects/<id>/tasks/new redirects to form with project pre-selected."""
        response = client.get(f'/projects/{sample_project.id}/tasks/new',
                              follow_redirects=True)

        assert response.status_code == 200
        assert b'selected' in response.data


class TestTaskListUI:
    """Test task list UI elements."""

    def test_list_has_table_wrapper(self, client, sample_task, db_session):
        """Task list table is wrapped in table-wrapper div."""
        response = client.get('/tasks/')
        data = response.data.decode('utf-8')
        assert 'class="table-wrapper"' in data

    def test_list_complete_button_has_data_confirm(self, client, sample_task, db_session):
        """Complete button in task list has data-confirm attribute."""
        response = client.get('/tasks/')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this task as complete?"' in data

    def test_list_shows_priority_column(self, client, sample_task, db_session):
        """Task list shows priority column."""
        response = client.get('/tasks/')
        data = response.data.decode('utf-8')
        assert 'Priority' in data

    def test_list_has_edit_button(self, client, sample_task, db_session):
        """Task list shows Edit button for each task."""
        response = client.get('/tasks/')
        data = response.data.decode('utf-8')
        assert f'/tasks/{sample_task.id}/edit' in data
        assert '>Edit</a>' in data


class TestTaskEdit:
    """Test GET/POST /tasks/<id>/edit routes."""

    def test_edit_get_returns_200(self, client, sample_task, db_session):
        """Edit task form returns 200 OK."""
        response = client.get(f'/tasks/{sample_task.id}/edit')
        assert response.status_code == 200

    def test_edit_get_404_for_missing_task(self, client, db_session):
        """Edit returns 404 for non-existent task."""
        response = client.get('/tasks/99999/edit')
        assert response.status_code == 404

    def test_edit_get_shows_current_values(self, client, sample_task, db_session):
        """Edit form shows task's current field values."""
        response = client.get(f'/tasks/{sample_task.id}/edit')
        data = response.data.decode('utf-8')

        assert sample_task.target_name in data
        assert str(sample_task.due_date) in data

    def test_edit_get_preselects_project(self, client, sample_task, sample_project, db_session):
        """Edit form pre-selects the task's current project."""
        response = client.get(f'/tasks/{sample_task.id}/edit')
        data = response.data.decode('utf-8')

        # Project should be selected in dropdown
        assert 'Acme Corp' in data
        assert 'selected' in data

    def test_edit_get_preselects_target_type(self, client, sample_task, db_session):
        """Edit form pre-selects the task's current target_type."""
        sample_task.target_type = 'client'
        db_session.commit()

        response = client.get(f'/tasks/{sample_task.id}/edit')
        data = response.data.decode('utf-8')

        # Find the client option and verify it has selected
        assert 'value="client"' in data

    def test_edit_get_preselects_priority(self, client, sample_task, db_session):
        """Edit form pre-selects the task's current priority."""
        sample_task.priority = 'high'
        db_session.commit()

        response = client.get(f'/tasks/{sample_task.id}/edit')
        data = response.data.decode('utf-8')

        # Find the high option with selected
        assert 'value="high"' in data

    def test_edit_post_updates_task(self, client, sample_task, sample_project, db_session):
        """POST to edit updates task fields."""
        new_due_date = (date.today() + timedelta(days=14)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'opposing_counsel',
            'target_name': 'Updated Name',
            'due_date': new_due_date,
            'description': 'Updated description',
            'priority': 'low'
        }, follow_redirects=False)

        assert response.status_code == 302

        # Verify task was updated
        db_session.refresh(sample_task)
        assert sample_task.target_name == 'Updated Name'
        assert sample_task.target_type == 'opposing_counsel'
        assert sample_task.description == 'Updated description'
        assert sample_task.priority == 'low'

    def test_edit_post_redirects_to_project_detail(self, client, sample_task, sample_project, db_session):
        """POST redirects to project detail page."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert f'/projects/{sample_project.id}' in response.location

    def test_edit_post_flashes_success(self, client, sample_task, sample_project, db_session):
        """POST sets success flash message."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=True)

        assert b'Task updated successfully' in response.data

    def test_edit_post_validates_required_target_name(self, client, sample_task, sample_project, db_session):
        """POST validates target_name is required."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': '',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Target name is required' in response.data

    def test_edit_post_validates_required_due_date(self, client, sample_task, sample_project, db_session):
        """POST validates due_date is required."""
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': '',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Due date is required' in response.data

    def test_edit_post_validates_due_date_format(self, client, sample_task, sample_project, db_session):
        """POST with invalid due_date format shows validation error."""
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': 'not-a-date',
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Due date must be a valid date' in response.data

    def test_edit_post_validates_target_type(self, client, sample_task, sample_project, db_session):
        """POST with invalid target_type shows validation error."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'invalid_type',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 200
        assert b'Invalid target type' in response.data

    def test_edit_post_validates_priority(self, client, sample_task, sample_project, db_session):
        """POST with invalid priority shows validation error."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'invalid'
        })

        assert response.status_code == 200
        assert b'Invalid priority' in response.data

    def test_edit_post_404_for_missing_task(self, client, db_session):
        """Edit POST returns 404 for non-existent task."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post('/tasks/99999/edit', data={
            'project_id': 1,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 404

    def test_edit_post_404_for_invalid_project(self, client, sample_task, db_session):
        """POST returns 404 for non-existent project."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': 99999,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 404

    def test_edit_post_404_for_archived_project(self, client, sample_task, sample_project, db_session):
        """POST returns 404 if moving task to archived project."""
        sample_project.status = 'archived'
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        })

        assert response.status_code == 404

    def test_edit_post_defaults_target_type_to_self(self, client, sample_task, sample_project, db_session):
        """POST defaults target_type to 'self' if empty."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': '',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert response.status_code == 302
        db_session.refresh(sample_task)
        assert sample_task.target_type == 'self'

    def test_edit_post_defaults_priority_to_medium(self, client, sample_task, sample_project, db_session):
        """POST defaults priority to 'medium' if empty."""
        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': ''
        }, follow_redirects=False)

        assert response.status_code == 302
        db_session.refresh(sample_task)
        assert sample_task.priority == 'medium'

    def test_edit_post_handles_optional_description(self, client, sample_task, sample_project, db_session):
        """POST handles empty description correctly (sets to None)."""
        sample_task.description = 'Some description'
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium',
            'description': ''
        }, follow_redirects=False)

        assert response.status_code == 302
        db_session.refresh(sample_task)
        assert sample_task.description is None

    def test_edit_allows_editing_completed_task(self, client, sample_task, sample_project, db_session):
        """Completed tasks can still be edited."""
        from datetime import datetime
        sample_task.completed = True
        sample_task.completed_at = datetime.utcnow()
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': sample_project.id,
            'target_type': 'client',
            'target_name': 'Updated Completed Task',
            'due_date': due_date,
            'priority': 'high'
        }, follow_redirects=False)

        assert response.status_code == 302
        db_session.refresh(sample_task)
        assert sample_task.target_name == 'Updated Completed Task'
        assert sample_task.completed is True  # Still completed

    def test_edit_allows_changing_project(self, client, sample_task, sample_project, db_session):
        """POST allows moving task to a different active project."""
        from app.models import Project

        # Create a second project
        project2 = Project(
            client_name='Other Corp',
            project_name='Other Matter',
            assigner='Jane Doe',
            assigned_attorneys='Bob'
        )
        db_session.add(project2)
        db_session.commit()

        due_date = (date.today() + timedelta(days=7)).isoformat()
        response = client.post(f'/tasks/{sample_task.id}/edit', data={
            'project_id': project2.id,
            'target_type': 'client',
            'target_name': 'Test Person',
            'due_date': due_date,
            'priority': 'medium'
        }, follow_redirects=False)

        assert response.status_code == 302
        db_session.refresh(sample_task)
        assert sample_task.project_id == project2.id


class TestProjectDetailTaskEditUI:
    """Test Edit button in project detail page."""

    def test_project_detail_has_edit_button_for_pending_tasks(self, client, sample_task, sample_project, db_session):
        """Project detail page shows Edit button for pending tasks."""
        response = client.get(f'/projects/{sample_project.id}')
        data = response.data.decode('utf-8')

        assert f'/tasks/{sample_task.id}/edit' in data

    def test_project_detail_has_edit_button_for_completed_tasks(self, client, sample_task, sample_project, db_session):
        """Project detail page shows Edit button for completed tasks."""
        from datetime import datetime
        sample_task.completed = True
        sample_task.completed_at = datetime.utcnow()
        db_session.commit()

        response = client.get(f'/projects/{sample_project.id}')
        data = response.data.decode('utf-8')

        assert f'/tasks/{sample_task.id}/edit' in data
