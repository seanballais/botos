from django.db import models
from django.test import TestCase

from core.models import (
    ElectionSetting
)


class ElectionSettingsTest(TestCase):
    """
    Tests the ElectionSettings model.

    The ElectionSettings model must have the follwwing custom fields:
        - key
        - value

    Note that we're using the term custom since the ID field is already
    provided to us by Django.

    The key field must be a variable character field and has the following
    settings:
        - max_length = 30
        - null = False
        - blank = False
        - default = None
        - unique = True

    The value field must be a variable character field and has the following
    settings:
        - max_length = 128
        - null = True
        - blank = True
        - default = None
        - unique = False

    The model must have the following meta settings:
        - Index must be set to the key field.
        - The ordering must be alphabetical and be based on the key field.
        - The singular verbose name will be "election setting", with the
          plural form being "election settings".
    """
    @classmethod
    def setUpTestData(cls):
        cls._setting = ElectionSetting.objects.create(
            key='test_key',
            value='test_value'
        )
        cls._setting_key_field = cls._setting._meta.get_field('key')
        cls._setting_value_field = cls._setting._meta.get_field('value')

    # Test key field.
    def test_key_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._setting_key_field, models.CharField)
        )

    def test_key_max_length(self):
        self.assertEquals(self._setting_key_field.max_length, 30)

    def test_key_null(self):
        self.assertFalse(self._setting_key_field.null)

    def test_key_blank(self):
        self.assertFalse(self._setting_key_field.blank)

    def test_key_default(self):
        self.assertIsNone(self._setting_key_field.default)

    def test_key_unique(self):
        self.assertTrue(self._setting_key_field.unique)

    def test_key_verbose_name(self):
        self.assertEquals(
            self._setting_key_field.verbose_name,
            'key'
        )

    # Test value field.
    def test_value_is_varchar_field(self):
        self.assertTrue(
            isinstance(self._setting_value_field, models.CharField)
        )

    def test_value_max_length(self):
        self.assertEquals(self._setting_value_field.max_length, 128)

    def test_value_null(self):
        self.assertTrue(self._setting_value_field.null)

    def test_value_blank(self):
        self.assertTrue(self._setting_value_field.blank)

    def test_value_default(self):
        self.assertIsNone(self._setting_value_field.default)

    def test_value_unique(self):
        self.assertFalse(self._setting_value_field.unique)

    def test_value_verbose_name(self):
        self.assertEquals(
            self._setting_value_field.verbose_name,
            'value'
        )

    # Test the meta class.
    def test_meta_indexes(self):
        indexes = self._setting._meta.indexes
        self.assertEquals(len(indexes), 1)
        self.assertEquals(indexes[0].fields, [ 'key' ])

    def test_meta_ordering(self):
        self.assertEquals(self._setting._meta.ordering, [ 'key' ])

    def test_meta_verbose_name(self):
        self.assertEquals(self._setting._meta.verbose_name, 'election setting')

    def test_meta_verbose_name_plural(self):
        self.assertEquals(
            self._setting._meta.verbose_name_plural,
            'election settings'
        )

    def test_str(self):
        self.assertEquals(str(self._setting), 'test_value')
