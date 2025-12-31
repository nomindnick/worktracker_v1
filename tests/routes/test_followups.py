"""Tests for app/routes/followups.py - Follow-up routes."""


class TestFollowUpList:
    """Test GET /followups/ route."""

    def test_list_returns_200(self, client, db_session):
        """Follow-up list returns 200 OK."""
        response = client.get('/followups/')
        assert response.status_code == 200

    def test_list_shows_pending_followups(self, client, sample_followup, db_session):
        """Follow-up list shows pending (incomplete) follow-ups."""
        response = client.get('/followups/')

        assert b'John Doe' in response.data

    def test_list_excludes_completed_followups(self, client, sample_followup, db_session):
        """Follow-up list excludes completed follow-ups."""
        sample_followup.completed = True
        db_session.commit()

        response = client.get('/followups/')

        assert b'John Doe' not in response.data


class TestFollowUpNew:
    """Test GET/POST /followups/new routes."""

    def test_new_get_returns_200(self, client, db_session):
        """New follow-up form returns 200 OK."""
        response = client.get('/followups/new')
        assert response.status_code == 200

    def test_new_post_stub(self, client, db_session):
        """POST to new is stubbed (returns form page)."""
        response = client.post('/followups/new', data={})
        assert response.status_code == 200


class TestFollowUpComplete:
    """Test POST /followups/<id>/complete route."""

    def test_complete_returns_redirect(self, client, sample_followup, db_session):
        """Complete redirects (stub behavior)."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_complete_404_for_missing_followup(self, client, db_session):
        """Complete returns 404 for non-existent follow-up."""
        response = client.post('/followups/99999/complete')
        assert response.status_code == 404

    def test_complete_redirects_to_referrer(self, client, sample_followup, db_session):
        """Complete redirects to referrer if available."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               headers={'Referer': '/projects/1'},
                               follow_redirects=False)
        assert response.location == '/projects/1'

    def test_complete_redirects_to_dashboard_without_referrer(self, client, sample_followup, db_session):
        """Complete redirects to dashboard when no referrer."""
        response = client.post(f'/followups/{sample_followup.id}/complete',
                               follow_redirects=False)
        assert '/' in response.location


class TestFollowUpSnooze:
    """Test POST /followups/<id>/snooze route."""

    def test_snooze_returns_redirect(self, client, sample_followup, db_session):
        """Snooze redirects (stub behavior)."""
        response = client.post(f'/followups/{sample_followup.id}/snooze',
                               follow_redirects=False)
        assert response.status_code == 302

    def test_snooze_404_for_missing_followup(self, client, db_session):
        """Snooze returns 404 for non-existent follow-up."""
        response = client.post('/followups/99999/snooze')
        assert response.status_code == 404
