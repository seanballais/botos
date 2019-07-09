from django.db import connection
from django.db.models.base import ModelBase
from django.db.utils import OperationalError
from django.test import TestCase

from core.models.base_model import Base


class BaseModelTest(Testcase):
    """
    Tests the base model.

    This test is based on the code in this StackOverflow answer:
    - https://stackoverflow.com/a/51146819/1116098
    """
    @classmethod
    def setUpTestData(cls):
        # Create dummy model extending Base, a mixin.
        cls._base_model = ModelBase(
            '__TestModel__Base',
            ( Base, ),
            { '__module__': Base.__module__ }
        )

        # Create the schema for our base model. If a schema is already
        # create then let's not create another one.
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.create_model(cls._base_model)
            super(BaseModelTest, cls).setUpClass()
        except OperationalError:
            pass

    @classmethod
    def tearDownClass(cls):
        
