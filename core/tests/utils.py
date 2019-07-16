from django.test import TestCase

from core.utils import AppSettings


class AppSettingsTest(TestCase):
    """
    Tests the AppSettings utility.

    AppSettings will deal with storing and loading app-related settings. App
    settings is different from the project settings. It deals with app-level
    settings such as templates to be used, while the project settings deals
    with project-level settings such as the database to be used.

    This utility is implemented as a singleton since it will control a single
    shared resource.

    It is expected that there will be more reads than writes, which will be
    relatively rare, with this utility. As such, no concurrency handling is
    needed.
    """
    pass
