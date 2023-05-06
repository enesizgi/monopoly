import argparse
import json
from cmd import Cmd
from socket import *
from TCPMessage import TCPCommand, TCPNotification
from threading import Thread


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
        self.s.send(TCPCommand("auth", [username, password]).make_command().encode())
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_getinstances(self, arg):
        """Gets the list of available instances"""
        self.s.send(TCPCommand("getinstances").make_command().encode())
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_createinstance(self, arg):
        """Creates a new instance"""
        self.s.send(TCPCommand("new").make_command().encode())
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_attach(self, arg):
        """Attaches a user to the game (args: board_id)"""
        self.s.send(TCPCommand("attach", [arg]).make_command().encode())
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        self.s.send(TCPCommand("detach").make_command().encode())
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_ready(self, arg):
        """Sets the user as ready"""
        self.s.send(TCPCommand("ready").make_command().encode())
        print('Waiting for other players to be ready...')
        # m = self.s.recv(1024).decode()
        # TCPNotification.parse_message(m).print_message()
        # print(self.s.recv(1024).decode())

        message_thread = Thread(target=self.wait_message, args=())
        message_thread.start()

    def wait_message(self):
        while True:
            messages = self.s.recv(1024).decode()
            print(messages)
            # messages = []
            if len(messages) > 0:
                messages = json.loads(messages)
            else:
                messages = []
            for message in messages:
                message = TCPNotification.parse_message(message)
                message.print_message()
            # message = TCPNotification.parse_message(self.s.recv(1024).decode())
        # message.print_message()
        # while message.message_type == "notification":
        #     message = TCPNotification.parse_message(self.s.recv(1024).decode())
        #     message.print_message()


    def do_turn(self, arg):
        s.send(TCPCommand("turn", [arg]).make_command().encode())
        #self.wait_message()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    port = int(args.port)

    s = socket(AF_INET, SOCK_STREAM)

    Client(s, port).cmdloop()


