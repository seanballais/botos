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

        # It is unlikely that a write operation will occur when there will
        # be a lot of read operations. Thus, we don't do the following
        # operations in a transaction.
        #
        # Used to do the following code with:
        # try:
        #     Setting.objects.create(key=key, value=value)
        # except IntegrityError, UniqueViolation (the psycopg2 exception):
        #     setting = Setting.objects.get(key=key)
        #     setting.value = value
        #     setting.save()
        #
        # However, those two exceptions cannot be captured here, even though
        # it looks like the exceptions are raised here. As such, I switched
        # the code to the one below. In the future, we might want to
        # investigate the incident and find out the reasons why the
        # aforementioned exceptions are not being captured.
        try:
            setting = Setting.objects.get(key=key)
        except Setting.DoesNotExist:
            Setting.objects.create(key=key, value=value)
        else:
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
