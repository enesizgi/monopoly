from datetime import timezone

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .client import Clients, Client
from socket import socket, AF_INET, SOCK_STREAM
from .apps import PORT


@receiver(user_logged_in)
def user_logged_in_receiver(sender, request, user, **kwargs):
    # Perform your extra actions here
    # For example, you can log the login activity, update user's last login timestamp, etc.
    # You can access the logged-in user using the 'user' argument
    print('User logged in! {}'.format(user.username))
    clients = Clients()
    s = socket(AF_INET, SOCK_STREAM)
    client = Client(s, PORT)
    client.do_connect()
    client.do_auth(user.username)
    clients.add_client(user.username, client)

    # Example: Log the login activity


@receiver(user_logged_out)
def user_logged_out_receiver(sender, request, user, **kwargs):
    client = Clients().get_client(user.username)
    if client is not None:
        client.do_detach()