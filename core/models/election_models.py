from django.core.validators import MinValueValidator
from django.db import models

from .base_model import Base
from .user_models import (
    User, Batch
)


class Election(Base):
    """ Model for the elections. """
    name = models.CharField(
        'name',
        max_length=32,
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'name' ]) ]
        ordering = [ 'name' ]
        verbose_name = 'election'
        verbose_name_plural = 'elections'

    def __str__(self):
        return self.name


class CandidateParty(Base):
    """ Model for the candidate parties. """
    party_name = models.CharField(
        'party name',
        max_length=32,
        null=False,
        blank=False,
        default=None,
        unique=False
    )

    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='candidate_parties'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'party_name' ]) ]
        ordering = [ 'party_name' ]
        unique_together = ( ( 'party_name', 'election', ), )
        verbose_name = 'party'
        verbose_name_plural = 'parties'

    def __str__(self):
        return self.party_name


class CandidatePosition(Base):
    """ Model for the candidate positions. """
    position_name = models.CharField(
        'position name',
        max_length=32,
        null=False,
        blank=False,
        default=None,
        unique=False
    )
    position_level = models.PositiveSmallIntegerField(
        'position level',
        null=False,
        blank=False,
        default=32767,  # This is the largest number this field type supports.
        unique=False
    )
    max_num_selected_candidates = models.PositiveSmallIntegerField(
        'max_num_selected_candidates',
        null=False,
        blank=False,
        default=1,
        unique=False,
        validators=[ MinValueValidator(1) ]
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='candidate_positions'
    )
    target_batches = models.ManyToManyField(
        Batch,
        blank=True,
        default=None,
        related_name='candidate_positions'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'position_name' ]) ]
        ordering = [ 'position_level', 'position_name' ]
        unique_together = ( ( 'position_name', 'election', ), )
        verbose_name = 'candidate position'
        verbose_name_plural = 'candidate positions'

    def __str__(self):
        return self.position_name


class Candidate(Base):
    """ Model for the candidates. """
    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        related_name='+'  # It doesn't make sense to have a reverse
                          # relationship in an is-a relationship.
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        default='avatars/default.png',
        unique=False
    )
    party = models.ForeignKey(
        CandidateParty,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='candidates'
    )
    position = models.ForeignKey(
        CandidatePosition,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='candidates'
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='candidates'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'user' ]) ]
        ordering = [
            'position__position_level',
            'party__party_name',
            'user__last_name',
            'user__first_name'
        ]
        verbose_name = 'candidate'
        verbose_name_plural = 'candidates'

    def __str__(self):
        return '{}, {}'.format(self.user.last_name, self.user.first_name)


class Vote(Base):
    """
    Model for the votes. The existent of a vote record for a user-candidate
    pair means that the user voted for the candidate.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='votes'
    )
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='votes'
    )
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='votes'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'user', 'candidate' ])]
        ordering = [
            'candidate__position__position_level',
            'candidate__party__party_name'
        ]
        unique_together = [ 'user', 'candidate' ]
        verbose_name = 'vote'
        verbose_name_plural = 'votes'

    def __str__(self):
        # Should the need arise, this can be used to determine whose votes were
        # not properly casted, which can be implemented in the admin panel in
        # the future. The votes can be listed, and individually checked. Since
        # we're just checking for existence of votes, the vote count of each
        # vote does not have to be displayed during this auditing process.
        return '<Vote for \'{}\' by \'{}\'>'.format(
            self.candidate.user.username,
            self.user.username
        )
