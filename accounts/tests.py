from django.db import IntegrityError
from django.db import models
from django.test import TestCase

from accounts.models import User
from accounts.models import Batch
from accounts.models import Section


class UserModelTest(TestCase):
    """
    Tests the User model.

    Note that we are not testing the other fields such as the username
    since they are provided by Django. We should only test code that is
    our own, e.g. the batch foreign key field.
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._section = Section.objects.create(section_name='Emerald')
        cls._user = User.objects.create(
            username='juan',
            batch=cls._batch,
            section=cls._section
        )

        cls._user_batch_field = cls._user._meta.get_field('batch')
        cls._user_section_field = cls._user._meta.get_field('section')

    # Test batch foreign key.
    def test_batch_fk_value_is_as_set(self):
        batch_fk = self._user.batch
        self.assertEquals(batch_fk, self._batch)

    def test_batch_fk_connected_model(self):
        connected_model = getattr(
            self._user_batch_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Batch)

    def test_batch_fk_on_delete(self):
        on_delete_policy = getattr(
            self._user_batch_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_batch_fk_null(self):
        null_value = self._user_batch_field.null
        self.assertFalse(null_value)

    def test_batch_fk_blank(self):
        blank_value = self._user_batch_field.blank
        self.assertFalse(blank_value)

    def test_batch_fk_default(self):
        default_value = self._user_batch_field.default
        self.assertIsNone(default_value)

    def test_batch_fk_unique(self):
        unique_value = self._user_batch_field.unique
        self.assertFalse(unique_value)

    def test_batch_fk_related_name(self):
        related_name = getattr(
            self._user_batch_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'users')

    # Test section foreign key.
    def test_section_fk_value_is_as_set(self):
        section_fk = self._user.section
        self.assertEquals(section_fk, self._section)

    def test_section_fk_connected_model(self):
        connected_model = getattr(
            self._user_section_field.remote_field,
            'model'
        )
        self.assertEquals(connected_model, Section)

    def test_section_fk_on_delete(self):
        on_delete_policy = getattr(
            self._user_section_field.remote_field,
            'on_delete'
        )
        self.assertEquals(on_delete_policy, models.PROTECT)

    def test_section_fk_null(self):
        null_value = self._user_section_field.null
        self.assertFalse(null_value)

    def test_section_fk_blank(self):
        blank_value = self._user_section_field.blank
        self.assertFalse(blank_value)

    def test_section_fk_default(self):
        default_value = self._user_section_field.default
        self.assertIsNone(default_value)

    def test_section_fk_unique(self):
        unique_value = self._user_section_field.unique
        self.assertFalse(unique_value)

    def test_secection_fk_related_name(self):
        related_name = getattr(
            self._user_section_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'users')

    # Test the meta class of the custom user model.
    def test_meta_indexes(self):
        indexes = self._user._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'username' ])

    def test_meta_ordering(self):
        ordering = self._user._meta.ordering
        self.assertEquals(ordering, [ 'username' ])

    def test_meta_verbose_name(self):
        verbose_name = self._user._meta.verbose_name
        self.assertEquals(verbose_name, 'user')

    def test_meta_verbose_name_plural(self):
        verbose_name_plural = self._user._meta.verbose_name_plural
        self.assertEquals(verbose_name_plural, 'users')

    def test_str(self):
        self.assertEquals(str(self._user), '<User \'juan\'>')


class BatchModelTest(TestCase):
    """ Tests the Batch model. """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._batch_year_field = cls._batch._meta.get_field('year')

    def test_year_is_as_set(self):
        self.assertEquals(self._batch.year, 2019)

    def test_year_null(self):
        null_value = self._batch_year_field.null
        self.assertFalse(null_value)

    def test_year_blank(self):
        blank_value = self._batch_year_field.blank
        self.assertFalse(blank_value)

    def test_year_default(self):
        default_value = self._batch_year_field.default
        self.assertIsNone(default_value)

    def test_year_unique(self):
        unique_value = self._batch_year_field.unique
        self.assertTrue(unique_value)

    def test_year_verbose_name(self):
        verbose_name = self._batch_year_field.verbose_name
        self.assertEquals(verbose_name, 'year')

    # Test the meta class of the batch model.
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
        cls._section_name_field = cls._section._meta.get_field('section_name')

    def test_section_name_field_is_as_set(self):
        self.assertEquals(self._section.section_name, 'Section')

    def test_section_name_field_max_length(self):
        max_length = self._section_name_field.max_length
        self.assertEquals(max_length, 15)

    def test_section_name_field_null(self):
        null_value = self._section_name_field.null
        self.assertFalse(null_value)

    def test_section_name_field_blank(self):
        blank_value = self._section_name_field.blank
        self.assertFalse(blank_value)

    def test_section_name_field_default(self):
        default_value = self._section_name_field.default
        self.assertIsNone(default_value)

    def test_section_name_field_unique(self):
        unique_value = self._section_name_field.unique
        self.assertTrue(unique_value)

    def test_section_name_field_verbose_name(self):
        verbose_name = self._section_name_field.verbose_name
        self.assertEquals(verbose_name, 'section_name')

    # Test the meta class of the section model.
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
