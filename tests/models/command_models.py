from django.contrib.auth.base_user import BaseUserManager
from django.db import models


class TestConnectedModel(models.Model):
    """ Model for batches. """
    some_small_int = models.SmallIntegerField(
        'some_small_int',
        primary_key=True,
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    def __str__(self):
        return str(self.some_small_int)


class TestUserManager(BaseUserManager):
    """
    Based on UserManager in:
        https://github.com/django/django/blob/
            5f8495a40ab1554e81ac845484da890dd390e1d8/
            django/contrib/auth/models.py
    """
    use_in_migrations = True

    def make_random_password(self, length=10,
                             allowed_chars='abcdefghjkmnpqrstuvwxyz'
                                           'ABCDEFGHJKLMNPQRSTUVWXYZ'
                                           '23456789'):
        pass

    def _create_user(self, username, email, **extra_fields):
        """
        Create and save a user with the given username, and email.
        """
        if not username:
            raise ValueError('The given username must be set.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, **extra_fields)

    def create_superuser(self, username, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, **extra_fields)


class AnotherTestUserManager(TestUserManager):
    def _create_user(self, username, email, **extra_fields):
        """
        Create and save a user with the given username, and email.
        """
        try:
            extra_fields['some_small_int'] = TestConnectedModel.objects.get(
                some_small_int=extra_fields['some_small_int']
            )
        except TestConnectedModel.DoesNotExist:
            extra_fields['some_small_int'] = TestConnectedModel.objects.create(
                some_small_int=extra_fields['some_small_int']
            )

        if not username:
            raise ValueError('The given username must be set.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.save(using=self._db)
        return user


class TestUser(models.Model):
    """
    Based on AbstractUser and PermissionsMixin in:
        https://github.com/django/django/blob/
            5f8495a40ab1554e81ac845484da890dd390e1d8/
            django/contrib/auth/models.py
    """
    username = models.CharField(
        'username', max_length=150, unique=True
    )
    first_name = models.CharField(
        'first name', max_length=150, blank=True
    )
    last_name = models.CharField(
        'last name', max_length=150, blank=True
    )
    email = models.EmailField('email address', blank=True)
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_superuser = models.BooleanField('superuser status', default=False)

    objects = TestUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']


class AnotherTestUser(TestUser):
    """
    Used to test the createsuperuser when the user model has a relationship
    with another model.
    """
    some_small_int = models.ForeignKey(
        'TestConnectedModel',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='another_test_users'
    )

    objects = AnotherTestUserManager()

    REQUIRED_FIELDS = [ 'some_small_int' ]
