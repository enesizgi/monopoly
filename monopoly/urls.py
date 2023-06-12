from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/boards', views.fetch_available_boards, name='fetch_available_boards'),
    path('board/<int:id>', views.board, name='board'),
]