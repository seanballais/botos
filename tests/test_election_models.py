import json

from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.test import TestCase

from core.models import (
    Vote, Candidate, CandidateParty, CandidatePosition, Election,
    User, Batch, Section, UserType, VoterProfile
)


class VoteTest(TestCase):
    """
    Tests the Vote model.

    The Vote model must have the following custom fields:
        - user (foreign key)
        - candidate (foreign key)
        - vote_cipher

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The user field must be a one-to-one field and have the following settings:
        - to = 'User'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - related_name = 'votes'
        - unique = False

    The candidate field must be a foreign key and have the following settings:
        - to = 'Candidate'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'votes'

    The election field must be a foreign key and have the following settings:
        - to = 'Election'
        - on_delete = 'CASCADE'
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'votes'

    The model must have the following meta settings:
        - Index must be set to the user field and the candidate field.
        - The ordering must be based on the candidate position level first,
          then the candidate last name, and lastly, the candidate first name.
        - Candidate and user must be unique together. This is so that the user
          cannot have duplicate votes for the same candidate.
        - The singular verbose name will be "vote", with the plural being
          "votes".

    The __str__() method should return
    "<Vote for '{candidate username}' by '{ user username }'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._user = User.objects.create(username='juan', type=UserType.VOTER)
        cls._party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=cls._election
        )
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0,
            election=cls._election
        )
        cls._candidate = Candidate.objects.create(
            user=cls._user,
            party=cls._party,
            position=cls._position,
            election=cls._election
        )
        cls._vote = Vote.objects.create(
            user=cls._user,
            candidate=cls._candidate,
            election=cls._election
        )
        cls._vote_user_field = cls._vote._meta.get_field('user')
        cls._vote_candidate_field = cls._vote._meta.get_field('candidate')
        cls._vote_election_field = cls._vote._meta.get_field('election')

    # Test user foreign key.
    def test_user_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._vote_user_field, models.ForeignKey)
        )

    def test_user_fk_connected_model(self):
        connected_model = getattr(
            self._vote_user_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, User)

    def test_user_fk_on_delete(self):
        on_delete_policy = getattr(
            self._vote_user_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_user_fk_null(self):
        self.assertFalse(self._vote_user_field.null)

    def test_user_fk_blank(self):
        self.assertFalse(self._vote_user_field.blank)

    def test_user_fk_default(self):
        self.assertIsNone(self._vote_user_field.default)

    def test_user_fk_unique(self):
        self.assertFalse(self._vote_user_field.unique)

    def test_user_fk_related_name(self):
        related_name = getattr(
            self._vote_user_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'votes')

    # Test candidate foreign key.
    def test_candidate_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._vote_candidate_field, models.ForeignKey)
        )

    def test_candidate_fk_connected_model(self):
        connected_model = getattr(
            self._vote_candidate_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Candidate)

    def test_candidate_fk_on_delete(self):
        on_delete_policy = getattr(
            self._vote_candidate_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_candidate_fk_null(self):
        self.assertFalse(self._vote_candidate_field.null)

    def test_candidate_fk_blank(self):
        self.assertFalse(self._vote_candidate_field.blank)

    def test_candidate_fk_default(self):
        self.assertIsNone(self._vote_candidate_field.default)

    def test_candidate_fk_related_name(self):
        related_name = getattr(
            self._vote_candidate_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'votes')

    # Test election foreign key.
    def test_election_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._vote_election_field, models.ForeignKey)
        )

    def test_election_fk_connected_model(self):
        connected_model = getattr(
            self._vote_election_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Election)

    def test_election_fk_on_delete(self):
        on_delete_policy = getattr(
            self._vote_election_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_election_fk_null(self):
        self.assertFalse(self._vote_election_field.null)

    def test_election_fk_blank(self):
        self.assertFalse(self._vote_election_field.blank)

    def test_election_fk_default(self):
        self.assertIsNone(self._vote_election_field.default)

    def test_election_fk_related_name(self):
        related_name = getattr(
            self._vote_election_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'votes')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._vote._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'user', 'candidate' ])

    def test_meta_ordering(self):
        ordering = self._vote._meta.ordering
        self.assertEquals(
            ordering,
            [
                'candidate__position__position_level',
                'candidate__party__party_name'
            ]
        )

    def test_meta_unique_together(self):
        self.assertEquals(
            self._vote._meta.unique_together,
            ( ('user', 'candidate'), )
        )

    def test_meta_verbose_name(self):
        verbose_name = self._vote._meta.verbose_name
        self.assertEquals(verbose_name, 'vote')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._vote._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'votes')

    def test_str(self):
        self.assertEquals(str(self._vote), '<Vote for \'juan\' by \'juan\'>')


class CandidateTest(TestCase):
    """
    Tests the Candidate model.

    The Candidate model must have the following custom fields:
        - user_id (foreign key)
        - avatar
        - party_id (foreign key)
        - position_id (foreign key)

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The user field must be a one-to-one field and have the following
    settings:
        - to = 'User'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = True
        - related_name = 'candidate'

    The avatar field must be a image field and have the following settings:
        - upload_to = 'avatars/'
        - null = True
        - blank = True
        - default = 'avatars/default.png'
        - unique = False

    The party must be a foreign key and have the following settings:
        - to = 'CandidateParty'
        - on_delete = models.SET_NULL
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidates'

    The position must be a foreign key and have the following settings:
        - to = 'CandidatePosition'
        - on_delete = models.SET_NULL
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidates'

    The election field must be a foreign key and have the following settings:
        - to = 'Election'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidates'

    The model must have the following meta settings:
        - Index must be set to the user field.
        - The ordering must be based on the position level first, then
          the user's last name, and lastly, the user's first name.
        - The singular verbose name will be "candidate", with the plural being
          "candidates".

    The __str__() method should return
    "<Candidate '{candidate username}' ('{position}' candidate of '{party}')>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._user = User.objects.create(
            username='juan',
            first_name='Juan',
            last_name='Pedro',
            type=UserType.VOTER
        )
        cls._election = Election.objects.create(name='Election')
        cls._party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=cls._election
        )
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0,
            election=cls._election
        )
        cls._candidate = Candidate.objects.create(
            user=cls._user,
            party=cls._party,
            position=cls._position,
            election=cls._election
        )
        cls._candidate_user_field = cls._candidate._meta.get_field('user')
        cls._candidate_avatar_field = cls._candidate._meta.get_field('avatar')
        cls._candidate_party_field = cls._candidate._meta.get_field('party')
        cls._candidate_position_field = cls._candidate._meta.get_field(
            'position'
        )
        cls._candidate_election_field = cls._candidate._meta.get_field(
            'election'
        )

        # Test data for validation tests.
        cls._election0 = Election.objects.create(name='Election 0')
        cls._election1 = Election.objects.create(name='Election 1')
        cls._election2 = Election.objects.create(name='Election 2')
        cls._election3 = Election.objects.create(name='Election 3')

        cls._user0 = User.objects.create(
            username='juan0',
            type=UserType.VOTER
        )
        cls._section0 = Section.objects.create(section_name='Section 0')

    # Test user foreign key.
    def test_user_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_user_field, models.OneToOneField)
        )

    def test_user_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_user_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, User)

    def test_user_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_user_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_user_fk_null(self):
        self.assertFalse(self._candidate_user_field.null)

    def test_user_fk_blank(self):
        self.assertFalse(self._candidate_user_field.blank)

    def test_user_fk_default(self):
        self.assertIsNone(self._candidate_user_field.default)

    def test_user_fk_unique(self):
        self.assertTrue(self._candidate_user_field.unique)

    def test_user_fk_related_name(self):
        related_name = getattr(
            self._candidate_user_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidate')

    # Test avatar image field.
    def test_avatar_is_image_field(self):
        self.assertTrue(
            isinstance(self._candidate_avatar_field, models.ImageField)
        )

    def test_avatar_upload_to(self):
        self.assertEquals(
            self._candidate_avatar_field.upload_to,
            'avatars/'
        )

    def test_avatar_null(self):
        self.assertTrue(self._candidate_avatar_field.null)

    def test_avatar_blank(self):
        self.assertTrue(self._candidate_avatar_field.blank)

    def test_avatar_default(self):
        self.assertEquals(
            self._candidate_avatar_field.default,
            'avatars/default.png'
        )

    def test_avatar_unique(self):
        self.assertFalse(self._candidate_avatar_field.unique)

    def tesr_avatar_verbose_name(self):
        self.assertEquals(
            self._candidate_avatar_field.verbose_name,
            'avatar'
        )

    # Test party foreign key.
    def test_party_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_party_field, models.ForeignKey)
        )

    def test_party_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_party_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, CandidateParty)

    def test_party_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_party_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.SET_NULL)

    def test_party_fk_null(self):
        self.assertTrue(self._candidate_party_field.null)

    def test_party_fk_blank(self):
        self.assertFalse(self._candidate_party_field.blank)

    def test_party_fk_default(self):
        self.assertIsNone(self._candidate_party_field.default)

    def test_party_fk_unique(self):
        self.assertFalse(self._candidate_party_field.unique)

    def test_party_fk_related_name(self):
        related_name = getattr(
            self._candidate_party_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidates')

    # Test position foreign key.
    def test_position_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_position_field, models.ForeignKey)
        )

    def test_position_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_position_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, CandidatePosition)

    def test_position_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_position_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.SET_NULL)

    def test_position_fk_null(self):
        self.assertTrue(self._candidate_position_field.null)

    def test_position_fk_blank(self):
        self.assertFalse(self._candidate_position_field.blank)

    def test_position_fk_default(self):
        self.assertIsNone(self._candidate_position_field.default)

    def test_position_fk_unique(self):
        self.assertFalse(self._candidate_position_field.unique)

    def test_party_fk_related_name(self):
        related_name = getattr(
            self._candidate_position_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidates')

    # Test election foreign key.
    def test_election_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._candidate_election_field, models.ForeignKey)
        )

    def test_election_fk_connected_model(self):
        connected_model = getattr(
            self._candidate_election_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Election)

    def test_election_fk_on_delete(self):
        on_delete_policy = getattr(
            self._candidate_election_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_election_fk_null(self):
        self.assertFalse(self._candidate_election_field.null)

    def test_election_fk_blank(self):
        self.assertFalse(self._candidate_election_field.blank)

    def test_election_fk_default(self):
        self.assertIsNone(self._candidate_election_field.default)

    def test_election_fk_unique(self):
        self.assertFalse(self._candidate_election_field.unique)

    def test_election_fk_related_name(self):
        related_name = getattr(
            self._candidate_election_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidates')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._candidate._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'user' ])

    def test_meta_ordering(self):
        ordering = self._candidate._meta.ordering
        self.assertEquals(
            ordering,
            [
                'election',
                'position__position_level',
                'party__party_name',
                'user__last_name',
                'user__first_name'
            ]
        )

    def test_meta_verbose_name(self):
        verbose_name = self._candidate._meta.verbose_name
        self.assertEquals(verbose_name, 'candidate')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._candidate._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'candidates')

    def test_str(self):
        self.assertEquals(
            str(self._candidate),
            'Pedro, Juan'
        )

    def test_model_validate_election_fields_consistent(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        try:
            candidate.clean()
        except ValidationError:
            self.fail(
                'ValidationError raised despite consistent '
                'election field values.'
            )

    def test_model_validate_election_fields_inconsistent_batch(self):
        batch = Batch.objects.create(year=0, election=self._election1)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_party(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election1
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_position(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election1
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_candidate(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election1
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_batch_party(self):
        batch = Batch.objects.create(year=0, election=self._election1)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election2
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_batch_position(self):
        batch = Batch.objects.create(year=0, election=self._election1)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election2
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_batch_candidate(self):
        batch = Batch.objects.create(year=0, election=self._election1)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election2
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_party_position(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election1
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election2
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election0
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_party_candidate(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election1
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election0
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election2
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_pos_candidate(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election0
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election1
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election2
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )

    def test_model_validate_election_fields_inconsistent_all(self):
        batch = Batch.objects.create(year=0, election=self._election0)

        VoterProfile.objects.create(
            user=self._user0,
            batch=batch,
            section=self._section0
        )

        party = CandidateParty.objects.create(
            party_name='Party 0',
            election=self._election1
        )

        position = CandidatePosition.objects.create(
            position_name='Position 0',
            election=self._election2
        )

        candidate = Candidate.objects.create(
            user=self._user0,
            party=party,
            position=position,
            election=self._election3
        )

        self.assertRaisesMessage(
            ValidationError,
            'The candidate\'s batch, party, position, and the candidate '
            'him/herself are not under the same election.',
            candidate.clean
        )


class CandidatePartyTest(TestCase):
    """
    Test the CandidateParty model.

    The CandidateParty model must have the following custom field:
        - party_name

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The party_name field must be a variable character field and have the
    following settings:
        - max_length = 32
        - null = False
        - blank = False
        - default = None
        - unique = False

    The election field must be a foreign key and have the following settings:
        - to = 'Election'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidate_parties'

    The model must have the following meta settings:
        - Index must be set to the party_name field.
        - The ordering must be alphabetical and be based on the party_name
          field.
        - Election and party_name must be a unique pair. This is
          so that there can only be one party with the name in an election.
        - The singular verbose name will be "party", with the plural being
          "parties".

    The __str___() method should return "<CandidateParty '{party name}'>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._party = CandidateParty.objects.create(
            party_name='Awesome Party',
            election=cls._election
        )
        cls._party_name_field = cls._party._meta.get_field('party_name')
        cls._party_election_field = cls._party._meta.get_field('election')

    # Test party_name field.
    def test_party_name_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._party_name_field, models.CharField)
        )

    def test_party_name_max_length(self):
        self.assertEquals(self._party_name_field.max_length, 32)

    def test_party_name_null(self):
        self.assertFalse(self._party_name_field.null)

    def test_party_name_blank(self):
        self.assertFalse(self._party_name_field.blank)

    def test_party_name_default(self):
        self.assertIsNone(self._party_name_field.default)

    def test_party_name_unique(self):
        self.assertFalse(self._party_name_field.unique)

    # Test election foreign key.
    def test_election_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._party_election_field, models.ForeignKey)
        )

    def test_election_fk_connected_model(self):
        connected_model = getattr(
            self._party_election_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Election)

    def test_election_fk_on_delete(self):
        on_delete_policy = getattr(
            self._party_election_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_election_fk_null(self):
        self.assertFalse(self._party_election_field.null)

    def test_election_fk_blank(self):
        self.assertFalse(self._party_election_field.blank)

    def test_election_fk_default(self):
        self.assertIsNone(self._party_election_field.default)

    def test_election_fk_unique(self):
        self.assertFalse(self._party_election_field.unique)

    def test_election_fk_related_name(self):
        related_name = getattr(
            self._party_election_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidate_parties')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._party._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'party_name' ])

    def test_meta_ordering(self):
        self.assertEquals(
            self._party._meta.ordering, [ 'election', 'party_name' ])

    def test_meta_unique_together(self):
        self.assertEquals(
            self._party._meta.unique_together,
            ( ('party_name', 'election'), )
        )

    def test_meta_verbose_name(self):
        self.assertEquals(self._party._meta.verbose_name, 'party')

    def test_meta_verbose_name_plural(self):
        self.assertEquals(self._party._meta.verbose_name_plural, 'parties')

    def test_str(self):
        self.assertEquals(
            str(self._party),
            'Awesome Party'
        )


class CandidatePositionTest(TestCase):
    """
    Test the CandidatePosition model.

    The CandidatePosition model must have the following custom fields:
        - position_name
        - position_level (a lower number means a higher position)

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The position_name field must be variable character field and have the
    following settings:
        - max_length = 32
        - null = False
        - blank = False
        - default = None
        - unique = False

    The position_level field must be a positive small integer field and
    have the following settings:
        - null = False
        - blank = False
        - default = 32767 (the largest number this field type supports)
        - unique = False

    The max_num_selected_candidates field must be a positive small integer
    field and have the following settings:
        - null = False
        - blank = False
        - default = 1
        - unique = False
        - validator = [ MinValueValidator(1) ]
        - verbose_name = 'Maximum Number of Selectable Candidates'

    The election field must be a foreign key and have the following settings:
        - to = 'Election'
        - on_delete = models.CASCADE
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'candidate_positions'

    The target_batches field must be a many-to-many field and have the
    following settings:
        - to = 'Batch'
        - null = True
        - blank = True
        - default = None
        - related_name = 'candidate_positions'

    The model must have the following meta settings:
        - Index must be set to the position_name field.
        - The ordering must be alphabetical and be based on the position_level
          field, then the position_name.
        - Election and position_name must be a unique pair. This is so that
          there is only one position with such name in an election.
        - The singular verbose name will be "candidate position", with the
          plural for being "candidate positions".

    The __str___() method should return
    "<CandidatePosition '{position name}' (level {position level})>".
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._position = CandidatePosition.objects.create(
            position_name='Amazing Position',
            position_level=0,
            election=cls._election
        )
        cls._position_name_field = cls._position._meta.get_field(
            'position_name'
        )
        cls._position_level_field = cls._position._meta.get_field(
            'position_level'
        )
        cls._max_num_selected_candidates = cls._position._meta.get_field(
            'max_num_selected_candidates'
        )
        cls._position_election_field = cls._position._meta.get_field(
            'election'
        )
        cls._target_batches_field = cls._position._meta.get_field(
            'target_batches'
        )

    # Test position_name field.
    def test_position_name_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._position_name_field, models.CharField)
        )

    def test_position_name_max_length(self):
        self.assertEquals(self._position_name_field.max_length, 32)

    def test_position_name_null(self):
        self.assertFalse(self._position_name_field.null)

    def test_position_name_blank(self):
        self.assertFalse(self._position_name_field.blank)

    def test_position_name_default(self):
        self.assertIsNone(self._position_name_field.default)

    def test_position_name_unique(self):
        self.assertFalse(self._position_name_field.unique)

    # Test position level field.
    def test_position_level_is_positive_smallint_field(self):
        self.assertTrue(
            isinstance(
                self._position_level_field,
                models.PositiveSmallIntegerField
            )
        )

    def test_position_level_null(self):
        self.assertFalse(self._position_level_field.null)

    def test_position_level_blank(self):
        self.assertFalse(self._position_level_field.blank)

    def test_position_level_default(self):
        self.assertEquals(self._position_level_field.default, 32767)

    def test_position_level_unique(self):
        self.assertFalse(self._position_level_field.unique)

    # Test position max_num_selected_candidates field.
    def test_max_num_selected_candidates_is_positive_smallint_field(self):
        self.assertTrue(
            isinstance(
                self._max_num_selected_candidates,
                models.PositiveSmallIntegerField
            )
        )

    def test_max_num_selected_candidates_null(self):
        self.assertFalse(self._max_num_selected_candidates.null)

    def test_max_num_selected_candidates_blank(self):
        self.assertFalse(self._max_num_selected_candidates.blank)

    def test_max_num_selected_candidates_default(self):
        self.assertEquals(self._max_num_selected_candidates.default, 1)

    def test_max_num_selected_candidates_unique(self):
        self.assertFalse(self._max_num_selected_candidates.unique)

    def test_max_num_selected_candidates_validators(self):
        self.assertTrue(
            isinstance(
                self._max_num_selected_candidates.validators[0],
                MinValueValidator
            )
        )

    def test_max_num_selected_candidates_verbose_name(self):
        self.assertEqual(
            self._max_num_selected_candidates.verbose_name,
            'Maximum Number of Selectable Candidates'
        )

    # Test election foreign key.
    def test_position_election_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._position_election_field, models.ForeignKey)
        )

    def test_position_election_fk_connected_model(self):
        connected_model = getattr(
            self._position_election_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Election)

    def test_position_election_fk_on_delete(self):
        on_delete_policy = getattr(
            self._position_election_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.CASCADE)

    def test_position_election_fk_null(self):
        self.assertFalse(self._position_election_field.null)

    def test_position_election_fk_blank(self):
        self.assertFalse(self._position_election_field.blank)

    def test_position_election_fk_default(self):
        self.assertIsNone(self._position_election_field.default)

    def test_position_election_fk_unique(self):
        self.assertFalse(self._position_election_field.unique)

    def test_position_election_fk_related_name(self):
        related_name = getattr(
            self._position_election_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidate_positions')

    # Test batches many-to-many field.
    def test_target_batches_field_m2m_is_m2m(self):
        self.assertTrue(
            isinstance(self._target_batches_field, models.ManyToManyField)
        )

    def test_target_batches_field_connected_model(self):
        connected_model = getattr(
            self._target_batches_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Batch)

    def test_target_batches_field_blank(self):
        self.assertTrue(self._target_batches_field.blank)

    def test_target_batches_field_default(self):
        self.assertIsNone(self._target_batches_field.default)

    def test_target_batches_field_related_name(self):
        related_name = getattr(
            self._target_batches_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'candidate_positions')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._position._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'position_name' ])

    def test_meta_ordering(self):
        self.assertEquals(
            self._position._meta.ordering,
            [ 'election', 'position_level', 'position_name' ]
        )

    def test_meta_unique_together(self):
        self.assertEquals(
            self._position._meta.unique_together,
            ( ( 'position_name', 'election', ), )
        )

    def test_meta_verbose_name(self):
        self.assertEquals(
            self._position._meta.verbose_name,
            'candidate position'
        )

    def test_meta_verbose_name_plural(self):
        self.assertEquals(
            self._position._meta.verbose_name_plural,
            'candidate positions'
        )

    def test_str(self):
        self.assertEquals(
            str(self._position),
            'Amazing Position'
        )


class ElectionTest(TestCase):
    """
    Tests the Election model.

    The election name field must be a character field and the following
    settings:
        - max_length = 32
        - null = False
        - blank = False
        - default = None
        - unique = True

    The __str___() method should return "{election name}".
    """
    @classmethod
    def setUpTestData(cls):
        cls._election = Election.objects.create(name='Election')
        cls._election_name_field = cls._election._meta.get_field('name')

    # Test section_name field.
    def test_election_name_field_is_char_field(self):
        self.assertTrue(
            isinstance(self._election_name_field, models.CharField)
        )

    def test_election_name_field_max_length(self):
        self.assertEquals(self._election_name_field.max_length, 32)

    def test_election_name_field_null(self):
        self.assertFalse(self._election_name_field.null)

    def test_election_name_field_blank(self):
        self.assertFalse(self._election_name_field.blank)

    def test_election_name_field_default(self):
        self.assertIsNone(self._election_name_field.default)

    def test_election_name_field_unique(self):
        self.assertTrue(self._election_name_field.unique)

    def test_election_name_field_verbose_name(self):
        self.assertEquals(
            self._election_name_field.verbose_name,
            'name'
        )

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._election._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'name' ])

    def test_meta_ordering(self):
        ordering = self._election._meta.ordering
        self.assertEquals(ordering, [ 'name' ])

    def test_meta_verbose_name(self):
        verbose_name = self._election._meta.verbose_name
        self.assertEquals(verbose_name, 'election')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._election._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'elections')

    def test_str(self):
        self.assertEquals(str(self._election), 'Election')
