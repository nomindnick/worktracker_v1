"""Tests for app/__init__.py - app factory and CLI commands."""
from flask import Flask


class TestCreateApp:
    """Test application factory."""

    def test_create_app_returns_flask_instance(self, app):
        """create_app returns a Flask application instance."""
        assert isinstance(app, Flask)

    def test_app_has_secret_key(self, app):
        """Application has a secret key configured."""
        assert app.config['SECRET_KEY'] is not None

    def test_app_has_database_uri(self, app):
        """Application has database URI configured."""
        assert 'SQLALCHEMY_DATABASE_URI' in app.config

    def test_dashboard_blueprint_registered(self, app):
        """Dashboard blueprint is registered at root URL."""
        assert 'dashboard' in app.blueprints

    def test_projects_blueprint_registered(self, app):
        """Projects blueprint is registered with /projects prefix."""
        assert 'projects' in app.blueprints

    def test_followups_blueprint_registered(self, app):
        """Followups blueprint is registered with /followups prefix."""
        assert 'followups' in app.blueprints

    def test_updates_blueprint_registered(self, app):
        """Updates blueprint is registered with /updates prefix."""
        assert 'updates' in app.blueprints

    def test_export_blueprint_registered(self, app):
        """Export blueprint is registered with /export prefix."""
        assert 'export' in app.blueprints


class TestInitDbCommand:
    """Test init-db CLI command."""

    def test_init_db_command_exists(self, runner):
        """init-db command is registered."""
        result = runner.invoke(args=['init-db'])
        assert result.exit_code == 0

    def test_init_db_creates_tables(self, runner, app):
        """init-db command creates database tables."""
        result = runner.invoke(args=['init-db'])

        assert 'Database initialized' in result.output

        from app import db
        with app.app_context():
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            assert 'projects' in tables
            assert 'followups' in tables
            assert 'status_updates' in tables
