from django.contrib import admin

# Register your models here.

from .models import Board, User

admin.site.register(Board)
admin.site.register(User)
