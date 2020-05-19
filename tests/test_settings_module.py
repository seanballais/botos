from django.core.management import call_command
from django.test import TestCase

from botos import settings


class SettingsModuleTest(TestCase):
    """
    Tests the settings module.
    """
    def test_get_env_var_func_value_available(self):
        fake_env = {
            "BOTOS_DATABASE_NAME": 'botos_db'
        }
        self.assertEqual(
            settings.get_env_var('BOTOS_DATABASE_NAME', env_source=fake_env),
            'botos_db'
        )

    def test_get_env_var_func_value_unavailable(self):
        fake_env = dict()
        self.assertRaises(
            SystemExit,
            lambda: settings.get_env_var(
                'BOTOS_DATABASE_NAME', env_source=fake_env
            )
        )

    def test_get_env_var_func_with_value_range_and_meaning_valid_value(self):
        fake_env = {
            "BOTOS_DEBUG": 'True'  # String because os.environ gives a string.
        }
        self.assertEqual(
            settings.get_env_var(
                'BOTOS_DEBUG',
                env_source=fake_env,
                value_meanings={
                    "True": True,
                    "False": False
                }
            ),
            True
        )

    def test_get_env_var_func_with_value_range_and_meaning_invalid_value(self):
        fake_env = {
            "BOTOS_DEBUG": '1'  # String because os.environ gives a string.
        }
        self.assertRaises(
            SystemExit,
            lambda: settings.get_env_var(
                'BOTOS_DEBUG',
                env_source=fake_env,
                value_meanings={
                    "True": True,
                    "False": False
                }
            )
        )

    def test_get_env_var_func_with_debug_value_debug_mode(self):
        fake_env = {
            "BOTOS_DATABASE_NAME": 'botos_db'
        }
        self.assertEqual(
            settings.get_env_var(
                'BOTOS_DATABASE_NAME',
                env_source=fake_env,
                debug=True,
                debug_value='botos_debug'),
            'botos_debug'
        )

    def test_get_env_var_func_with_debug_value_non_debug_mode(self):
        fake_env = {
            "BOTOS_DATABASE_NAME": 'botos_db'
        }
        self.assertEqual(
            settings.get_env_var(
                'BOTOS_DATABASE_NAME',
                env_source=fake_env,
                debug=False),
            'botos_db'
        )

    def test_get_env_var_func_error_msg_no_value_meanings(self):
        with self.assertRaises(SystemExit) as e:
            fake_env = dict()
            settings.get_env_var('BOTOS_DEBUG', env_source=fake_env)

            self.assertEqual(
                e.exception.args[0],
                (
                    'Environment variable, BOTOS_DEBUG, does not exist. '
                    'Make sure that the variable exists.'
                )
            )

    def test_get_env_var_func_error_msg_one_value_meanings(self):
        with self.assertRaises(SystemExit) as e:
            fake_env = {
                "BOTOS_DEBUG": '1'  # String because os.environ gives a string.
            }
            settings.get_env_var(
                'BOTOS_DEBUG',
                env_source=fake_env,
                value_meanings={
                    "True": True
                }
            )

            self.assertEqual(
                e,exception.args[0],
                (
                    'Environment variable, BOTOS_DEBUG, does not exist. '
                    'Make sure that the variable exists. The supported value '
                    'is:\n'
                    '    True'
                )
            )

    def test_get_env_var_func_error_msg_multiple_value_meanings(self):
        with self.assertRaises(SystemExit) as e:
            fake_env = {
                "BOTOS_DEBUG": '1'  # String because os.environ gives a string.
            }
            settings.get_env_var(
                'BOTOS_DEBUG',
                env_source=fake_env,
                value_meanings={
                    "True": True,
                    "False": False,
                    "2": True
                }
            )

            self.assertEqual(
                e,exception.args[0],
                (
                    'Environment variable, BOTOS_DEBUG, does not exist. '
                    'Make sure that the variable exists. The supported value '
                    'is:\n'
                    '    True, False, and 2'
                )
            )
