from django.test import TestCase


class SvnToGitTests(TestCase):

    def test_redirect(self):
        response = self.client.get('/svntogit/1/', follow=False)
        target = 'https://github.com/django/django/commit/d6ded0e91b'
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response['Location'], target)

    def test_redirect_empty_changeset(self):
        response = self.client.get('/svntogit/7/')
        self.assertEqual(response.status_code, 404)

    def test_redirect_non_existing_changeset(self):
        response = self.client.get('/svntogit/20000/')
        self.assertEqual(response.status_code, 404)
