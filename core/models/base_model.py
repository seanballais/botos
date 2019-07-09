from django.db import models


class Base(models.Model):
    date_created = models.DateTimeField(
        'date_created',
        auto_now=False,
        auto_now_add=True
    )

    date_updated = models.DateTimeField(
        'date_updated',
        auto_now=True,
        auto_now_add=False
    )

    class Meta:
        abstract = True
