from django.apps import AppConfig
from .app import Server
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

ready_count = 0

def create_server():
    print('Creating server...')
    s = socket(AF_INET, SOCK_STREAM)
    # args = parser.parse_args()
    port = 1219
    s.bind(('localhost', int(port)))
    s.listen(5)

    server = Server()
    # Initially create an instance
    server.create_new_instance()

    print('Server is running...')
    while True:
        # For each connection request, create a new agent responsible for user
        c, addr = s.accept()
        print(f'Connection accepted from {addr}')
        t = Thread(target=server.agent, args=(c, addr))
        t.start()


class MonopolyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monopoly'

    def ready(self):
        print('Monopoly app is ready!')
        import monopoly.signals
        global ready_count
        if ready_count == 0:
            t = Thread(target=create_server)
            t.start()
            ready_count += 1
