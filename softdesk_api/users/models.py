# from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
