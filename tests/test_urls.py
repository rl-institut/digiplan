"""Base tests to see if django runserver comes up."""
from django.test import TestCase


# Simple tests on project level
class HomepageUrlTests(TestCase):
    """Basic checks for homepage."""

    def test_homepage_status_code(self):
        """Checks if index page is loaded."""
        response = self.client.get("/")
        # redirect to /de/ as standard language (302=Redirect)
        assert response.status_code == 302

    def test_german_url(self):
        """Checks if german version runs."""
        response = self.client.get("/de/")
        assert response.status_code == 200

    def test_english_url(self):
        """Checks if english version runs."""
        response = self.client.get("/en/")
        assert response.status_code == 200
