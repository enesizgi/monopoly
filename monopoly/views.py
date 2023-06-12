import json

from django.shortcuts import render
from django.http import JsonResponse

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

def board(request, id):
    return render(request, 'board.html', context={'id': id, 'user': request.user, 'player_positions': json.dumps(player_positions)})

def fetch_available_boards(request):
    return JsonResponse([
        {'id': 1, 'status': 'available', 'users': ['user1', 'user2']},
        {'id': 2, 'status': 'available', 'users': ['user3', 'user4']},
    ], safe=False)