from django.db import models

from .base_model import Base


class Setting(Base):
    """ Model for the election settings. """
    key = models.CharField(
        'key',
        max_length=30,
        null=False,
        blank=False,
        default=None,
        unique=True
    )
    value = models.TextField(
        'value',
        null=True,
        blank=True,
        default=None,
        unique=False
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'key' ]) ]
        ordering = [ 'key' ]
        verbose_name = 'election setting'
        verbose_name_plural = 'election settings'

    def __str__(self):
        return self.value
