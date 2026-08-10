from django.db import models

from django.contrib.auth.models import AbstractUser
# Import AbstractUser for Custom User Model

from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    pass 