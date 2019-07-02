from django.db import models


class Batch(models.Model):
    """ Model for batches. """
    year = models.SmallIntegerField(
        null=False,
        blank=False,
        unique=True,
        verbose_name='year',
        default=None
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'year' ]) ]
        ordering = [ 'year' ]
        verbose_name = 'batch'
        verbose_name_plural = 'batches'


    def __str__(self):
        return '<Batch {}>'.format(self.year)
