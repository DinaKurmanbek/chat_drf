from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from .managers import UserManager

class User(AbstractBaseUser):
    SUPERUSER, MODERATOR, APPUSER = 1, 2, 3
    ROLES = (
        (SUPERUSER, 'Superuser'),
        (MODERATOR, 'Moderator'),
        (APPUSER, 'AppUser')
    )

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    role = models.IntegerField(default=APPUSER, choices=ROLES)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin access
    is_superuser = models.BooleanField(default=False)  # Required for all permissions

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_superuser

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_superuser
