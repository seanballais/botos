from django.test import TestCase

from core.utils import AppSettings


class AppSettingsTest(TestCase):
    """
    Tests the AppSettings utility.

    AppSettings will deal with storing and loading app-related settings. App
    settings is different from the project settings. It deals with app-level
    settings such as templates to be used, while the project settings deals
    with project-level settings such as the database to be used. The way to
    use this is similar to using a dictionary.

    This utility is implemented as a singleton since it will control a single
    shared resource.

    It is expected that there will be more reads than writes, which will be
    relatively rare, with this utility. As such, no concurrency handling is
    needed.

    The utility have the following public methods:
        - set(key, value)
            Create a setting item with the key `key` and a value of `value`.
            The value's default value is None.
        - get(key, default)
            Gets the setting with the key `key`. If such a key is non-existent,
            it will return the value of `default`. The default value of
            `default` is None. The default can be any data type, and not just
            a string. This is to allow for getting back a non-string value
            should the need arise.

    The methods casts the key and value parameters to strings.
    """
    @classmethod
    def setUpTestData(cls):
        AppSettings().set(1)
        AppSettings().set(2, 3)
        AppSettings().set(3, 'number')
        AppSettings().set('number', 3)
        AppSettings().set('another_number', '4')

    def test_properly_converts_keys_and_vals_to_strings(self):
        self.assertTrue(isinstance(AppSettings().get(2), str))
        self.assertTrue(isinstance(AppSettings().get(3), str))
        self.assertTrue(isinstance(AppSettings().get('number'), str))
        self.assertTrue(isinstance(AppSettings().get('another_number'), str))

    def test_key_without_value_gives_none(self):
        self.assertIsNone(AppSettings().get(1))

    def test_non_existent_key_gives_default(self):
        self.assertIsNone(AppSettings().get(69))
        self.assertEqual(AppSettings().get(143, default=69), 69)
