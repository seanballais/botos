from django.db import IntegrityError
from django.test import TestCase

from accounts.models import Batch
from accounts.models import Section


class BatchModelTest(TestCase):
    """ Tests the Batch model. """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)

    def test_year_is_as_initialized(self):
        self.assertEquals(self._batch.year, 2019)

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
        self.assertEquals(str(self._batch), '<Batch \'2019\'>')


class SectionModelTest(TestCase):
    """ Tests the Section model. """
    @classmethod
    def setUpTestData(cls):
        cls._section = Section.objects.create(section_name='Section')

    def test_section_name_is_as_initialized(self):
        self.assertEquals(self._section.section_name, 'Section')

    def test_section_name_max_length(self):
        max_length = self._section._meta.get_field('section_name').max_length
        self.assertEquals(max_length, 15)

    def test_section_name_is_null(self):
        null_constraint = self._section._meta.get_field('section_name').null
        self.assertFalse(null_constraint)

    def test_section_name_is_blank(self):
        blank_constraint = self._section._meta.get_field('section_name').blank
        self.assertFalse(blank_constraint)

    def test_section_name_is_unique(self):
        unique_constraint = self._section._meta.get_field('section_name').unique
        self.assertTrue(unique_constraint)

    def test_section_name_verbose_name(self):
        verbose_name = self._section._meta.get_field('section_name').verbose_name
        self.assertEquals(verbose_name, 'section_name')

    def test_meta_indexes(self):
        indexes = self._section._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'section_name' ])

    def test_meta_ordering(self):
        ordering = self._section._meta.ordering
        self.assertEquals(ordering, [ 'section_name' ])

    def test_meta_verbose_name(self):
        verbose_name = self._section._meta.verbose_name
        self.assertEquals(verbose_name, 'section')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._section._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'sections')

    def test_str(self):
        self.assertEquals(str(self._section), '<Section \'Section\'>')
