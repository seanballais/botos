from django.contrib.auth.models import AbstractUser
from django.db import models

from .base_model import Base


class User(AbstractUser, Base):
    """ Custom model for users. """
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='users'
    )
    section = models.ForeignKey(
        'Section',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='users'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'username' ]) ]
        ordering = [ 'username' ]
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class Batch(Base):
    """ Model for batches. """
    year = models.SmallIntegerField(
        'year',
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'year' ]) ]
        ordering = [ 'year' ]
        verbose_name = 'batch'
        verbose_name_plural = 'batches'


    def __str__(self):
        return str(self.year)


class Section(Base):
    """ Model for sections. """
    section_name = models.CharField(
        'section_name',
        max_length=15,
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'section_name' ]) ]
        ordering = [ 'section_name' ]
        verbose_name = 'section'
        verbose_name_plural = 'sections'

    def __str__(self):
        return self.section_name
