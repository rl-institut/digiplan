from django.test import TestCase


# Simple tests on project level
class HomepageUrlTests(TestCase):
    def test_homepage_status_code(self):
        response = self.client.get("/")
        # redirect to /de/ as standard language (302=Redirect)
        assert response.status_code == 302

    def test_german_url(self):
        response = self.client.get("/de/")
        assert response.status_code == 200

    def test_english_url(self):
        response = self.client.get("/en/")
        assert response.status_code == 200
