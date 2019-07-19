from abc import (
    ABC, abstractmethod
)

from django.test import TestCase

from core.forms.admin import (
    CurrentTemplateForm, ElectionStateForm, GenerateElectionKeysForm
)
from core.models (
    User, Batch, Section
)
from core.utils import AppSettings


# Test views.
class BaseElectionSettingsViewTest(ABC, TestCase):
    """
    This is the base class for the rest of the election settings view tests.
    """
    @classmethod
    def setUpClass(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Section')
        cls._admin_batch = Batch.objects.create(year=0)
        cls._admin_section = Section.objects.create(section_name='Superusers')

        User.objects.create_user(
            username='admin',
            email='admin@admin.com',
            password='root',
            batch=cls._admin_batch,
            section=cls._admin_section
        )

        cls._view_url = ''

    def test_view_denies_anonymous_users(self):
        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(response, '/admin')

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(response, '/admin')

    def test_view_denies_non_superusers(self):
        User.objects.create_user(
            username='juan',
            email='juan@juan.com',
            password='123',
            batch=self._batch,
            section=self._section
        )

        self.client.login(username='juan', password='123')

        response = self.client.get(self._view_url, follow=True)
        self.assertRedirects(response, '/admin')

        response = self.client.post(self._view_url, follow=True)
        self.assertRedirects(response, '/admin')

    @abstractmethod
    def test_view_accepts_superusers(self):
        pass


class ElectionSettingsViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings view in the admin.

    The election settings view can be accessed via `/admin/election/`.
    Anonymous and non-superuser users will be redirected to the admin index
    page.

    This view allows modifying the following settings:
        - Current Template
        - Open/Close State of the Elections
            - Note: When the elections are open, the results will give each
                    candidate names and have their avatars changed to the
                    default one, but with some colour changes. On the flip
                    side, when the elections are closed, the results will
                    show the candidates' actual names and avatars.
        - Creation/Modification of Public/Private Keys For Vote Encryption
            - Note: This setting will be disabled if there are vote set
                    already, or the elections are open.

    This view also has a button that will purge votes, essentially resetting
    the elections. However, candidates, parties, and positions will remain
    intact.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        cls._view_url = '/admin/election'

    def test_view_accepts_superusers(self):
        self.client.login(username='admin', password='root')

        response = self.client.get('/admin/election', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            '{}/admin_election.html'.format(cls._current_template)
        )


class ElectionSettingsCurrentTemplateViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings current template view.

    This view changes the current template being used. This will only accept
    POST requests. GET requests from superusers will result in a redirection
    to `/admin/election`, while non-superusers and anonymoous users to `/`.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._view_url = '/admin/election/template'

        cls.client.login(username='admin', password='root')

    def test_view_accepts_superusers(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_properly_redirects_get_requests(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('template', 'default')

        # Return an error message to the view we'll be redirected to.
        response = self.client.post(self._view_url, {})

        self.assertTrue(
            'Template field must not be empty '
            + 'nor have invalid data.' in response.content
        )
        self.assertEquals(AppSettings.get('template'), 'default')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('template', 'default')

        # Return a success message to the view we'll be redirected to.
        response = self.client.post(
            self._view_url,
            { 'new_template_name': 'my-little-pony' }
        )

        self.assertTrue(
            'Current template changed successfully.' in response.content
        )
        self.assertEquals(AppSettings.get('template'), 'my-little-pony')


class ElectionSettingsElectionsStateViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings election state view.

    This view changes the election state being used. An election state can
    either be open or closed. When the state is open, voters will be allowed to
    vote, and realtime results will show candidates with random names. This
    will only accept POST requests. GET requests from superusers will result in
    a redirection to `/admin/election`, while non-superusers and anonymoous
    users to `/`.

    This view must only accept a value that is either a True or False.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._view_url = '/admin/election/state'

        cls.client.login(username='admin', password='root')

    def test_view_accepts_superusers(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_properly_redirects_get_requests(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_with_invalid_post_requests(self):
        AppSettings().set('is_elections_open', True)

        # Return an error message to the view we'll be redirected to.
        response = self.client.post(self._view_url, {})

        self.assertTrue(
            'You attempted to change the '
            + 'election state with invalid data.' in response.content
        )
        self.assertEquals(AppSettings().get('is_elections_open'), 'True')

    def test_view_with_valid_post_requests(self):
        AppSettings().set('is_elections_open', True)

        # Return a success message to the view we'll be redirected to.
        response = self.client.post(
            self._view_url,
            { 'new_state': 'False' }
        )

        self.assertTrue(
            'Election state changed successfully.' in response.content
        )
        self.assertEquals(AppSettings().get('template'), 'False')


class ElectionSettingsPubPrivKeysViewTest(BaseElectionSettingsViewTest):
    """
    Tests the election settings public/private election keys view.

    This view changes the election state being used. An election state can
    either be open or closed. When the state is open, voters will be allowed to
    vote, and realtime results will show candidates with random names. This
    will only accept POST requests. GET requests from superusers will result in
    a redirection to `/admin/election`, while non-superusers and anonymoous
    users to `/`.

    Calling this view will immediately invoke Botos to generate a new set of
    public and private election keys. The keys will be used to encrypt and
    decrypt votes. However, if there are votes already or the elections are
    open, then calling this view will just simply send back a message that the
    operation cannot be performed due to the aformentioned conditions.
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls._view_url = '/admin/election/keys'

        cls.client.login(username='admin', password='root')

    def test_view_accepts_superusers(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_properly_redirects_get_requests(self):
        response = self.client.get(self._view_url)
        self.assertRedirects(response, '/admin/election')

    def test_view_disregards_params_in_post_requests(self):
        # View should still perform its task even if there are parameters in
        # the post request.
        self.client.post(self._view_url, { 'this is a': 'param' })
        self.assertIsNotNone(AppSettings().get('public_election_key'))
        self.assertIsNotNone(AppSettings().get('private_election_key'))

    def test_view_with_empty_params_in_post_requests(self):
        self.client.post(self._view_url, {})
        self.assertIsNotNone(AppSettings().get('public_election_key'))
        self.assertIsNotNone(AppSettings().get('private_election_key'))

    def test_view_but_with_votes_present(self):
        # Create the test non-superuser.
        _batch = Batch.objects.create(year=2019)
        _section = Section.objects.create(section_name='Emerald')
        _user = User.objects.create(
            username='juan',
            batch=cls._batch,
            section=cls._section
        )
        _party = CandidateParty.objects.create(party_name='Awesome Party')
        _position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0
        )
        _candidate = Candidate.objects.create(
            user=cls._user,
            party=cls._party,
            position=cls._position
        )

        # Create a dummy vote.
        _vote = Vote.objects.create(
            user=cls._user,
            candidate=cls._candidate,
            vote_cipher=json.dumps(dict())
        )

        # public_election_key`and`private_election_key`must not change,
        # since votes are already present.
        AppSettings().set('public_election_key', 'am a barbie girl')
        AppSettings().set('private_election_key', 'in a barbie world')

        self.client.post(self._view_url, {})

        self.assertEquals(
            AppSettings().get(
                'public_election_key',
                'am a barbie girl'
            )
        )
        self.assertEquals(
            AppSettings().get(
                'private_election_key',
                'in a barbie world'
            )
        )

    def test_view_but_with_votes_not_present(self):
        # public_election_key`and private_election_key`must change,
        # since votes are not present.
        AppSettings().set('public_election_key', 'all we hear is')
        AppSettings().set('private_election_key', 'radio gaga')

        self.client.post(self._view_url, {})

        self.assertNotEquals(
            AppSettings().get(
                'public_election_key',
                'all we hear is'
            )
        )
        self.assertNotEquals(
            AppSettings().get(
                'private_election_key',
                'radio gaga'
            )
        )

    def test_view_but_with_elections_open(self):
        # public_election_key`and`private_election_key`must not change,
        # since the elections are open.
        AppSettings().set('is_elections_open', True)
        AppSettings().set('public_election_key', 'break break break')
        AppSettings().set('private_election_key', 'breakthrough')

        self.client.post(self._view_url, {})

        self.assertEquals(
            AppSettings().get(
                'public_election_key',
                'break break break'
            )
        )
        self.assertEquals(
            AppSettings().get(
                'private_election_key',
                'breakthrough'
            )
        )

    def test_view_but_with_elections_closed(self):
        # public_election_key`and`private_election_key`must change,
        # since the elections are closed.
        AppSettings().set('is_elections_open', False)
        AppSettings().set('public_election_key', 'years from now, i be like')
        AppSettings().set('private_election_key', 'wtf was i thinking')

        self.client.post(self._view_url, {})

        self.assertNotEquals(
            AppSettings().get(
                'public_election_key',
                'years from now, i be like'
            )
        )
        self.assertNotEquals(
            AppSettings().get(
                'private_election_key',
                'wtf was i thinking'
            )
        )
