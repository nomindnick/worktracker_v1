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
