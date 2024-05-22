from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db import models
from django.test import TestCase

from core.models import (
    User, Batch, Section, UserType, VoterProfile, Election
)


class UserManagerTest(TestCase):
    """
    Tests the UserManager.

    This mostly tests UserManager in cases that are not covered by other tests.
    """
    def test_create_voter_user(self):
        User.objects.create_user(
            'voter',
            email='voter@botos.system',
            password='root'
        )

        try:
            user = User.objects.get(username='voter')
        except User.DoesNotExist:
            self.fail('Voter was not created.')
        else:
            self.assertEqual(user.type, UserType.VOTER)
            self.assertFalse(user.is_staff)
            self.assertFalse(user.is_superuser)

    def test_create_voter_user_with_no_username(self):
        self.assertRaises(
            ValueError,
            lambda: User.objects.create_user(
                username=None,
                email='voter@botos.system',
                password='root'
            )
        )

    def test_create_admin_user(self):
        User.objects.create_superuser(
            'admin',
            email='admin@botos.system',
            password='root'
        )

        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created.')
        else:
            self.assertEqual(user.type, UserType.ADMIN)
            self.assertTrue(user.is_staff)
            self.assertTrue(user.is_superuser)

    def test_create_admin_user_with_no_username(self):
        self.assertRaises(
            ValueError,
            lambda: User.objects.create_superuser(
                username=None,
                email='admin@botos.system',
                password='root'
            )
        )


class UserModelTest(TestCase):
    """
    Tests the User model.

    Note that we are not testing the other fields such as the username
    since they are provided by Django. We should only test code that is
    our own, e.g. the user type field.

    This model has two user types it can select from: voter and admin. A user
    can only have one role.

    This model must have its username field set be the index and its
    ordering based on the aforementioned field. The verbose name and
    the plural equivalent must be 'user' and 'users' respectively.

    The __str___() method should return "User '{username}'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._user = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Pedro',
            type=UserType.VOTER
        )

        cls._type_field = cls._user._meta.get_field('type')

    # Test the type field.
    def test_type_is_positive_small_int_field(self):
        self.assertTrue(
            isinstance(self._type_field, models.PositiveSmallIntegerField)
        )

    def test_type_choices_not_none(self):
        self.assertIsNotNone(self._type_field.choices)

    def test_type_not_null(self):
        self.assertFalse(self._type_field.null)

    def test_type_not_blank(self):
        self.assertFalse(self._type_field.blank)

    def test_type_default_is_voter(self):
        self.assertEqual(self._type_field.default, UserType.VOTER)

    def test_type_not_unique(self):
        self.assertFalse(self._type_field.unique)

    # NOTE: DO NOT TEST THE FIRST NAME AND LAST NAME FIELDS. THEY WILL BE
    #       REMOVED.
    # TODO: Test the other untested model fields, and functions.

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._user._meta.indexes
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].fields, [ 'username' ])

    def test_meta_ordering(self):
        ordering = self._user._meta.ordering
        self.assertEqual(ordering, [ 'username' ])

    def test_meta_verbose_name(self):
        verbose_name = self._user._meta.verbose_name
        self.assertEqual(verbose_name, 'user')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._user._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, 'users')

    def test_str(self):
        self.assertEqual(str(self._user), 'Pedro, Juan')

    # Test the permissions function.
    def test_has_perm_with_voter(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.VOTER
        )
        self.assertFalse(user.has_perm(None))

    def test_has_perm_with_admin(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.ADMIN
        )
        self.assertTrue(user.has_perm(None))

    def test_has_perms_with_voter(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.VOTER
        )
        self.assertFalse(user.has_perms([]))

    def test_has_perms_with_admin(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.ADMIN
        )
        self.assertTrue(user.has_perms([]))

    def test_has_module_perms_with_voter(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.VOTER
        )
        self.assertFalse(user.has_module_perms(''))

    def test_has_module_perms_with_admin(self):
        user = User.objects.create(
            username='jun',
            first_name='Jun',
            last_name='Pedro',
            type=UserType.ADMIN
        )
        self.assertTrue(user.has_module_perms(''))

    # Test the save function.
    def test_save_with_user_type_as_admin(self):
        user = User.objects.create(
            username='admin',
            type=UserType.ADMIN
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_save_with_user_type_as_voter(self):
        user = User.objects.create(
            username='voter',
            type=UserType.VOTER
        )
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)


class VoterProfileModelTest(TestCase):
    """
    Tests the Voter Profile model.
    
    This model holds the profile for voters.

    The user field must be a one-to-one field and have the
    following settings:
        - on_delete = CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = True
        - related_name = 'voter_profile'

    The has_voted field must be a boolean field and hve the following settings:
        - null = False
        - blank = False
        - default = False
        - unique = False

    The batch and section foreign keys must have the following settings:
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'voter_profiles'

    The model must have the following meta settings:
        - Index must be set to the user field.
        - The singular verbose name will be "voter profile", with the plural
          being "voter profiles".

    The __str___() method should return the string version of the user object.
    """
    @classmethod
    def setUpTestData(cls):
        _election = Election.objects.create(name='Election')
        cls._batch = Batch.objects.create(year=2019, election=_election)
        cls._section = Section.objects.create(section_name='Emerald')
        cls._user = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Miguel',
            type=UserType.VOTER
        )
        cls._voter_profile = VoterProfile.objects.create(
            user=cls._user,
            batch=cls._batch,
            section=cls._section
        )

        cls._user_field = cls._voter_profile._meta.get_field('user')
        cls._batch_field = cls._voter_profile._meta.get_field('batch')
        cls._section_field = cls._voter_profile._meta.get_field('section')
        cls._has_voted_field = cls._voter_profile._meta.get_field('has_voted')

        # Test data for testing model clean function.
        cls._batch0 = Batch.objects.create(year=0, election=_election)
        cls._batch1 = Batch.objects.create(year=1, election=_election)

        cls._section0 = Section.objects.create(section_name='Section 0')
        cls._section1 = Section.objects.create(section_name='Section 1')
        cls._section2 = Section.objects.create(section_name='Section 2')

        cls._user0 = User.objects.create(username='user0', type=UserType.VOTER)
        cls._user1 = User.objects.create(username='user1', type=UserType.VOTER)
        cls._user2 = User.objects.create(username='user2', type=UserType.VOTER)

        VoterProfile.objects.create(
            user=cls._user1,
            batch=cls._batch0,
            section=cls._section1
        )

        VoterProfile.objects.create(
            user=cls._user2,
            batch=cls._batch1,
            section=cls._section2
        )

    # Test user foreign key.
    def test_user_fk_is_one_to_one(self):
        self.assertTrue(
            isinstance(self._user_field, models.OneToOneField)
        )

    def test_user_fk_connected_model(self):
        connected_model = getattr(self._user_field.remote_field, 'model')
        self.assertEqual(connected_model, User)

    def test_user_fk_on_delete(self):
        on_delete_policy = getattr(self._user_field.remote_field, 'on_delete')
        self.assertEqual(on_delete_policy, models.CASCADE)

    def test_user_fk_null(self):
        self.assertFalse(self._user_field.null)

    def test_user_fk_blank(self):
        self.assertFalse(self._user_field.blank)

    def test_user_fk_default(self):
        self.assertIsNone(self._user_field.default)

    def test_user_fk_unique(self):
        self.assertTrue(self._user_field.unique)

    def test_user_fk_related_name(self):
        related_name = getattr(self._user_field.remote_field, 'related_name')
        self.assertEqual(related_name, 'voter_profile')

    # Test has_voted field.
    def test_has_voted_field_is_boolean(self):
        self.assertTrue(
            isinstance(self._has_voted_field, models.BooleanField)
        )

    def test_has_voted_field_null(self):
        self.assertFalse(self._has_voted_field.null)

    def test_has_voted_field_blank(self):
        self.assertFalse(self._has_voted_field.blank)

    def test_has_voted_field_default(self):
        self.assertFalse(self._has_voted_field.default)

    def test_has_voted_field_unique(self):
        self.assertFalse(self._has_voted_field.unique)

    # Test batch foreign key.
    def test_batch_fk_is_fk(self):
        self.assertTrue(isinstance(self._batch_field, models.ForeignKey))

    def test_batch_fk_connected_model(self):
        connected_model = getattr(
            self._batch_field.remote_field,
            'model'
        )
        self.assertEqual(connected_model, Batch)

    def test_batch_fk_on_delete(self):
        on_delete_policy = getattr(
            self._batch_field.remote_field,
            'on_delete'
        )
        self.assertEqual(on_delete_policy, models.CASCADE)

    def test_batch_fk_null(self):
        self.assertFalse(self._batch_field.null)

    def test_batch_fk_blank(self):
        self.assertFalse(self._batch_field.blank)

    def test_batch_fk_default(self):
        self.assertIsNone(self._batch_field.default)

    def test_batch_fk_unique(self):
        self.assertFalse(self._batch_field.unique)

    def test_batch_fk_related_name(self):
        related_name = getattr(self._batch_field.remote_field, 'related_name')
        self.assertEqual(related_name, 'voter_profiles')

    # Test section foreign key.
    def test_section_fk_is_fk(self):
        self.assertTrue(isinstance(self._section_field, models.ForeignKey))

    def test_section_fk_connected_model(self):
        connected_model = getattr(self._section_field.remote_field, 'model')
        self.assertEqual(connected_model, Section)

    def test_section_fk_on_delete(self):
        on_delete_policy = getattr(
            self._section_field.remote_field,
            'on_delete'
        )
        self.assertEqual(on_delete_policy, models.CASCADE)

    def test_section_fk_null(self):
        self.assertFalse(self._section_field.null)

    def test_section_fk_blank(self):
        self.assertFalse(self._section_field.blank)

    def test_section_fk_default(self):
        self.assertIsNone(self._section_field.default)

    def test_section_fk_unique(self):
        self.assertFalse(self._section_field.unique)

    def test_section_fk_related_name(self):
        related_name = getattr(
            self._section_field.remote_field,
            'related_name'
        )
        self.assertEqual(related_name, 'voter_profiles')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._voter_profile._meta.indexes
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].fields, [ 'user' ])

    def test_meta_ordering(self):
        ordering = self._voter_profile._meta.ordering
        self.assertEqual(ordering, [ 'user__username' ])

    def test_meta_verbose_name(self):
        verbose_name = self._voter_profile._meta.verbose_name
        self.assertEqual(verbose_name, 'voter profile')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._voter_profile._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, 'voter profiles')

    def test_str(self):
        self.assertEqual(str(self._voter_profile), str(self._user))

    def test_creating_voter_profile_available_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section0
        )

        try:
            voter_profile.clean()
        except ValidationError:
            self.fail(
                'Voter profile raised a validation error even though it'
                'should not.'
            )

    def test_creating_voter_profile_allowed_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section1
        )

        try:
            voter_profile.clean()
        except ValidationError:
            self.fail(
                'Voter profile raised a validation error even though it'
                'should not.'
            )

    def test_creating_voter_profile_unavailable_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section2
        )
        self.assertRaisesMessage(
            ValidationError,
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
            voter_profile.clean
        )

    def test_saving_voter_profile_available_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section0
        )

        try:
            voter_profile.save()
        except ValidationError:
            self.fail(
                'Voter profile raised a validation error even though it'
                'should not.'
            )

    def test_saving_voter_profile_allowed_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section1
        )

        try:
            voter_profile.save()
        except ValidationError:
            self.fail(
                'Voter profile raised a validation error even though it'
                'should not.'
            )

    def test_creating_voter_profile_unavailable_section(self):
        voter_profile = VoterProfile(
            user=self._user0,
            batch=self._batch0,
            section=self._section2
        )
        self.assertRaisesMessage(
            ValidationError,
            'The selected section is already used by another batch. No two '
            'batches can have the same section.',
            voter_profile.save
        )


class BatchModelTest(TestCase):
    """
    Tests the Batch model.

    The year field must be a small integer field and has the following
    settings:
        - null = False
        - blank = False
        - default = None
        - unique = True

    The election field must be a foreign key and have the following settings:
        - to = 'Election'
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'batches'

    The __str___() method should return "<Batch '{year}'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._batch = Batch.objects.create(year=2019, election=cls._election)
        cls._batch_year_field = cls._batch._meta.get_field('year')
        cls._batch_election_field = cls._batch._meta.get_field(
            'election'
        )

    # Test year field.
    def test_year_is_small_int_field(self):
        self.assertTrue(
            isinstance(self._batch_year_field, models.SmallIntegerField)
        )

    def test_year_null(self):
        self.assertFalse(self._batch_year_field.null)

    def test_year_blank(self):
        self.assertFalse(self._batch_year_field.blank)

    def test_year_default(self):
        self.assertIsNone(self._batch_year_field.default)

    def test_year_unique(self):
        self.assertTrue(self._batch_year_field.unique)

    def test_year_verbose_name(self):
        self.assertEqual(self._batch_year_field.verbose_name, 'year')

    # Test election foreign key.
    def test_election_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._batch_election_field, models.ForeignKey)
        )

    def test_election_fk_connected_model(self):
        connected_model = getattr(
            self._batch_election_field.remote_field,
            'model'
        )
        self.assertEqual(connected_model, Election)

    def test_election_fk_on_delete(self):
        on_delete_policy = getattr(
            self._batch_election_field.remote_field,
            'on_delete'
        )
        self.assertEqual(on_delete_policy, models.PROTECT)

    def test_election_fk_null(self):
        # The election field shouldn't be null since, based on current use
        # cases, voters already have an election they will be participating
        # in.
        self.assertFalse(self._batch_election_field.null)

    def test_election_fk_blank(self):
        self.assertFalse(self._batch_election_field.blank)

    def test_election_fk_default(self):
        self.assertIsNone(self._batch_election_field.default)

    def test_election_fk_unique(self):
        self.assertFalse(self._batch_election_field.unique)

    def test_election_fk_related_name(self):
        related_name = getattr(
            self._batch_election_field.remote_field,
            'related_name'
        )
        self.assertEqual(related_name, 'batches')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._batch._meta.indexes
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].fields, [ 'year' ])

    def test_meta_ordering(self):
        self.assertEqual(self._batch._meta.ordering, [ 'year' ])

    def test_meta_verbose_name(self):
        self.assertEqual(self._batch._meta.verbose_name, 'batch')

    def test_meta_verbose_name_plural(self):
        self.assertEqual(self._batch._meta.verbose_name_plural, 'batches')

    def test_str(self):
        self.assertEqual(str(self._batch), '2019')


class SectionModelTest(TestCase):
    """
    Tests the Section model.

    The section name field must be a character field and the following
    settings:
        - max_length = 15
        - null = False
        - blank = False
        - default = None
        - unique = True

    The __str___() method should return "<Section '{section name}'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._section = Section.objects.create(section_name='Section')
        cls._section_name_field = cls._section._meta.get_field('section_name')

    # Test section_name field.
    def test_section_name_field_is_char_field(self):
        self.assertTrue(
            isinstance(self._section_name_field, models.CharField)
        )

    def test_section_name_field_max_length(self):
        self.assertEqual(self._section_name_field.max_length, 15)

    def test_section_name_field_null(self):
        self.assertFalse(self._section_name_field.null)

    def test_section_name_field_blank(self):
        self.assertFalse(self._section_name_field.blank)

    def test_section_name_field_default(self):
        self.assertIsNone(self._section_name_field.default)

    def test_section_name_field_unique(self):
        self.assertTrue(self._section_name_field.unique)

    def test_section_name_field_verbose_name(self):
        self.assertEqual(
            self._section_name_field.verbose_name,
            'section_name'
        )

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._section._meta.indexes
        self.assertEqual(len(indexes), 1)
        self.assertEqual(indexes[0].fields, [ 'section_name' ])

    def test_meta_ordering(self):
        ordering = self._section._meta.ordering
        self.assertEqual(ordering, [ 'section_name' ])

    def test_meta_verbose_name(self):
        verbose_name = self._section._meta.verbose_name
        self.assertEqual(verbose_name, 'section')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._section._meta.verbose_name_plural
        self.assertEqual(verbose_name_plural, 'sections')

    def test_str(self):
        self.assertEqual(str(self._section), 'Section')
