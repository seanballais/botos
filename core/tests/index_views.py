from bs4 import BeautifulSoup

from django.test import TestCase

from core.utils import AppSettings


class LoginSubviewTest(TestCase):
    """
    Tests the login sub-view in the index view (accessed via `/`).

    This subview will only appear to anonymous users. Logged-in users will be
    shown either the voting subview or the voted subview.

    It should be noted that user authentication will be handled by
    `django.contrib.auth`. Thus, no tests will be needed for the authentication
    implementation.

    TODO: Make more integration tests to make sure that the login form does
          log in the user, if the correct credentials are given, and returns an
          error message if otherwise.
    """
    def test_anonymous_users_login_subview(self):
        response = self.client.get('/')
        self.assertIsNotNone(self._get_login_form(str(response.content)))

    def test_login_subview_form_has_correct_action_URL(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('action'), '/auth/login')

    def test_login_subview_form_has_correct_method(self):
        response = self.client.get('/')
        form = self._get_login_form(str(response.content))
        self.assertEquals(form.get('method').lower(), 'post')

    def test_index_uses_correct_template(self):
        response = self.client.get('/')
        self.assertTemplatedUsed(response, 'default/index.html')

    def _get_login_form(self, view_html):
        view_html_soup = BeautifulSoup(view_html, 'html.parser')
        form = view_html_soup.find('form', id='login')

        return form
