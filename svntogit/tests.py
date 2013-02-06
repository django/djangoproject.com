from django.test import TestCase

class SvnToGitTests(TestCase):
    urls = 'svntogit.urls'

    def test_redirect(self):
        response = self.client.get('/1/', follow=False)
        target = 'https://github.com/django/django/commit/d6ded0e91b'
        self.assertEquals(response.status_code, 301)
        self.assertEquals(response['Location'], target)

    def test_redirect_empty_changeset(self):
        response = self.client.get('/7/')
        self.assertEquals(response.status_code, 404)

    def test_redirect_non_existing_changeset(self):
        response = self.client.get('/20000/')
        self.assertEquals(response.status_code, 404)
