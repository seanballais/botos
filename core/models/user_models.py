from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .base_model import Base


class UserType(object):
    # We could have used an Enum here, but that would mean that expressions
    # accessing attributes here (e.g. UserType.VOTER) will give back an enum.
    # We need to get integers from this. Sure, we can just append a .value at
    # end of every expression, but it looks inelegant compared to one without
    # a .value.
    VOTER = 0
    ADMIN = 1


class UserManager(BaseUserManager):
    """
    Custom user manager for users.

    Based on Django's UserManager, as defined in:
        https://github.com/django/django/blob/
                5f8495a40ab1554e81ac845484da890dd390e1d8/
                django/contrib/auth/models.py
    """
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields['type'] = UserType.VOTER
        extra_fields['is_staff'] = False
        extra_fields['is_superuser'] = False

        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None,
                         **extra_fields):
        extra_fields['type'] = UserType.ADMIN
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, Base):
    """
    Custom model for users.

    Based on Django's AbstractUser, as defined in:
        https://github.com/django/django/blob/
                5f8495a40ab1554e81ac845484da890dd390e1d8/
                django/contrib/auth/models.py
    """
    USER_TYPE_CHOICES = (
        (UserType.VOTER, 'voter'),
        (UserType.ADMIN, 'admin'),
    )

    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
        help_text=(
            'Required. 150 characters or fewer. Letters, digits, '
            'and @/./+/-/_ only.'
        ),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    first_name = models.CharField('first name', max_length=150, blank=True)
    last_name = models.CharField('last name', max_length=150, blank=True)
    email = models.EmailField('email address', blank=True)

    # We need is_staff, is_active, and is_superuser, so that we can play nicely
    # with Django Admin.
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into this admin site.',
    )
    is_superuser = models.BooleanField(
        'superuser status',
        default=False,
        help_text=(
            'Designates that this user has all permissions without '
            'explicitly assigning them.'
        ),
    )
    type = models.PositiveSmallIntegerField(
        choices=USER_TYPE_CHOICES,
        null=False,
        blank=False,
        default=UserType.VOTER,
        unique=False,
        verbose_name='type'
    )

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        indexes = [ models.Index(fields=[ 'username' ]) ]
        ordering = [ 'username' ]
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def save(self, *args, **kwargs):
        if self.type == UserType.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        elif self.type == UserType.VOTER:
            self.is_staff = False
            self.is_superuser = False

        #self.is_active = True
        
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    # These functions are only here so that we can play nicely with Django.
    def has_perm(self, perm, obj=None):
        return self.type == UserType.ADMIN

    def has_perms(self, perm_list, obj=None):
        return self.type == UserType.ADMIN

    def has_module_perms(self, app_label):
        # Active superusers have all permissions.
        return self.type == UserType.ADMIN

    def __str__(self):
        return '{}, {}'.format(self.last_name, self.first_name)


class VoterProfile(Base):
    """ Custom model for users. """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        unique=True,
        null=False,
        blank=False,
        default=None,
        related_name='voter_profile'  # Note: Voter user *has a* voter profile.
    )
    has_voted = models.BooleanField(
        unique=False,
        null=False,
        blank=False,
        default=False
    )
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='voter_profiles'
    )
    section = models.ForeignKey(
        'Section',
        on_delete=models.PROTECT,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='voter_profiles'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'user' ]) ]
        ordering = [ 'user__username' ]
        verbose_name = 'voter_profile'
        verbose_name_plural = 'voter_profiles'

    def __str__(self):
        return '<Voter Profile, \'{}\'>'.format(self.user.username)


class Batch(Base):
    """ Model for batches. """
    year = models.SmallIntegerField(
        'year',
        null=False,
        blank=False,
        default=None,
        unique=True
    )
    election = models.ForeignKey(
        'Election',  # Using a string for the model name, since using the model
                     # itself would mean importing the model from
                     # election_models, which will cause a circular dependency
                     # since election_models also imports from this module.
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        default=None,
        unique=False,
        related_name='batches'
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'year' ]) ]
        ordering = [ 'year' ]
        verbose_name = 'batch'
        verbose_name_plural = 'batches'


    def __str__(self):
        return str(self.year)


class Section(Base):
    """ Model for sections. """
    section_name = models.CharField(
        'section_name',
        max_length=15,
        null=False,
        blank=False,
        default=None,
        unique=True
    )

    class Meta:
        indexes = [ models.Index(fields=[ 'section_name' ]) ]
        ordering = [ 'section_name' ]
        verbose_name = 'section'
        verbose_name_plural = 'sections'

    def __str__(self):
        return self.section_name
