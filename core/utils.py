from django.db import IntegrityError

from core.models import Setting


class AppSettings(object):
    """
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
    def __new__(cls):
        if not hasattr(cls, '_instance') or not cls._instance:
            cls._instance = super().__new__(cls)

        return cls._instance

    def set(self, key, value=None):
        """
        Create a setting item with the key `key` and a value of `value`. The
        value's default value is None.
        """
        key = str(key)
        if value is not None:
            value = str(value)

        try:
            Setting.objects.create(key=key, value=value)
        except IntegrityError:
            # This means that the unique constraint of `key` has been violated.
            setting = Setting.objects.get(key=key)
            setting.value = value
            setting.save()

    def get(self, key, default=None):
        """
        Get the setting with the key `key`. If such a key is non-existent, it
        will return the value of `default`. The default value of `default` is
        None. The default can be any data type, and not just a string. This is
        to allow for getting back a non-string value should the need arise.
        """
        key = str(key)
        try:
            setting = Setting.objects.get(key=key)
            value = setting.value
        except Setting.DoesNotExist:
            value = default

        return value
