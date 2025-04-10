from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Wymagany unikalny e-mail
    role = models.CharField(max_length=100, default='user')
    # Dodaj dodatkowe pola w razie potrzeby
