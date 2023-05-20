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
    clients = Clients()
    client = clients.get_client(request.user.username)
    if 'create_new_board' in request.POST:
        server = Server()
        server.create_new_instance()
    elif 'quit' in request.POST:
        if client is not None:
            client.do_detach()
    if client is None:
        return render(request, 'home.html', context={'board_ids': board_ids, 'logged_in': False})
    return render(request, 'home.html', context={'board_ids': board_ids, 'logged_in': True})


def board(request, id):
    context = {'id': id}
    clients = Clients()
    client = clients.get_client(request.user.username)
    if client is not None:
        client.do_attach(id)
    context['username'] = request.user.username
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
                context[f'player{i+1}_y_text'] = player_positions[user1.location]['y']+30
                context[f'player{i+1}_username'] = user1.username



            context['state'] = user.get()
    except:
        print('Exception')
        pass
    if request.method == 'POST':
        print(request.POST)
        if 'ready' in request.POST and request.POST['ready'] == 'ready' and client is not None:
            client.do_ready()
            if isinstance(user, User):
                user.set_ready(True)
        elif 'move' in request.POST and client is not None:
            command = request.POST['move']
            if 'args' in request.POST:
                command += ' ' + request.POST['args'].strip()
            client.do_turn(command)
    if isinstance(user, User) and user.ready:
        print('User is ready')
        context['is_ready'] = True
    else:
        print('User is not ready')
        context['is_ready'] = False

    # Player positions

    if client is not None:
        context['logged_in'] = False
    else:
        context['logged_in'] = True
    return render(request, 'board.html', context=context)
