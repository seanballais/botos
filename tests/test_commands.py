from io import StringIO

from django.contrib.auth.hashers import check_password
from django.core import exceptions
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import (
    TestCase, override_settings
)
from unittest import mock

from core.management.commands import createsuperuser
from core.models import (
    User, UserType
)
from tests.models import (
    AnotherTestUser, TestUser, TestConnectedModel
)


class CreateSuperUserTest(TestCase):
    """ Tests the customized createsuperuser command. """
    def test_superuser_gets_created(self):
        call_command(
            'createsuperuser',
            username='admin',
            password='root',
            email='admin@admin.com',
            stdout=StringIO()
        )

        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' was not created.')

    def test_superuser_password_is_correct(self):
        call_command(
            'createsuperuser',
            username='admin',
            password='root',
            email='admin@admin.com',
            stdout=StringIO()
        )

        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' was not created.')
        else:
            self.assertTrue(user.check_password('root'))

    def test_superuser_is_superuser(self):
        call_command(
            'createsuperuser',
            username='admin',
            password='root',
            email='admin@admin.com',
            stdout=StringIO()
        )

        try:
            user = User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Superuser \'admin\' got the wrong section.')
        else:
            self.assertEqual(user.type, UserType.ADMIN)

    @override_settings(AUTH_USER_MODEL='tests.TestUser')
    def test_user_model_no_password_field(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=admin@botos.system'
        ]
        call_command('createsuperuser', *args, stdout=StringIO())

        try:
            TestUser.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_stdin_not_a_tty(self):
        class MockNoTTYStdin(object):
            def isatty(self):
                return False

        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=admin@botos.system'
        ]
        self.assertRaises(
            createsuperuser.NotRunningInTTYException,
            call_command(
                'createsuperuser', *args,
                stdout=StringIO(), stdin=MockNoTTYStdin()
            )
        )

    def test_non_interactive_call_all_args_valid(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        call_command('createsuperuser', *args, stdout=StringIO())

        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_all_args_valid_with_empty_password(self):
        args = [
            '--username=admin',
            '--password=',
            '--email=admin@botos.system',
            '--no-input'
        ]
        call_command('createsuperuser', *args, stdout=StringIO())

        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_all_args_no_email_valid_used_email(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--no-input'
        ]
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args, stdout=StringIO())
        )

    def test_non_interactive_call_all_args_no_email_invalid_used_email(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--no-input'
        ]
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args,
                                 stdout=StringIO(), stderr=StringIO())
        )

    def test_non_interactive_call_no_additional_args(self):
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin', 'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser', stdout=StringIO())

        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_specified_arg_blank_username(self):
        args = [
            '--username=',
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args, stdout=StringIO())
        )

    def test_non_interactive_call_specified_invalid_taken_username(self):
        User.objects.create(
            username='some_taken_username'
        )

        try:
            User.objects.get(username='some_taken_username')
        except User.DoesNotExist:
            self.fail('User with username \'some_taken_username\' '
                      'was not created.')

        args = [
            '--username=some_taken_username',
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args,
                                 stdout=StringIO(), stderr=StringIO())
        )

    def test_non_interactive_call_specified_invalid_blank_username(self):
        args = [
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]        
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args,
                                 stdout=StringIO(), stderr=StringIO())
        )

    def test_non_interactive_call_specified_invalid_username(self):
        args = [
            '--username=adm!n', # The exclamation mark makes this invalid.
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args,
                                 stdout=StringIO(), stderr=StringIO())
        )

    def test_non_interactive_call_specified_valid_username_no_password(self):
        args = [
            '--username=admin',
            '--email=admin@botos.system',
            '--no-input'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin',
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_specified_no_password_entered_blanks(self):
        args = [
            '--username=admin',
            '--email=admin@botos.system',
            '--no-input'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin',
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '', '', '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_incorrectly_input_repeat_password(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        with mock.patch('getpass.getpass') as mock_getpass:
            mock_getpass.side_effect = [
                '!(root)@', '!(r00t)@', '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_invalid_email(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=adminbotos.system',
            '--no-input'
        ]
        
        self.assertRaises(
            CommandError,
            lambda: call_command('createsuperuser', *args,
                                 stdout=StringIO(), stderr=StringIO())
        )

    def test_non_interactive_call_password_available_in_env(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--email=admin@botos.system',
            '--no-input'
        ]
        with mock.patch.dict(
                'os.environ', { 'DJANGO_SUPERUSER_PASSWORD':  '!(root)@' }):
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_non_interactive_call_user_with_field_val_from_environment(self):
        pass

    @override_settings(AUTH_USER_MODEL='tests.AnotherTestUser')
    def test_non_interactive_call_user_with_foreign_key_required_field(self):
        args = [
            '--username=admin',
            '--password=!(root)@',
            '--some_small_int=1'
        ]
        call_command('createsuperuser', *args,
                     stdout=StringIO(), stderr=StringIO())

        try:
            AnotherTestUser.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    @override_settings(AUTH_USER_MODEL='tests.AnotherTestUser')
    def test_interactive_call_user_model_with_foreign_key_required_field(self):
        TestConnectedModel.objects.create(some_small_int=1)

        args = [
            '--username=admin',
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input:
            # This will be the input for the TestConnectedModel field
            # in AnotherTestUser.
            mock_input.side_effect = [ '1' ]
            call_command('createsuperuser', *args,
                         stdout=StringIO(), stderr=StringIO())

        try:
            AnotherTestUser.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_perform_keyboard_interrupt(self):
        args = [
            '--interactive'
        ]
        target_func_str = (
            'core.management.commands.createsuperuser.get_default_username'
        )
        with mock.patch(target_func_str) as mock_get_default_username:
            # We're just using get_default_username() as a way to invoke a
            # KeyboardInterrupt.
            mock_get_default_username.side_effect = KeyboardInterrupt()
            self.assertRaises(
                SystemExit,
                lambda: call_command('createsuperuser', *args,
                                     stdout=StringIO(), stderr=StringIO())
            )

    def test_interactive_call_perform_arbitrary_validationerror(self):
        args = [
            '--interactive'
        ]
        target_func_str = (
            'core.management.commands.createsuperuser.get_default_username'
        )
        with mock.patch(target_func_str) as mock_get_default_username:
            # We're just using get_default_username() as a way to raise a
            # exceptions.ValidationError.
            mock_get_default_username.side_effect = (
                exceptions.ValidationError('Mocked validation error.')
            )
            self.assertRaises(
                CommandError,
                lambda: call_command('createsuperuser', *args,
                                     stdout=StringIO(), stderr=StringIO())
            )

    def test_interactive_call_no_additional_args(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin', 'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser', *args, stdout=StringIO())

        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_specified_arg_blank_username(self):
        args = [
            '--interactive', '--username='
        ]
        self.assertRaises(CommandError,
                          lambda: call_command('createsuperuser', *args))

    def test_interactive_call_specified_invalid_taken_username(self):
        User.objects.create(username='some_taken_username')

        try:
            User.objects.get(username='some_taken_username')
        except User.DoesNotExist:
            self.fail('User with username \'some_taken_username\' '
                      'was not created.')

        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'some_taken_username',
                'admin', # Time to choose a different username.
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_specified_invalid_blank_username(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                '',
                'admin', # Time to choose a different username.
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_specified_invalid_username(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'adm!n', # The exclamation mark makes this username invalid.
                'admin', # Time to choose a different username.
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_arg_with_invalid_username(self):
        args = [
            '--username=adm!n',
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin', # Time to choose a different username.
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_specified_invalid_email(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin',
                'admin.botos'
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_specified_valid_username_no_password(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin',
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                # No passwords aren't allowed, so let's input passwords.
                '', '', '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_incorrectly_input_repeat_password(self):
        args = [
            '--interactive'
        ]
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass:
            mock_input.side_effect = [
                'admin',
                'admin@botos.system'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(r00t)@', '!(root)@', '!(root)@'
            ]
            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_interactive_call_bypass_password_validation(self):
        args = [
            '--interactive'
        ]
        target_password_validator_str = (
            'core.management.commands.createsuperuser.validate_password'
        )
        with mock.patch('builtins.input') as mock_input, \
             mock.patch('getpass.getpass') as mock_getpass, \
             mock.patch(target_password_validator_str) as mock_pass_validator:
            mock_input.side_effect = [
                'admin',
                'admin@botos.system',
                'N'
            ]
            mock_getpass.side_effect = [
                '!(root)@', '!(root)@', '!(root)@', '!(root)@'
            ]
            mock_pass_validator.side_effect = [
                exceptions.ValidationError('Mocked validation error'),
                None
            ]

            call_command('createsuperuser',
                         *args,
                         stdout=StringIO(),
                         stderr=StringIO())
        try:
            User.objects.get(username='admin')
        except User.DoesNotExist:
            self.fail('Admin was not created successfully.')

    def test_get_input_data_with_default_and_empty_val(self):
        command = createsuperuser.Command()
        with mock.patch('builtins.input') as mock_input:
            mock_input.side_effect = [ '' ]

            test_field = User._meta.get_field('username')
            self.assertEqual(
                command.get_input_data(test_field, '', default='valid_str'),
                'valid_str'
            )
