from django.contrib.postgres import fields as postgres_fields
from django.db import models

from .base_model import Base
from .user_models import User


class CandidateParty(Base):
    """ Model for the candidate parties. """
    party_name = models.CharField(
        'party name',
        max_length=32,
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'party_name' ]) ]
        ordering = [ 'party_name' ]
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
        unique=True
    )
    position_level = models.PositiveSmallIntegerField(
        'position level',
        null=False,
        blank=False,
        default=32767,  # This is the largest number this field type supports.
        unique=False
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'position_name' ]) ]
        ordering = [ 'position_level', 'position_name' ]
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

    class Meta:
        indexes = [ models.Index(fields=[ 'user' ]) ]
        ordering = [
            'position__position_level',
            'party__party_name'
        ]
        verbose_name = 'candidate'
        verbose_name_plural = 'candidates'

    def __str__(self):
        return '{}, {}'.format(self.user.last_name, self.user.first_name)


class Vote(Base):
    """ Model for the votes. """
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
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
    vote_cipher = postgres_fields.JSONField(
        null=False,
        blank=False,
        default=None,
        unique=True  # For privacy reasons; having the same resulting cipher
                     # will weaken privacy since, once you are able to
                     # figure out the original value of a cipher, you will
                     # obviously automatically know the value of duplicate
                     # ciphers.
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'user', 'candidate' ])]
        ordering = [
            'candidate__position__position_level',
            'candidate__party__party_name'
        ]
        verbose_name = 'vote'
        verbose_name_plural = 'votes'

    def __str__(self):
        return '<Vote for \'{}\' by \'{}\'>'.format(
            self.candidate.user.username,
            self.user.username
        )
