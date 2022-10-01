from datetime import timezone
from enum import unique
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
import uuid
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserManager(BaseUserManager):
    """ 
    This is a custom user model manager where email is the UID (unique identifier) for authentication instead of username.
    """

    def create_user(self, email, username=None, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('User must set an email!')

        if password is None:
            raise ValueError("Password cannot be empty!")

        if username is not None:
            user = self.model(username=username,
                              email=self.normalize_email(email), **extra_fields)
            user.set_password(password)
            user.save()
            return user

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('SuperUser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('SuperUser must have is_superuser=True')

        return self.create_user(email=email, username=username, password=password, ** extra_fields)


AUTH_PROVIDER = {'google': 'google', 'twitter': 'twitter', 'facebook': 'facebook', 'email': 'email'}

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(
        unique=True, max_length=40, blank=True, null=True, db_index=True)
    email = models.EmailField(
        unique=True, verbose_name="Email", max_length=120, db_index=True)
    auth_provider = models.CharField(blank=False, null=False, max_length=255, default=AUTH_PROVIDER.get('email'))
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_banned = models.BooleanField(default=False)
    is_suspended = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
