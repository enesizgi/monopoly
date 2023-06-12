from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class Board(models.Model):
    status = models.CharField(max_length=100)

class User(AbstractUser):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, null=True, blank=True)
