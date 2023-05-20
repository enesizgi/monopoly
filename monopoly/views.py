from django.shortcuts import render
from .client import Clients, Client
from .app import Server


# Create your views here.

def home(request):
    server = Server.__new__(Server)
    board_ids = list(map(lambda x: x.id, server.list_of_instances.values()))
    print(board_ids, server.list_of_instances)
    return render(request, 'home.html', context={'board_ids': board_ids})

def board(request, id):
    clients = Clients.__new__(Clients)
    client = clients.get_client(request.user.username)
    board = Server.__new__(Server).list_of_instances[id]
    client.do_attach(id)
    return render(request, 'board.html', context={'id': id})