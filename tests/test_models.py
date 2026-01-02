"""Tests for app/models.py - SQLAlchemy model definitions."""
from datetime import date, datetime, timedelta


class TestProjectModel:
    """Test Project model behavior."""

    def test_create_project_with_required_fields(self, db_session):
        """Project can be created with required fields only."""
        from app.models import Project

        project = Project(
            client_name='Test Client',
            project_name='Test Project',
            internal_deadline=date.today(),
            assigned_attorneys='Test Attorney'
        )
        db_session.add(project)
        db_session.commit()

        assert project.id is not None
        assert project.status == 'active'
        assert project.priority == 'medium'
        assert project.assigner == 'Self'

    def test_create_project_with_all_fields(self, db_session):
        """Project stores all optional fields."""
        from app.models import Project

        project = Project(
            client_name='Full Client',
            project_name='Full Project',
            matter_number='2024-999',
            hard_deadline=date.today() + timedelta(days=30),
            internal_deadline=date.today() + timedelta(days=14),
            assigner='Partner',
            assigned_attorneys='Associate',
            priority='high',
            estimated_hours=25.5,
            actual_hours=10.0
        )
        db_session.add(project)
        db_session.commit()

        assert project.matter_number == '2024-999'
        assert project.hard_deadline == date.today() + timedelta(days=30)
        assert project.estimated_hours == 25.5
        assert project.actual_hours == 10.0

    def test_project_created_at_auto_set(self, db_session):
        """Project created_at is automatically set."""
        from app.models import Project

        project = Project(
            client_name='Test',
            project_name='Test',
            internal_deadline=date.today(),
            assigned_attorneys='Test'
        )
        db_session.add(project)
        db_session.commit()

        assert project.created_at is not None
        assert isinstance(project.created_at, datetime)

    def test_project_repr(self, sample_project):
        """Project __repr__ returns readable string."""
        repr_str = repr(sample_project)

        assert 'Acme Corp' in repr_str
        assert 'Patent Application' in repr_str

    def test_project_followups_relationship(self, sample_project, sample_followup, db_session):
        """Project has access to related follow-ups."""
        assert sample_followup in sample_project.followups.all()

    def test_project_status_updates_relationship(self, sample_project_with_updates, db_session):
        """Project has access to related status updates."""
        assert sample_project_with_updates.status_updates.count() == 2

    def test_project_cascade_delete_followups(self, sample_project, sample_followup, db_session):
        """Deleting project cascades to delete follow-ups."""
        from app.models import FollowUp

        followup_id = sample_followup.id
        db_session.delete(sample_project)
        db_session.commit()

        assert FollowUp.query.get(followup_id) is None

    def test_project_cascade_delete_status_updates(self, sample_project_with_updates, db_session):
        """Deleting project cascades to delete status updates."""
        from app.models import StatusUpdate

        project_id = sample_project_with_updates.id
        db_session.delete(sample_project_with_updates)
        db_session.commit()

        assert StatusUpdate.query.filter_by(project_id=project_id).count() == 0


class TestFollowUpModel:
    """Test FollowUp model behavior."""

    def test_create_followup(self, sample_project, db_session):
        """FollowUp can be created with required fields."""
        from app.models import FollowUp

        followup = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='John Doe',
            due_date=date.today()
        )
        db_session.add(followup)
        db_session.commit()

        assert followup.id is not None
        assert followup.completed is False

    def test_followup_repr(self, sample_followup):
        """FollowUp __repr__ returns readable string."""
        repr_str = repr(sample_followup)

        assert 'John Doe' in repr_str

    def test_followup_project_backref(self, sample_followup):
        """FollowUp has access to parent project via backref."""
        assert sample_followup.project is not None
        assert sample_followup.project.client_name == 'Acme Corp'


class TestStatusUpdateModel:
    """Test StatusUpdate model behavior."""

    def test_create_status_update(self, sample_project, db_session):
        """StatusUpdate can be created with required fields."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes='Work in progress'
        )
        db_session.add(update)
        db_session.commit()

        assert update.id is not None
        assert update.created_at is not None

    def test_status_update_repr(self, sample_project, db_session):
        """StatusUpdate __repr__ returns readable string."""
        from app.models import StatusUpdate

        update = StatusUpdate(project_id=sample_project.id, notes='Test')
        db_session.add(update)
        db_session.commit()

        repr_str = repr(update)
        assert str(update.id) in repr_str
        assert str(sample_project.id) in repr_str

    def test_status_update_project_backref(self, sample_project_with_updates):
        """StatusUpdate has access to parent project via backref."""
        update = sample_project_with_updates.status_updates.first()

        assert update.project is not None
        assert update.project.id == sample_project_with_updates.id


class TestProjectStalenessProperties:
    """Test Project staleness calculation properties."""

    def test_last_update_date_with_updates(self, sample_project_with_updates, db_session):
        """last_update_date returns most recent update datetime."""
        last_date = sample_project_with_updates.last_update_date
        assert last_date is not None
        assert isinstance(last_date, datetime)

    def test_last_update_date_without_updates(self, sample_project, db_session):
        """last_update_date returns None when no updates exist."""
        assert sample_project.last_update_date is None

    def test_days_since_update_with_updates(self, sample_project_with_updates, db_session):
        """days_since_update calculates from last update."""
        days = sample_project_with_updates.days_since_update
        assert days == 0  # Just created

    def test_days_since_update_without_updates(self, sample_project, db_session):
        """days_since_update calculates from created_at when no updates."""
        days = sample_project.days_since_update
        assert days == 0  # Just created

    def test_staleness_level_ok(self, sample_project, db_session):
        """staleness_level returns 'ok' for <7 days."""
        assert sample_project.staleness_level == 'ok'

    def test_staleness_level_warning(self, sample_project, db_session):
        """staleness_level returns 'warning' for 7-13 days."""
        sample_project.created_at = datetime.utcnow() - timedelta(days=10)
        db_session.commit()
        assert sample_project.staleness_level == 'warning'

    def test_staleness_level_critical(self, sample_project, db_session):
        """staleness_level returns 'critical' for 14+ days."""
        sample_project.created_at = datetime.utcnow() - timedelta(days=14)
        db_session.commit()
        assert sample_project.staleness_level == 'critical'


class TestProjectFollowupMethods:
    """Test Project follow-up query methods."""

    def test_get_pending_followups(self, sample_project, db_session):
        """get_pending_followups returns all pending follow-ups ordered by due_date."""
        from app.models import FollowUp

        # Create multiple follow-ups with different due dates
        followup1 = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today() + timedelta(days=3)
        )
        followup2 = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1)
        )
        followup3 = FollowUp(
            project_id=sample_project.id,
            target_type='other',
            target_name='Person C',
            due_date=date.today() + timedelta(days=2),
            completed=True
        )
        db_session.add_all([followup1, followup2, followup3])
        db_session.commit()

        pending = sample_project.get_pending_followups()
        assert len(pending) == 2
        assert pending[0].target_name == 'Person B'  # earliest due_date first
        assert pending[1].target_name == 'Person A'

    def test_get_pending_followups_empty(self, sample_project, db_session):
        """get_pending_followups returns empty list when no pending follow-ups."""
        pending = sample_project.get_pending_followups()
        assert pending == []

    def test_get_completed_followups(self, sample_project, db_session):
        """get_completed_followups returns all completed follow-ups ordered by completed_at desc."""
        from app.models import FollowUp

        # Create multiple completed follow-ups
        followup1 = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow() - timedelta(hours=2)
        )
        followup2 = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow() - timedelta(hours=1)
        )
        followup3 = FollowUp(
            project_id=sample_project.id,
            target_type='other',
            target_name='Person C',
            due_date=date.today(),
            completed=False
        )
        db_session.add_all([followup1, followup2, followup3])
        db_session.commit()

        completed = sample_project.get_completed_followups()
        assert len(completed) == 2
        assert completed[0].target_name == 'Person B'  # most recent completion first
        assert completed[1].target_name == 'Person A'

    def test_get_completed_followups_empty(self, sample_project, db_session):
        """get_completed_followups returns empty list when no completed follow-ups."""
        completed = sample_project.get_completed_followups()
        assert completed == []

    def test_pending_followup_count(self, sample_project, db_session):
        """pending_followup_count returns count of pending follow-ups."""
        from app.models import FollowUp

        assert sample_project.pending_followup_count == 0

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
            due_date=date.today(),
            completed=True
        )
        db_session.add_all([followup1, followup2])
        db_session.commit()

        assert sample_project.pending_followup_count == 1

    def test_next_followup(self, sample_project, db_session):
        """next_followup returns the earliest pending follow-up."""
        from app.models import FollowUp

        assert sample_project.next_followup is None

        followup1 = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today() + timedelta(days=3)
        )
        followup2 = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1)
        )
        db_session.add_all([followup1, followup2])
        db_session.commit()

        next_followup = sample_project.next_followup
        assert next_followup is not None
        assert next_followup.target_name == 'Person B'

    def test_next_followup_ignores_completed(self, sample_project, db_session):
        """next_followup ignores completed follow-ups."""
        from app.models import FollowUp

        followup1 = FollowUp(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today(),
            completed=True
        )
        followup2 = FollowUp(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=2)
        )
        db_session.add_all([followup1, followup2])
        db_session.commit()

        next_followup = sample_project.next_followup
        assert next_followup.target_name == 'Person B'


class TestProjectEffectiveDeadline:
    """Test Project.effective_deadline property."""

    def test_returns_internal_when_both_set(self, db_session):
        """Returns internal_deadline when both deadlines exist."""
        from app.models import Project

        project = Project(
            client_name='Test',
            project_name='Test',
            internal_deadline=date.today() + timedelta(days=7),
            hard_deadline=date.today() + timedelta(days=14),
            assigned_attorneys='Test'
        )
        db_session.add(project)
        db_session.commit()

        assert project.effective_deadline == date.today() + timedelta(days=7)

    def test_returns_internal_when_only_internal_set(self, sample_project, db_session):
        """Returns internal_deadline when only it exists."""
        # sample_project has only internal_deadline set
        assert sample_project.effective_deadline == sample_project.internal_deadline


class TestProjectDeadlineType:
    """Test Project.deadline_type property."""

    def test_returns_internal_when_internal_set(self, sample_project, db_session):
        """Returns 'internal' when internal_deadline exists."""
        assert sample_project.deadline_type == 'internal'

    def test_returns_internal_when_both_set(self, db_session):
        """Returns 'internal' when both deadlines exist (internal takes precedence)."""
        from app.models import Project

        project = Project(
            client_name='Test',
            project_name='Test',
            internal_deadline=date.today(),
            hard_deadline=date.today() + timedelta(days=14),
            assigned_attorneys='Test'
        )
        db_session.add(project)
        db_session.commit()

        assert project.deadline_type == 'internal'


class TestProjectLatestStatusUpdate:
    """Test Project.latest_status_update property."""

    def test_returns_most_recent_update(self, sample_project, db_session):
        """Returns the most recent StatusUpdate."""
        from app.models import StatusUpdate

        update1 = StatusUpdate(
            project_id=sample_project.id,
            notes='First update'
        )
        db_session.add(update1)
        db_session.commit()

        update2 = StatusUpdate(
            project_id=sample_project.id,
            notes='Second update'
        )
        db_session.add(update2)
        db_session.commit()

        latest = sample_project.latest_status_update
        assert latest is not None
        assert latest.notes == 'Second update'

    def test_returns_none_when_no_updates(self, sample_project, db_session):
        """Returns None when project has no updates."""
        assert sample_project.latest_status_update is None


class TestProjectStatusPreview:
    """Test Project.get_status_preview() method."""

    def test_returns_first_3_lines(self, sample_project, db_session):
        """Returns first 3 lines of latest status notes."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes='Line 1\nLine 2\nLine 3\nLine 4\nLine 5'
        )
        db_session.add(update)
        db_session.commit()

        preview = sample_project.get_status_preview()
        assert preview is not None
        assert preview['text'] == 'Line 1\nLine 2\nLine 3'

    def test_has_more_true_when_exceeds_limit(self, sample_project, db_session):
        """has_more is True when notes exceed line limit."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes='Line 1\nLine 2\nLine 3\nLine 4'
        )
        db_session.add(update)
        db_session.commit()

        preview = sample_project.get_status_preview()
        assert preview['has_more'] is True
        assert preview['full_text'] == 'Line 1\nLine 2\nLine 3\nLine 4'

    def test_has_more_false_when_within_limit(self, sample_project, db_session):
        """has_more is False when notes are within limit."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes='Line 1\nLine 2'
        )
        db_session.add(update)
        db_session.commit()

        preview = sample_project.get_status_preview()
        assert preview['has_more'] is False
        assert preview['full_text'] is None

    def test_returns_none_when_no_updates(self, sample_project, db_session):
        """Returns None when project has no updates."""
        assert sample_project.get_status_preview() is None

    def test_custom_max_lines(self, sample_project, db_session):
        """Respects custom max_lines parameter."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes='Line 1\nLine 2\nLine 3\nLine 4\nLine 5'
        )
        db_session.add(update)
        db_session.commit()

        preview = sample_project.get_status_preview(max_lines=2)
        assert preview['text'] == 'Line 1\nLine 2'
        assert preview['has_more'] is True

    def test_handles_empty_notes(self, sample_project, db_session):
        """Returns None when notes is empty string."""
        from app.models import StatusUpdate

        update = StatusUpdate(
            project_id=sample_project.id,
            notes=''
        )
        db_session.add(update)
        db_session.commit()

        # Empty notes should return None
        assert sample_project.get_status_preview() is None
