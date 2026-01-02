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
            client_number='CLT-001',
            assigner='Partner',
            assigned_attorneys='Associate',
            priority='high',
            estimated_hours=25.5,
            actual_hours=10.0
        )
        db_session.add(project)
        db_session.commit()

        assert project.matter_number == '2024-999'
        assert project.client_number == 'CLT-001'
        assert project.estimated_hours == 25.5
        assert project.actual_hours == 10.0

    def test_project_created_at_auto_set(self, db_session):
        """Project created_at is automatically set."""
        from app.models import Project

        project = Project(
            client_name='Test',
            project_name='Test',
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

    def test_project_tasks_relationship(self, sample_project, sample_task, db_session):
        """Project has access to related tasks."""
        assert sample_task in sample_project.tasks.all()

    def test_project_status_updates_relationship(self, sample_project_with_updates, db_session):
        """Project has access to related status updates."""
        assert sample_project_with_updates.status_updates.count() == 2

    def test_project_cascade_delete_tasks(self, sample_project, sample_task, db_session):
        """Deleting project cascades to delete tasks."""
        from app.models import Task

        task_id = sample_task.id
        db_session.delete(sample_project)
        db_session.commit()

        assert Task.query.get(task_id) is None

    def test_project_cascade_delete_milestones(self, sample_project, sample_milestone, db_session):
        """Deleting project cascades to delete milestones."""
        from app.models import Milestone

        milestone_id = sample_milestone.id
        db_session.delete(sample_project)
        db_session.commit()

        assert Milestone.query.get(milestone_id) is None

    def test_project_cascade_delete_status_updates(self, sample_project_with_updates, db_session):
        """Deleting project cascades to delete status updates."""
        from app.models import StatusUpdate

        project_id = sample_project_with_updates.id
        db_session.delete(sample_project_with_updates)
        db_session.commit()

        assert StatusUpdate.query.filter_by(project_id=project_id).count() == 0


class TestTaskModel:
    """Test Task model behavior."""

    def test_create_task(self, sample_project, db_session):
        """Task can be created with required fields."""
        from app.models import Task

        task = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='John Doe',
            due_date=date.today()
        )
        db_session.add(task)
        db_session.commit()

        assert task.id is not None
        assert task.completed is False
        assert task.priority == 'medium'

    def test_create_task_with_all_target_types(self, sample_project, db_session):
        """Task accepts all valid target_type values."""
        from app.models import Task

        target_types = ['self', 'associate', 'client', 'opposing_counsel', 'assigning_attorney']
        for idx, target_type in enumerate(target_types):
            task = Task(
                project_id=sample_project.id,
                target_type=target_type,
                target_name=f'Person {idx}',
                due_date=date.today() + timedelta(days=idx)
            )
            db_session.add(task)
        db_session.commit()

        tasks = Task.query.filter_by(project_id=sample_project.id).all()
        assert len(tasks) == 5
        for task, expected_type in zip(tasks, target_types):
            assert task.target_type == expected_type

    def test_create_task_with_priority(self, sample_project, db_session):
        """Task can be created with priority field."""
        from app.models import Task

        task = Task(
            project_id=sample_project.id,
            target_type='self',
            target_name='Self Task',
            due_date=date.today(),
            priority='high'
        )
        db_session.add(task)
        db_session.commit()

        assert task.priority == 'high'

    def test_create_task_with_description(self, sample_project, db_session):
        """Task can be created with description field."""
        from app.models import Task

        task = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Client Name',
            due_date=date.today(),
            description='This is a detailed description of the task.'
        )
        db_session.add(task)
        db_session.commit()

        assert task.description == 'This is a detailed description of the task.'

    def test_task_repr(self, sample_task):
        """Task __repr__ returns readable string."""
        repr_str = repr(sample_task)

        assert 'John Doe' in repr_str

    def test_task_project_backref(self, sample_task):
        """Task has access to parent project via backref."""
        assert sample_task.project is not None
        assert sample_task.project.client_name == 'Acme Corp'


class TestMilestoneModel:
    """Test Milestone model behavior."""

    def test_create_milestone(self, sample_project, db_session):
        """Milestone can be created with required fields."""
        from app.models import Milestone

        milestone = Milestone(
            project_id=sample_project.id,
            name='Discovery Deadline',
            date=date.today() + timedelta(days=30)
        )
        db_session.add(milestone)
        db_session.commit()

        assert milestone.id is not None
        assert milestone.completed is False

    def test_create_milestone_with_all_fields(self, sample_project, db_session):
        """Milestone stores all optional fields."""
        from app.models import Milestone

        milestone = Milestone(
            project_id=sample_project.id,
            name='Trial Date',
            description='Final trial hearing scheduled',
            date=date.today() + timedelta(days=90),
            completed=False
        )
        db_session.add(milestone)
        db_session.commit()

        assert milestone.name == 'Trial Date'
        assert milestone.description == 'Final trial hearing scheduled'
        assert milestone.date == date.today() + timedelta(days=90)

    def test_milestone_created_at_auto_set(self, sample_project, db_session):
        """Milestone created_at is automatically set."""
        from app.models import Milestone

        milestone = Milestone(
            project_id=sample_project.id,
            name='Test Milestone',
            date=date.today()
        )
        db_session.add(milestone)
        db_session.commit()

        assert milestone.created_at is not None
        assert isinstance(milestone.created_at, datetime)

    def test_milestone_repr(self, sample_milestone):
        """Milestone __repr__ returns readable string."""
        repr_str = repr(sample_milestone)

        assert 'Initial Filing' in repr_str
        assert str(sample_milestone.project_id) in repr_str

    def test_milestone_project_backref(self, sample_milestone):
        """Milestone has access to parent project via backref."""
        assert sample_milestone.project is not None
        assert sample_milestone.project.client_name == 'Acme Corp'


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


class TestProjectTaskMethods:
    """Test Project task query methods."""

    def test_get_pending_tasks(self, sample_project, db_session):
        """get_pending_tasks returns all pending tasks ordered by due_date."""
        from app.models import Task

        # Create multiple tasks with different due dates
        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today() + timedelta(days=3)
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1)
        )
        task3 = Task(
            project_id=sample_project.id,
            target_type='self',
            target_name='Person C',
            due_date=date.today() + timedelta(days=2),
            completed=True
        )
        db_session.add_all([task1, task2, task3])
        db_session.commit()

        pending = sample_project.get_pending_tasks()
        assert len(pending) == 2
        assert pending[0].target_name == 'Person B'  # earliest due_date first
        assert pending[1].target_name == 'Person A'

    def test_get_pending_tasks_empty(self, sample_project, db_session):
        """get_pending_tasks returns empty list when no pending tasks."""
        pending = sample_project.get_pending_tasks()
        assert pending == []

    def test_get_completed_tasks(self, sample_project, db_session):
        """get_completed_tasks returns all completed tasks ordered by completed_at desc."""
        from app.models import Task

        # Create multiple completed tasks
        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow() - timedelta(hours=2)
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today(),
            completed=True,
            completed_at=datetime.utcnow() - timedelta(hours=1)
        )
        task3 = Task(
            project_id=sample_project.id,
            target_type='self',
            target_name='Person C',
            due_date=date.today(),
            completed=False
        )
        db_session.add_all([task1, task2, task3])
        db_session.commit()

        completed = sample_project.get_completed_tasks()
        assert len(completed) == 2
        assert completed[0].target_name == 'Person B'  # most recent completion first
        assert completed[1].target_name == 'Person A'

    def test_get_completed_tasks_empty(self, sample_project, db_session):
        """get_completed_tasks returns empty list when no completed tasks."""
        completed = sample_project.get_completed_tasks()
        assert completed == []

    def test_pending_task_count(self, sample_project, db_session):
        """pending_task_count returns count of pending tasks."""
        from app.models import Task

        assert sample_project.pending_task_count == 0

        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today()
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today(),
            completed=True
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        assert sample_project.pending_task_count == 1

    def test_next_task(self, sample_project, db_session):
        """next_task returns the earliest pending task."""
        from app.models import Task

        assert sample_project.next_task is None

        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today() + timedelta(days=3)
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=1)
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        next_task = sample_project.next_task
        assert next_task is not None
        assert next_task.target_name == 'Person B'

    def test_next_task_ignores_completed(self, sample_project, db_session):
        """next_task ignores completed tasks."""
        from app.models import Task

        task1 = Task(
            project_id=sample_project.id,
            target_type='associate',
            target_name='Person A',
            due_date=date.today(),
            completed=True
        )
        task2 = Task(
            project_id=sample_project.id,
            target_type='client',
            target_name='Person B',
            due_date=date.today() + timedelta(days=2)
        )
        db_session.add_all([task1, task2])
        db_session.commit()

        next_task = sample_project.next_task
        assert next_task.target_name == 'Person B'


class TestProjectMilestoneMethods:
    """Test Project milestone query methods."""

    def test_get_pending_milestones(self, sample_project, db_session):
        """get_pending_milestones returns all pending milestones ordered by date."""
        from app.models import Milestone

        # Create multiple milestones with different dates
        milestone1 = Milestone(
            project_id=sample_project.id,
            name='Milestone A',
            date=date.today() + timedelta(days=30)
        )
        milestone2 = Milestone(
            project_id=sample_project.id,
            name='Milestone B',
            date=date.today() + timedelta(days=10)
        )
        milestone3 = Milestone(
            project_id=sample_project.id,
            name='Milestone C',
            date=date.today() + timedelta(days=20),
            completed=True
        )
        db_session.add_all([milestone1, milestone2, milestone3])
        db_session.commit()

        pending = sample_project.get_pending_milestones()
        assert len(pending) == 2
        assert pending[0].name == 'Milestone B'  # earliest date first
        assert pending[1].name == 'Milestone A'

    def test_get_pending_milestones_empty(self, sample_project, db_session):
        """get_pending_milestones returns empty list when no pending milestones."""
        pending = sample_project.get_pending_milestones()
        assert pending == []

    def test_get_completed_milestones(self, sample_project, db_session):
        """get_completed_milestones returns all completed milestones ordered by date desc."""
        from app.models import Milestone

        # Create multiple completed milestones
        milestone1 = Milestone(
            project_id=sample_project.id,
            name='Milestone A',
            date=date.today() - timedelta(days=10),
            completed=True
        )
        milestone2 = Milestone(
            project_id=sample_project.id,
            name='Milestone B',
            date=date.today() - timedelta(days=5),
            completed=True
        )
        milestone3 = Milestone(
            project_id=sample_project.id,
            name='Milestone C',
            date=date.today() + timedelta(days=20),
            completed=False
        )
        db_session.add_all([milestone1, milestone2, milestone3])
        db_session.commit()

        completed = sample_project.get_completed_milestones()
        assert len(completed) == 2
        assert completed[0].name == 'Milestone B'  # most recent date first
        assert completed[1].name == 'Milestone A'

    def test_get_completed_milestones_empty(self, sample_project, db_session):
        """get_completed_milestones returns empty list when no completed milestones."""
        completed = sample_project.get_completed_milestones()
        assert completed == []

    def test_next_milestone(self, sample_project, db_session):
        """next_milestone returns the earliest pending milestone."""
        from app.models import Milestone

        assert sample_project.next_milestone is None

        milestone1 = Milestone(
            project_id=sample_project.id,
            name='Milestone A',
            date=date.today() + timedelta(days=30)
        )
        milestone2 = Milestone(
            project_id=sample_project.id,
            name='Milestone B',
            date=date.today() + timedelta(days=10)
        )
        db_session.add_all([milestone1, milestone2])
        db_session.commit()

        next_milestone = sample_project.next_milestone
        assert next_milestone is not None
        assert next_milestone.name == 'Milestone B'

    def test_next_milestone_ignores_completed(self, sample_project, db_session):
        """next_milestone ignores completed milestones."""
        from app.models import Milestone

        milestone1 = Milestone(
            project_id=sample_project.id,
            name='Milestone A',
            date=date.today() + timedelta(days=5),
            completed=True
        )
        milestone2 = Milestone(
            project_id=sample_project.id,
            name='Milestone B',
            date=date.today() + timedelta(days=15)
        )
        db_session.add_all([milestone1, milestone2])
        db_session.commit()

        next_milestone = sample_project.next_milestone
        assert next_milestone.name == 'Milestone B'


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
