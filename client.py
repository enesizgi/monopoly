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
        try:
            self.s.connect(('localhost', int(self.port)))
        except Exception as e:
            print(e)
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

    def do_createinstance(self, arg):
        """Creates a new instance"""
        self.s.send('new'.encode())
        print(self.s.recv(1024).decode())

    def do_attach(self, arg):
        """Attaches a user to the game (args: board_id)"""
        self.s.send(f'attach {arg}'.encode())
        print(self.s.recv(1024).decode())

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        self.s.send(f'detach {arg}'.encode())
        print(self.s.recv(1024).decode())

    def do_ready(self, arg):
        """Sets the user as ready"""
        self.s.send('ready'.encode())
        print('Waiting for other players to be ready...')
        msg = self.s.recv(1024).decode()
        print(msg)
        # print(self.s.recv(1024).decode())

        self.wait_notification()

    def wait_notification(self):
        notification = self.s.recv(1024).decode()
        print(notification)
        while notification.startswith('N'):
            notification = self.s.recv(1024).decode()
            print('Notification: ', notification)

    def do_turn(self, arg):
        s.send(arg.encode())
        self.wait_notification()






if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    port = int(args.port)

    s = socket(AF_INET, SOCK_STREAM)

    Client(s, port).cmdloop()


