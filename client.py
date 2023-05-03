import argparse
from cmd import Cmd
from socket import *


class Client(Cmd):
    def __init__(self, s, port):
        super().__init__()
        self.prompt = "client> "
        self.s = s
        self.port = port

    def do_connect(self, arg):
        """Connects to the server"""
        self.s.connect(('localhost', int(self.port)))
        print(self.s.recv(1024).decode())

    def do_auth(self, arg):
        """Authenticates the user (args: username, password)"""
        username, password = arg.split(' ')
        self.s.send(f'auth {username} {password}'.encode())
        print(self.s.recv(1024).decode())

    def do_getinstances(self, arg):
        """Gets the list of available instances"""
        request = 'getinstances'
        self.s.send(request.encode())
        print(self.s.recv(1024).decode())

    def do_attach(self, arg):
        """Attaches a user to the game (args: board_id)"""
        self.s.send(f'attach {arg}'.encode())
        print(self.s.recv(1024).decode())

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        self.s.send(f'detach {arg}'.encode())
        print(self.s.recv(1024).decode())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    port = int(args.port)

    s = socket(AF_INET, SOCK_STREAM)

    Client(s, port).cmdloop()


