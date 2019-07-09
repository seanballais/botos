from django.db import connection
from django.db import models
from django.db.models.base import ModelBase
from django.db.utils import ProgrammingError
from django.test import TestCase

from core.models.base_model import Base


class BaseModelTest(TestCase):
    """
    Tests the base model.

    Parts of this test is based on the code in this StackOverflow answer:
    - https://stackoverflow.com/a/51146819/1116098

    It should be noted that the base model must be an abstract class.

    The date_created and date_updated fields must be DateTime field.
    Intuitively, the former can only be set on creation, while the
    latter should be set on creation and update. Thus, date_created
    should have the following settings:
        - auto_now_add = True
        - auto_now = False

    And date_updated with the following settings:
        - auto_now_add = False
        - auto_now = True

    The verbose names of date_created and date_updated must be
    'date_created' and 'date_updated' respectively.
    """
    @classmethod
    def setUpClass(cls):
        # Create dummy model extending Base, a mixin, if we haven't already.
        if not hasattr(cls, '_base_model'):
            cls._base_model = ModelBase(
                'Base',
                ( Base, ),
                { '__module__': Base.__module__ }
            )

            # Create the schema for our base model. If a schema is already
            # create then let's not create another one.
            try:
                with connection.schema_editor() as schema_editor:
                    schema_editor.create_model(cls._base_model)
                super(BaseModelTest, cls).setUpClass()
            except ProgrammingError:
                # NOTE: We get a ProgrammingError since that is what
                #       is being thrown by Postgres. If we were using
                #       MySQL, then we should catch OperationalError
                #       exceptions.
                pass

            cls._test_base = cls._base_model.objects.create()
            cls._test_base_date_created_field = cls._test_base._meta.get_field(
                'date_created'
            )
            cls._test_base_date_updated_field = cls._test_base._meta.get_field(
                'date_updated'
            )

    @classmethod
    def tearDownClass(cls):
        # Delete the schema for the base model. If there is no, then
        # we don't perform a deletion.
        try:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(cls._base_model)
            super(BaseModelTest, cls).tearDownClass()
        except ProgrammingError:
            # NOTE: We get a ProgrammingError since that is what
            #       is being thrown by Postgres. If we were using
            #       MySQL, then we should catch OperationalError
            #       exceptions.
            pass

    # Test date_created field.
    def test_date_created_is_date_time_field(self):
        self.assertTrue(
            isinstance(
                self._test_base_date_created_field,
                models.DateTimeField
            )
        )

    def test_date_created_auto_now(self):
        self.assertFalse(self._test_base_date_created_field.auto_now)

    def test_date_created_auto_now_add(self):
        self.assertTrue(self._test_base_date_created_field.auto_now_add)

    def test_date_created_verbose_name(self):
        self.assertEquals(
            self._test_base_date_created_field.verbose_name,
            'date_created'
        )

    # Test data_updated field.
    def test_date_updated_is_date_time_field(self):
        self.assertTrue(
            isinstance(
                self._test_base_date_updated_field,
                models.DateTimeField
            )
        )

    def test_date_updated_auto_now(self):
        self.assertTrue(self._test_base_date_updated_field.auto_now)

    def test_date_updated_auto_now_add(self):
        self.assertFalse(self._test_base_date_updated_field.auto_now_add)

    def test_date_created_verbose_name(self):
        self.assertEquals(
            self._test_base_date_updated_field.verbose_name,
            'date_updated'
        )

    # Test the meta class.
    def test_meta_abstract(self):
        self.assertTrue(Base._meta.abstract)
