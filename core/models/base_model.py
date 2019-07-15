from django.db import models


class Base(models.Model):
    """ Base model for all Botos models. """
    date_created = models.DateTimeField(
        'date_created',
        auto_now=False,
        auto_now_add=True,
        null=True  # To allow older data, if any, to have a value.
    )
    date_updated = models.DateTimeField(
        'date_updated',
        auto_now=True,
        auto_now_add=False,
        null=True  # To allow older data, if any, to have a value.
    )

    class Meta:
        abstract = True
