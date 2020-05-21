from django.test import TestCase

from core import context_processors
from core.utils import AppSettings


class TemplateContextProcessorTest(TestCase):
    """
    Tests the context processor that gives the current template's name.
    """
    def test_getting_default_template(self):
        self.assertEquals(
            context_processors.get_template(None),
            { 'template': 'default' }
        )

    def test_getting_set_theme(self):
        # WTF, 2019 Sean? HAHAHAHAHA -2020 Sean
        AppSettings().set('template', 'ye-ye-bonel')

        self.assertEquals(
            context_processors.get_template(None),
            { 'template': 'ye-ye-bonel' }
        )
