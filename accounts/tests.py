from django.db import IntegrityError
from django.test import TestCase

from accounts.models import Batch


class BatchModelTest(TestCase):
    """ Tests the Batch model class. """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)

    # Tests for design enforcement.
    def test_year_is_null(self):
        null_constraint = self._batch._meta.get_field('year').null
        self.assertFalse(null_constraint)

    def test_year_is_blank(self):
        blank_constraint = self._batch._meta.get_field('year').blank
        self.assertFalse(blank_constraint)

    def test_year_is_unique(self):
        unique_constraint = self._batch._meta.get_field('year').unique
        self.assertTrue(unique_constraint)

    def test_year_verbose_name(self):
        verbose_name = self._batch._meta.get_field('year').verbose_name
        self.assertEquals(verbose_name, 'year')

    def test_year_default(self):
        default = self._batch._meta.get_field('year').default
        self.assertIsNone(default)

    def test_meta_indexes(self):
        indexes = self._batch._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'year' ])

    def test_meta_ordering(self):
        ordering = self._batch._meta.ordering
        self.assertEquals(ordering, [ 'year' ])

    def test_meta_verbose_name(self):
        verbose_name = self._batch._meta.verbose_name
        self.assertEquals(verbose_name, 'batch')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._batch._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'batches')

    def test_str(self):
        self.assertEquals(str(self._batch), '<Batch 2019>')

    # Tests for testing behaviour.
    def test_year_must_be_unique(self):
        self.assertRaises(
            IntegrityError,
            lambda: Batch.objects.create(year=2019)
        )
