from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('board/<int:id>', views.board, name='board'),
]