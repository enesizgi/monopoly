import json

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import JsonResponse

from monopoly.forms import SignUpForm

# Create your views here.

player_positions = [
    {'x': 20, 'y': 80},
    {'x': 180, 'y': 80},
    {'x': 340, 'y': 80},
    {'x': 500, 'y': 80},
    {'x': 660, 'y': 80},
    {'x': 680, 'y': 240},
    {'x': 680, 'y': 400},
    {'x': 680, 'y': 560},
    {'x': 680, 'y': 720},
    {'x': 520, 'y': 720},
    {'x': 360, 'y': 720},
    {'x': 200, 'y': 720},
    {'x': 20, 'y': 720},
    {'x': 20, 'y': 560},
    {'x': 20, 'y': 400},
    {'x': 20, 'y': 240},
]

def home(request):

    # get user

    return render(request, 'home.html', context={'user': request.user})

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

def board(request, id):
    return render(request, 'board.html', context={'id': id, 'user': request.user, 'player_positions': json.dumps(player_positions)})
