"""Shared test fixtures for the Legal Work Tracker application."""
import os
import pytest
from datetime import date, datetime, timedelta

# Set test environment before importing app
os.environ['WORKLIST_DATA_DIR'] = '/tmp/test_worklist'


@pytest.fixture(scope='session')
def app():
    """Create application for testing with in-memory SQLite database."""
    from app import create_app, db

    class TestConfig:
        TESTING = True
        SECRET_KEY = 'test-secret-key'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False

    app = create_app()
    app.config.from_object(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client for making HTTP requests."""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Provide a clean database session for each test."""
    from app import db

    with app.app_context():
        db.create_all()
        yield db.session
        db.session.rollback()
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()


@pytest.fixture
def sample_project(db_session):
    """Create a sample project for testing."""
    from app.models import Project

    project = Project(
        client_name='Acme Corp',
        project_name='Patent Application',
        matter_number='2024-001',
        hard_deadline=date.today() + timedelta(days=30),
        internal_deadline=date.today() + timedelta(days=14),
        assigner='Partner Smith',
        assigned_attorneys='Associate Jones',
        priority='high',
        estimated_hours=40.0
    )
    db_session.add(project)
    db_session.commit()
    return project


@pytest.fixture
def sample_project_with_updates(sample_project, db_session):
    """Create a project with status updates for testing."""
    from app.models import StatusUpdate

    update1 = StatusUpdate(
        project_id=sample_project.id,
        notes='Initial research completed'
    )
    update2 = StatusUpdate(
        project_id=sample_project.id,
        notes='Draft in progress'
    )
    db_session.add_all([update1, update2])
    db_session.commit()
    return sample_project


@pytest.fixture
def sample_followup(sample_project, db_session):
    """Create a sample follow-up for testing."""
    from app.models import FollowUp

    followup = FollowUp(
        project_id=sample_project.id,
        target_type='client',
        target_name='John Doe',
        due_date=date.today() + timedelta(days=3),
        notes='Follow up on document review'
    )
    db_session.add(followup)
    db_session.commit()
    return followup


@pytest.fixture
def runner(app):
    """Create CLI runner for testing CLI commands."""
    return app.test_cli_runner()
