"""Tests for config.py - configuration loading."""
import os
import importlib


class TestConfig:
    """Test configuration class behavior."""

    def test_default_secret_key(self, monkeypatch):
        """Config uses default secret key when env var not set."""
        monkeypatch.delenv('SECRET_KEY', raising=False)
        import config
        importlib.reload(config)

        assert config.Config.SECRET_KEY == 'dev-secret-key-change-in-production'

    def test_custom_secret_key(self, monkeypatch):
        """Config uses SECRET_KEY from environment."""
        monkeypatch.setenv('SECRET_KEY', 'my-custom-key')
        import config
        importlib.reload(config)

        assert config.Config.SECRET_KEY == 'my-custom-key'

    def test_default_data_dir(self, monkeypatch):
        """Config uses default data directory when env var not set."""
        monkeypatch.delenv('WORKLIST_DATA_DIR', raising=False)
        import config
        importlib.reload(config)

        assert 'data' in str(config.DATA_DIR)

    def test_custom_data_dir(self, monkeypatch, tmp_path):
        """Config uses WORKLIST_DATA_DIR from environment."""
        custom_dir = tmp_path / 'custom_data'
        monkeypatch.setenv('WORKLIST_DATA_DIR', str(custom_dir))
        import config
        importlib.reload(config)

        assert str(config.DATA_DIR) == str(custom_dir)
        assert custom_dir.exists()

    def test_database_uri_format(self):
        """Database URI is properly formatted SQLite path."""
        import config

        assert config.Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///')
        assert 'worklist.db' in config.Config.SQLALCHEMY_DATABASE_URI

    def test_track_modifications_disabled(self):
        """SQLAlchemy track modifications is disabled for performance."""
        import config

        assert config.Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
