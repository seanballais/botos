from django.db import IntegrityError
from django.db import models
from django.test import TestCase

from core.models import (
    User, Batch, Section
)


class UserModelTest(TestCase):
    """
    Tests the User model.

    Note that we are not testing the other fields such as the username
    since they are provided by Django. We should only test code that is
    our own, e.g. the batch foreign key field.

    The batch and section foreign keys must have the following settings:
        - on_delete = models.PROTECT
        - null = False
        - blank = False
        - default = None
        - unique = False
        - related_name = 'users

    This model must have its username field set be the index and its
    ordering based on the aforementioned field. The verbose name and
    the plural equivalent must be 'user' and 'users' respectively.
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
    def test_batch_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._user_batch_field, models.ForeignKey)
        )

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
        self.assertFalse(self._user_batch_field.null)

    def test_batch_fk_blank(self):
        self.assertFalse(self._user_batch_field.blank)

    def test_batch_fk_default(self):
        self.assertIsNone(self._user_batch_field.default)

    def test_batch_fk_unique(self):
        self.assertFalse(self._user_batch_field.unique)

    def test_batch_fk_related_name(self):
        related_name = getattr(
            self._user_batch_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'users')

    # Test section foreign key.
    def test_section_fk_is_fk(self):
        self.assertTrue(
            isinstance(self._user_section_field, models.ForeignKey)
        )

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
        self.assertFalse(self._user_section_field.null)

    def test_section_fk_blank(self):
        self.assertFalse(self._user_section_field.blank)

    def test_section_fk_default(self):
        self.assertIsNone(self._user_section_field.default)

    def test_section_fk_unique(self):
        self.assertFalse(self._user_section_field.unique)

    def test_secection_fk_related_name(self):
        related_name = getattr(
            self._user_section_field.remote_field,
            'related_name'
        )
        self.assertEquals(related_name, 'users')

    # Test the meta class.
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
    """
    Tests the Batch model.

    The year field must be a small integer field and has the following
    settings:
        - null = False
        - blank = False
        - default = None
        - unique = True
    """
    @classmethod
    def setUpTestData(cls):
        cls._batch = Batch.objects.create(year=2019)
        cls._batch_year_field = cls._batch._meta.get_field('year')

    # Test year field.
    def test_year_is_small_int_field(self):
        self.assertTrue(
            isinstance(self._batch_year_field, models.SmallIntegerField)
        )

    def test_year_null(self):
        self.assertFalse(self._batch_year_field.null)

    def test_year_blank(self):
        self.assertFalse(self._batch_year_field.blank)

    def test_year_default(self):
        self.assertIsNone(self._batch_year_field.default)

    def test_year_unique(self):
        self.assertTrue(self._batch_year_field.unique)

    def test_year_verbose_name(self):
        self.assertEquals(self._batch_year_field.verbose_name, 'year')

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._batch._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'year' ])

    def test_meta_ordering(self):
        self.assertEquals(self._batch._meta.ordering, [ 'year' ])

    def test_meta_verbose_name(self):
        self.assertEquals(self._batch._meta.verbose_name, 'batch')

    def test_meta_verbose_name_plural(self):
        self.assertEquals(self._batch._meta.verbose_name_plural, 'batches')

    def test_str(self):
        self.assertEquals(str(self._batch), '<Batch \'2019\'>')


class SectionModelTest(TestCase):
    """
    Tests the Section model.

    The section name field must be a character field and the following
    settings:
        - max_length = 15
        - null = False
        - blank = False
        - default = None
        - unique = True
    """
    @classmethod
    def setUpTestData(cls):
        cls._section = Section.objects.create(section_name='Section')
        cls._section_name_field = cls._section._meta.get_field('section_name')

    # Test section_name field.
    def test_section_name_field_is_char_field(self):
        self.assertTrue(
            isinstance(self._section_name_field, models.CharField)
        )

    def test_section_name_field_max_length(self):
        self.assertEquals(self._section_name_field.max_length, 15)

    def test_section_name_field_null(self):
        self.assertFalse(self._section_name_field.null)

    def test_section_name_field_blank(self):
        self.assertFalse(self._section_name_field.blank)

    def test_section_name_field_default(self):
        self.assertIsNone(self._section_name_field.default)

    def test_section_name_field_unique(self):
        self.assertTrue(self._section_name_field.unique)

    def test_section_name_field_verbose_name(self):
        self.assertEquals(
            self._section_name_field.verbose_name,
            'section_name'
        )

    # Test the meta class.
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
