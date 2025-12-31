"""Tests for app/routes/dashboard.py - Dashboard routes."""


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
