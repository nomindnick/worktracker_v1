"""Tests for app/routes/updates.py - Status update routes."""


class TestStatusUpdateNew:
    """Test GET/POST /updates/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New status update form returns 200 OK."""
        response = client.get('/updates/new')
        assert response.status_code == 200

    def test_new_post_stub(self, client, db_session):
        """POST to new is stubbed (returns form page)."""
        response = client.post('/updates/new', data={})
        assert response.status_code == 200
