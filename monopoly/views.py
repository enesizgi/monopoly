from django.shortcuts import render
from .client import Clients, Client
from .app import Server
from .User import User

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


# Create your views here.

def home(request):
    server = Server()
    board_ids = list(map(lambda x: x.id, server.list_of_instances.values()))
    print(board_ids, server.list_of_instances)
    return render(request, 'home.html', context={'board_ids': board_ids})


def board(request, id):
    context = {'id': id}
    clients = Clients()
    client = clients.get_client(request.user.username)
    context['username'] = request.user.username
    client.do_attach(id)
    user = None
    try:
        instance = Server().list_of_instances[id]
        user = filter(lambda x: x.username == request.user.username, instance.users.values())
        user = list(user)[0]
        if isinstance(user, User):
            context['possible_commands'] = list(map(lambda x: x['type'], user.possible_commands))
            users = list(instance.users.values())
            for i in range(len(users)):
                user1 = users[i]
                context[f'player{i + 1}_x'] = player_positions[user1.location]['x'] + 20*i
                context[f'player{i + 1}_y'] = player_positions[user1.location]['y']
    except:
        print('Exception')
        pass
    if request.method == 'POST':
        print(request.POST)
        if 'ready' in request.POST and request.POST['ready'] == 'ready':
            client.do_ready()
            if isinstance(user, User):
                user.set_ready(True)
        elif 'move' in request.POST:
            client.do_turn(request.POST['move'])
    if isinstance(user, User) and user.ready:
        print('User is ready')
        context['is_ready'] = True
    else:
        print('User is not ready')
        context['is_ready'] = False

    # Player positions


    return render(request, 'board.html', context=context)
