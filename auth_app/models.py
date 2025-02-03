from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)  # Wymagany unikalny e-mail
    # Dodaj dodatkowe pola w razie potrzeby
