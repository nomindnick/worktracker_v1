"""Tests for app/routes/dashboard.py - Dashboard routes."""

from datetime import date, datetime, timedelta
from app.models import Project, FollowUp, StatusUpdate


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
        # Should have the new section headings
        assert b'Due Today' in response.data
        assert b'Due Tomorrow' in response.data
        assert b'Due in 2-5 Days' in response.data
        assert b'Due in 6-14 Days' in response.data


class TestDashboardDeadlineCategories:
    """Test project categorization by deadline proximity."""

    def test_project_due_today_appears_in_due_today_section(self, client, db_session):
        """Project with internal_deadline == today appears in Due Today section."""
        project = Project(
            client_name='Due Today Client',
            project_name='Due Today Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Due Today Client' in response.data

    def test_project_due_tomorrow_appears_in_due_tomorrow_section(self, client, db_session):
        """Project with deadline == tomorrow appears in Due Tomorrow section."""
        project = Project(
            client_name='Due Tomorrow Client',
            project_name='Due Tomorrow Project',
            internal_deadline=date.today() + timedelta(days=1),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Due Tomorrow Client' in response.data

    def test_project_due_in_3_days_appears_in_next_5_days_section(self, client, db_session):
        """Project with deadline in 3 days appears in 2-5 days section."""
        project = Project(
            client_name='Due In 3 Days Client',
            project_name='Due In 3 Days Project',
            internal_deadline=date.today() + timedelta(days=3),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Due In 3 Days Client' in response.data

    def test_project_due_in_10_days_appears_in_next_2_weeks_section(self, client, db_session):
        """Project with deadline in 10 days appears in 6-14 days section."""
        project = Project(
            client_name='Due In 10 Days Client',
            project_name='Due In 10 Days Project',
            internal_deadline=date.today() + timedelta(days=10),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Due In 10 Days Client' in response.data

    def test_project_due_in_20_days_not_shown(self, client, db_session):
        """Projects with deadline > 14 days are not shown on dashboard."""
        project = Project(
            client_name='Due In 20 Days Client',
            project_name='Due In 20 Days Project',
            internal_deadline=date.today() + timedelta(days=20),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Due In 20 Days Client' not in response.data

    def test_overdue_project_appears_in_due_today(self, client, db_session):
        """Projects with past deadlines appear in Due Today section."""
        project = Project(
            client_name='Overdue Client',
            project_name='Overdue Project',
            internal_deadline=date.today() - timedelta(days=3),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Overdue Client' in response.data

    def test_archived_project_excluded(self, client, db_session):
        """Archived projects don't appear on dashboard."""
        project = Project(
            client_name='Archived Client',
            project_name='Archived Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney',
            status='archived'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Archived Client' not in response.data

    def test_boundary_day_2(self, client, db_session):
        """Project due in 2 days appears in 2-5 days section."""
        project = Project(
            client_name='Day 2 Client',
            project_name='Day 2 Project',
            internal_deadline=date.today() + timedelta(days=2),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Day 2 Client' in response.data

    def test_boundary_day_5(self, client, db_session):
        """Project due in 5 days appears in 2-5 days section."""
        project = Project(
            client_name='Day 5 Client',
            project_name='Day 5 Project',
            internal_deadline=date.today() + timedelta(days=5),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Day 5 Client' in response.data

    def test_boundary_day_6(self, client, db_session):
        """Project due in 6 days appears in 6-14 days section."""
        project = Project(
            client_name='Day 6 Client',
            project_name='Day 6 Project',
            internal_deadline=date.today() + timedelta(days=6),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Day 6 Client' in response.data

    def test_boundary_day_14(self, client, db_session):
        """Project due in 14 days appears in 6-14 days section."""
        project = Project(
            client_name='Day 14 Client',
            project_name='Day 14 Project',
            internal_deadline=date.today() + timedelta(days=14),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Day 14 Client' in response.data

    def test_boundary_day_15_not_shown(self, client, db_session):
        """Project due in 15 days is not shown."""
        project = Project(
            client_name='Day 15 Client',
            project_name='Day 15 Project',
            internal_deadline=date.today() + timedelta(days=15),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        assert b'Day 15 Client' not in response.data


class TestDeadlineResolution:
    """Test effective_deadline logic (internal takes precedence)."""

    def test_internal_deadline_used_when_both_exist(self, client, db_session):
        """When both deadlines exist, internal_deadline determines category."""
        project = Project(
            client_name='Both Deadlines Client',
            project_name='Both Deadlines Project',
            internal_deadline=date.today(),  # Due today
            hard_deadline=date.today() + timedelta(days=10),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        response = client.get('/')
        # Should appear in Due Today section (uses internal_deadline)
        assert b'Both Deadlines Client' in response.data

    def test_hard_deadline_shown_with_indicator(self, client, db_session):
        """Hard deadline projects show (hard) indicator."""
        project = Project(
            client_name='Hard Only Client',
            project_name='Hard Only Project',
            internal_deadline=date.today() + timedelta(days=30),  # Far future
            hard_deadline=date.today() + timedelta(days=3),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        # This project won't show because internal_deadline is beyond 14 days
        response = client.get('/')
        assert b'Hard Only Client' not in response.data


class TestInlineFollowups:
    """Test follow-ups displayed inline within project cards."""

    def test_pending_followups_shown_in_project_card(self, client, db_session):
        """Pending follow-ups appear within their project's card."""
        project = Project(
            client_name='Followup Client',
            project_name='Followup Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Inline Target',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        assert b'Inline Target' in response.data

    def test_overdue_followup_has_overdue_styling(self, client, db_session):
        """Overdue follow-ups have CSS class for visual distinction."""
        project = Project(
            client_name='Overdue FU Client',
            project_name='Overdue FU Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Overdue Target',
            due_date=date.today() - timedelta(days=3)
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        assert b'followup-overdue' in response.data

    def test_followup_due_today_has_due_today_styling(self, client, db_session):
        """Follow-ups due today have CSS class for visual distinction."""
        project = Project(
            client_name='Today FU Client',
            project_name='Today FU Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Today Target',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        assert b'followup-due-today' in response.data

    def test_completed_followups_not_shown(self, client, db_session):
        """Completed follow-ups are not shown in project cards."""
        project = Project(
            client_name='Completed FU Client',
            project_name='Completed FU Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Completed Target',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        assert b'Completed Target' not in response.data

    def test_followup_complete_button_present(self, client, db_session):
        """Follow-up has Complete button with data-confirm."""
        project = Project(
            client_name='Complete Btn Client',
            project_name='Complete Btn Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Complete Target',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/followups/{followup.id}/complete' in data
        assert 'data-confirm=' in data

    def test_followup_snooze_button_present(self, client, db_session):
        """Follow-up has Snooze button with days input."""
        project = Project(
            client_name='Snooze Btn Client',
            project_name='Snooze Btn Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Snooze Target',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert f'/followups/{followup.id}/snooze' in data
        assert 'Snooze' in data


class TestStatusPreview:
    """Test latest status update preview display."""

    def test_latest_status_shown_in_card(self, client, db_session):
        """Latest status update preview appears in project card."""
        project = Project(
            client_name='Status Preview Client',
            project_name='Status Preview Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney',
            created_at=datetime.utcnow() - timedelta(days=10)
        )
        db_session.add(project)
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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney',
            created_at=datetime.utcnow() - timedelta(days=20)
        )
        db_session.add(project)
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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

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
    """Test sort order within deadline categories."""

    def test_projects_sorted_by_deadline_within_section(self, client, db_session):
        """Projects in same section sorted by deadline (earliest first)."""
        # Create two projects due in 2-5 days
        project1 = Project(
            client_name='Later Project',
            project_name='Later Project',
            internal_deadline=date.today() + timedelta(days=5),
            assigned_attorneys='Test Attorney'
        )
        project2 = Project(
            client_name='Earlier Project',
            project_name='Earlier Project',
            internal_deadline=date.today() + timedelta(days=2),
            assigned_attorneys='Test Attorney'
        )
        db_session.add_all([project1, project2])
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

    def test_due_next_5_days_section_has_urgency_info_class(self, client, db_session):
        """Due in 2-5 Days section has urgency-info CSS class."""
        response = client.get('/')
        assert b'urgency-info' in response.data

    def test_project_has_add_update_link(self, client, db_session):
        """Project has Add Update link with project pre-selection."""
        project = Project(
            client_name='Add Update Client',
            project_name='Add Update Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
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
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
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
        """Complete follow-up form has data-confirm attribute."""
        project = Project(
            client_name='Confirm Client',
            project_name='Confirm Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        followup = FollowUp(
            project_id=project.id,
            target_type='client',
            target_name='Confirm Target',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        response = client.get('/')
        data = response.data.decode('utf-8')
        assert 'data-confirm="Mark this follow-up as complete?"' in data
