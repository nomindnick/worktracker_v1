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
