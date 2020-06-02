from io import StringIO

from django.contrib.messages import get_messages
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from core.models import (
    User, Batch, Section, Election, UserType, VoterProfile
)


class LoginViewTest(TestCase):
    """
    Tests the login view.

    This view should only accept POST requests from anonymous users. GET
    requests and logged in users will be redirected to `/`. After logging in,
    users will be redirected to `/`.

    View URL: `/auth/login`
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the test user.
        _election = Election.objects.create(name='Election')
        _batch = Batch.objects.create(year=2020, election=_election)
        _section = Section.objects.create(section_name='Emerald')

        _user = User.objects.create(
            username='juan',
            type=UserType.VOTER
        )
        _user.set_password('pepito')
        _user.save()

        VoterProfile.objects.create(
            user=_user,
            batch=_batch,
            section=_section
        )

    def test_get_requests_redirected_to_index(self):
        response = self.client.get(reverse('auth-login'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_logged_users_redirected_to_index(self):
        self.client.login(username='juan', password='pepito')
        
        self.test_get_requests_redirected_to_index()

    def test_successful_login(self):
        self.client.post(
            reverse('auth-login'),
            { 'username': 'juan', 'password': 'pepito' },
            follow=True
        )
        response = self.client.get(reverse('index'))

        # Well, yeah, sure. We can test if the user gets properly logged in
        # by checking if the response gives it the correct subview, i.e. the
        # voting or voted subview. To make things simpler (Note: KISS), let's
        # just check if the user in the response is not anonymous and has the
        # username of the user we logged in. The latter also tests and makes
        # sure that we log in the correct user.
        response_user = response.context['user']
        self.assertTrue(response_user.is_authenticated)
        self.assertEquals(response_user.username, 'juan')

    def test_wrong_username_password_combination_login(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'juan', 'password': 'wrong password' },
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Wrong username/password combination.'
        )
        self.assertRedirects(response, reverse('index'))

    def test_post_login_no_username(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'password': 'pepito' },
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Invalid data submitted for authentication.'
        )
        self.assertRedirects(response, reverse('index'))

    def test_post_login_no_password(self):
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'juan' },
            follow=True
        )
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Invalid data submitted for authentication.'
        )
        self.assertRedirects(response, reverse('index'))


class LogoutViewTest(TestCase):
    """
    Tests the logout view.

    This view should only accept POST requests from logged in users. GET
    requests and anonymous users will be immediately redirected to `/`. After
    logging out, users will be redirected to `/`.

    Logout views must not accept GET requests because:
       1) It can be abused and have the user unknowingly get logged out of
          their session, which can be done by setting an image tag's src to the
          logout URL of a website, for example [1].
       2) Browsers pre-fetch websites that they think you will visit next. This
          pre-fetching may cause you to logout from the website you're
          currently visiting [2].

       References:
        [1] https://stackoverflow.com/a/3522013/1116098
        [2] https://stackoverflow.com/a/14587231/1116098

    View URL: `/auth/logout`
    """
    @classmethod
    def setUpTestData(cls):
        # Set up the test user.
        _election = Election.objects.create(name='Election')
        _batch = Batch.objects.create(year=2020, election=_election)
        _section = Section.objects.create(section_name='Emerald')

        _user = User.objects.create(
            username='juan',
            type=UserType.VOTER
        )
        _user.set_password('pepito')
        _user.save()

        VoterProfile.objects.create(
            user=_user,
            batch=_batch,
            section=_section
        )

    def test_anonymous_users_get_request_redirected_to_index(self):
        response = self.client.get(reverse('auth-logout'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_logged_in_users_get_request_redirected_to_index(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.get(reverse('auth-logout'), follow=True)
        self.assertRedirects(response, reverse('index'))

    def test_successful_logout(self):
        self.client.login(username='juan', password='pepito')

        response = self.client.post(reverse('auth-logout'), follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'Logged out successfully.'
        )
        self.assertEqual(response.status_code, 204)

        # Make sure the user has been logged out.
        response = self.client.get(reverse('index'), follow=True)
        response_user = response.context['user']
        self.assertTrue(response_user.is_anonymous)
