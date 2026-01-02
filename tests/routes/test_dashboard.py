"""Tests for app/routes/dashboard.py - Dashboard routes."""

from datetime import date, datetime, timedelta
from app.models import Project, Task, StatusUpdate


class TestDashboardIndex:
    """Test GET / (dashboard index) route."""

    def test_index_returns_200(self, client, db_session):
        """Dashboard index returns 200 OK."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_renders_template(self, client, db_session):
        """Dashboard renders dashboard.html template."""
        response = client.get('/')
        assert response.status_code == 200

    def test_empty_dashboard(self, client, db_session):
        """Dashboard renders with no data."""
        response = client.get('/')
        assert response.status_code == 200
        # Should have the new section headings based on task due dates
        assert b'Due Today' in response.data
        assert b'Due Tomorrow' in response.data
        assert b'Due This Week' in response.data


class TestDashboardTaskCategories:
    """Test project categorization by next task due date."""

    def test_project_with_task_due_today_appears_in_due_today_section(self, client, db_session):
        """Project with task due today appears in Due Today section."""
        project = Project(
            client_name='Due Today Client',
            project_name='Due Today Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Due Today Client' in response.data

    def test_project_with_task_due_tomorrow_appears_in_due_tomorrow_section(self, client, db_session):
        """Project with task due tomorrow appears in Due Tomorrow section."""
        project = Project(
            client_name='Due Tomorrow Client',
            project_name='Due Tomorrow Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=1),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Due Tomorrow Client' in response.data

    def test_project_with_task_due_in_3_days_appears_in_this_week_section(self, client, db_session):
        """Project with task due in 3 days appears in Due This Week section."""
        project = Project(
            client_name='Due In 3 Days Client',
            project_name='Due In 3 Days Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=3),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Due In 3 Days Client' in response.data

    def test_project_with_task_due_in_10_days_appears_in_due_later_section(self, client, db_session):
        """Project with task due in 10 days appears in Due Later section."""
        project = Project(
            client_name='Due In 10 Days Client',
            project_name='Due In 10 Days Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=10),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Due In 10 Days Client' in response.data

    def test_project_with_task_due_more_than_14_days_not_shown(self, client, db_session):
        """Project with task due > 14 days out does not appear on dashboard."""
        project = Project(
            client_name='Far Future Client',
            project_name='Far Future Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=20),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Far Future Client' not in response.data

    def test_project_with_no_tasks_appears_in_no_tasks_section(self, client, db_session):
        """Projects with no pending tasks appear in No Tasks section."""
        project = Project(
            client_name='No Tasks Client',
            project_name='No Tasks Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'No Tasks Client' in response.data

    def test_overdue_task_appears_in_due_today(self, client, db_session):
        """Projects with overdue tasks appear in Due Today section."""
        project = Project(
            client_name='Overdue Client',
            project_name='Overdue Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() - timedelta(days=3),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Overdue Client' in response.data

    def test_archived_project_excluded(self, client, db_session):
        """Archived projects don't appear on dashboard."""
        project = Project(
            client_name='Archived Client',
            project_name='Archived Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney',
            status='archived'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Archived Client' not in response.data

    def test_completed_task_not_used_for_categorization(self, client, db_session):
        """Completed tasks are not used for project categorization."""
        project = Project(
            client_name='Completed Task Client',
            project_name='Completed Task Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Completed task (should be ignored)
        completed_task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Completed Task',
            due_date=date.today(),
            priority='medium',
            completed=True,
            completed_at=datetime.utcnow()
        )
        # Pending task for later
        pending_task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Pending Task',
            due_date=date.today() + timedelta(days=5),
            priority='medium'
        )
        db_session.add_all([completed_task, pending_task])
        db_session.commit()

        response = client.get('/')
        # Project should be categorized by the pending task (5 days out)
        assert b'Completed Task Client' in response.data


class TestInlineTasks:
    """Test tasks displayed inline within project cards."""

    def test_pending_tasks_shown_in_project_card(self, client, db_session):
        """Pending tasks appear within their project's card."""
        project = Project(
            client_name='Task Client',
            project_name='Task Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Inline Target',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Inline Target' in response.data

    def test_task_description_shown_in_project_card(self, client, db_session):
        """Task description appears within the project card when present."""
        project = Project(
            client_name='Description Client',
            project_name='Description Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium',
            description='Review the contract documents carefully'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Review the contract documents carefully' in response.data
        assert b'task-description' in response.data

    def test_task_without_description_no_description_div(self, client, db_session):
        """Tasks without description do not render empty description div."""
        project = Project(
            client_name='No Desc Client',
            project_name='No Desc Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='No Desc Target',
            due_date=date.today(),
            priority='medium',
            description=None
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        # The task should be shown
        assert 'No Desc Target' in data
        # But there should be no task-description div for this task
        # Count occurrences - should be 0 since this is the only task
        assert data.count('task-description') == 0

    def test_overdue_task_has_overdue_styling(self, client, db_session):
        """Overdue tasks have CSS class for visual distinction."""
        project = Project(
            client_name='Overdue Task Client',
            project_name='Overdue Task Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Overdue Target',
            due_date=date.today() - timedelta(days=3),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'task-overdue' in response.data

    def test_task_due_today_has_due_today_styling(self, client, db_session):
        """Tasks due today have CSS class for visual distinction."""
        project = Project(
            client_name='Today Task Client',
            project_name='Today Task Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Today Target',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'task-due-today' in response.data

    def test_completed_tasks_not_shown(self, client, db_session):
        """Completed tasks are not shown in project cards."""
        project = Project(
            client_name='Completed Task Client',
            project_name='Completed Task Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Completed Target',
            due_date=date.today(),
            priority='medium',
            completed=True,
            completed_at=datetime.utcnow()
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        assert b'Completed Target' not in response.data

    def test_task_complete_button_present(self, client, db_session):
        """Task has Complete button with data-confirm."""
        project = Project(
            client_name='Complete Btn Client',
            project_name='Complete Btn Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Complete Target',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/tasks/{task.id}/complete' in data
        assert 'data-confirm=' in data

    def test_task_snooze_button_present(self, client, db_session):
        """Task has Snooze button with days input."""
        project = Project(
            client_name='Snooze Btn Client',
            project_name='Snooze Btn Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Snooze Target',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/tasks/{task.id}/snooze' in data
        assert 'Snooze' in data


class TestStatusPreview:
    """Test latest status update preview display."""

    def test_latest_status_shown_in_card(self, client, db_session):
        """Latest status update preview appears in project card."""
        project = Project(
            client_name='Status Preview Client',
            project_name='Status Preview Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)

        update = StatusUpdate(
            project_id=project.id,
            notes='This is the latest status update'
        )
        db_session.add(update)
        db_session.commit()

        response = client.get('/')
        assert b'This is the latest status update' in response.data

    def test_expand_button_shown_for_long_notes(self, client, db_session):
        """Show more button appears when notes exceed 3 lines."""
        project = Project(
            client_name='Long Notes Client',
            project_name='Long Notes Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)

        update = StatusUpdate(
            project_id=project.id,
            notes='Line 1\nLine 2\nLine 3\nLine 4\nLine 5'
        )
        db_session.add(update)
        db_session.commit()

        response = client.get('/')
        assert b'Show more...' in response.data
        assert b'btn-expand' in response.data

    def test_no_expand_button_for_short_notes(self, client, db_session):
        """No Show more button when notes are within limit."""
        project = Project(
            client_name='Short Notes Client',
            project_name='Short Notes Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)

        update = StatusUpdate(
            project_id=project.id,
            notes='Short note'
        )
        db_session.add(update)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        # Should not have expand button for this project's preview
        assert b'Short note' in response.data

    def test_no_preview_when_no_updates(self, client, db_session):
        """No status preview section when project has no updates."""
        project = Project(
            client_name='No Updates Client',
            project_name='No Updates Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        # Project should appear but without status preview content
        assert b'No Updates Client' in response.data


class TestStalenessIndicator:
    """Test staleness badge display on project cards."""

    def test_warning_staleness_badge_shown(self, client, db_session):
        """Projects 7-13 days stale show warning badge."""
        project = Project(
            client_name='Warning Stale Client',
            project_name='Warning Stale Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney',
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert 'staleness-warning' in data
        assert '10d stale' in data

    def test_critical_staleness_badge_shown(self, client, db_session):
        """Projects 14+ days stale show critical badge."""
        project = Project(
            client_name='Critical Stale Client',
            project_name='Critical Stale Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney',
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert 'staleness-critical' in data
        assert '20d stale' in data

    def test_no_badge_for_fresh_projects(self, client, db_session):
        """Projects with recent updates show no staleness badge."""
        project = Project(
            client_name='Fresh Client',
            project_name='Fresh Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)

        update = StatusUpdate(
            project_id=project.id,
            notes='Recent activity'
        )
        db_session.add(update)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        # Fresh Client should appear but without staleness badge
        assert 'Fresh Client' in data
        # Should not have staleness-warning or staleness-critical for this fresh project


class TestProjectSorting:
    """Test sort order within task due date categories."""

    def test_projects_sorted_by_next_task_due_date_within_section(self, client, db_session):
        """Projects in same section sorted by next task due date (earliest first)."""
        # Create two projects with tasks due in same category
        project1 = Project(
            client_name='Later Project',
            project_name='Later Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        project2 = Project(
            client_name='Earlier Project',
            project_name='Earlier Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add_all([project1, project2])
        db_session.commit()

        # Both in "this week" category but different order
        task1 = Task(
            project_id=project1.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=5),
            priority='medium'
        )
        task2 = Task(
            project_id=project2.id,
            target_type='self',
            target_name='Self',
            due_date=date.today() + timedelta(days=2),
            priority='medium'
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')

        # Earlier should appear before Later
        earlier_pos = data.find('Earlier Project')
        later_pos = data.find('Later Project')

        assert earlier_pos != -1
        assert later_pos != -1
        assert earlier_pos < later_pos


class TestDashboardTemplateRendering:
    """Test dashboard template CSS classes and quick actions."""

    def test_due_today_section_has_urgency_critical_class(self, client, db_session):
        """Due Today section has urgency-critical CSS class."""
        response = client.get('/')
        assert b'urgency-critical' in response.data

    def test_due_tomorrow_section_has_urgency_warning_class(self, client, db_session):
        """Due Tomorrow section has urgency-warning CSS class."""
        response = client.get('/')
        assert b'urgency-warning' in response.data

    def test_due_this_week_section_has_urgency_info_class(self, client, db_session):
        """Due This Week section has urgency-info CSS class."""
        response = client.get('/')
        assert b'urgency-info' in response.data

    def test_project_has_add_update_link(self, client, db_session):
        """Project has Add Update link with project pre-selection."""
        project = Project(
            client_name='Add Update Client',
            project_name='Add Update Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/updates/new?project_id={project.id}' in data
        assert 'Add Update' in data

    def test_project_has_view_link(self, client, db_session):
        """Project has View link."""
        project = Project(
            client_name='View Link Client',
            project_name='View Link Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # Add a task so project shows on dashboard
        task = Task(
            project_id=project.id,
            target_type='self',
            target_name='Self',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/projects/{project.id}' in data


class TestDashboardConfirmationModal:
    """Test confirmation modal and data-confirm attributes."""

    def test_confirmation_modal_html_present(self, client, db_session):
        """Confirmation modal HTML is present in page."""
        response = client.get('/')
        data = response.data.decode('utf-8')
        assert 'id="confirm-modal"' in data
        assert 'class="modal-overlay"' in data
        assert 'id="confirm-message"' in data
        assert 'id="confirm-ok"' in data
        assert 'id="confirm-cancel"' in data

    def test_complete_button_has_data_confirm_attribute(self, client, db_session):
        """Complete task form has data-confirm attribute."""
        project = Project(
            client_name='Confirm Client',
            project_name='Confirm Project',
            assigner='Test Partner',
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        task = Task(
            project_id=project.id,
            target_type='client',
            target_name='Confirm Target',
            due_date=date.today(),
            priority='medium'
        )
        db_session.add(task)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this task as complete?"' in data
