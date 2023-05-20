import argparse
import json
from socket import *
from .TCPMessage import TCPCommand, TCPNotification
from threading import Thread
from .app import singleton


@singleton
class Clients(object):
    def __init__(self):
        self.clients = {}

    # def __new__(cls):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(Clients, cls).__new__(cls)
    #     return cls.instance

    def add_client(self, client_id, client):
        self.clients[client_id] = client

    def get_client(self, client_id):
        return self.clients[client_id]

    def remove_client(self, client_id):
        del self.clients[client_id]


class Client:
    def __init__(self, s, port):
        self.s = s
        self.port = port
        self.attached = False
        self.ready = False

    def send_command(self, message):
        if isinstance(message, TCPCommand):
            self.s.send(message.make_command().encode())
        else:
            self.s.send(message.encode())

    def do_connect(self):
        """Connects to the server"""
        try:
            self.s.connect(('localhost', int(self.port)))
            message_thread = Thread(target=self.wait_message, args=())
            message_thread.start()
        except Exception as e:
            print(e)

    def do_auth(self, username):
        """Authenticates the user (args: username, password)"""
        self.send_command(TCPCommand("auth", [username]))

    def do_getinstances(self, _arg):
        """Gets the list of available instances"""
        self.send_command(TCPCommand("getinstances"))

    def do_createinstance(self, _arg):
        """Creates a new instance"""
        self.send_command(TCPCommand("new"))

    def do_attach(self, arg):
        """Attaches a user to the game (args: board_id)"""
        if not self.attached:
            self.send_command(TCPCommand("attach", [arg]))
            self.attached = True

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        if self.attached:
            self.send_command(TCPCommand("detach"))
            self.attached = False

    def do_ready(self):
        """Sets the user as ready"""
        self.send_command(TCPCommand("ready"))
        print('Waiting for other players to be ready...')

    def wait_message(self):
        print('Waiting for messages...')
        while True:
            messages = self.s.recv(4096).decode()
            try:
                if len(messages) > 0:
                    messages = json.loads(messages)
                else:
                    messages = []
                for message in messages:
                    message = TCPNotification.parse_message(message)
                    message.print_message()
            except Exception as e:
                print(e)
                print(f'Error while printing messages. Messages:{messages}')

    def do_turn(self, arg):
        self.send_command(TCPCommand("turn", [arg]))

    def do_getboardstate(self, _arg):
        """Gets the board state"""
        self.send_command(TCPCommand("getboardstate"))

    def do_getuserstate(self, arg):
        """Gets the user state (args: user_id)"""
        user_id = arg
        self.send_command(TCPCommand("getuserstate", [user_id]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    port = int(args.port)

    s = socket(AF_INET, SOCK_STREAM)

    Client(s, port).cmdloop()
