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

    def send_command(self, message):
        if isinstance(message, TCPCommand):
            self.s.send(message.make_command().encode())
        else:
            self.s.send(message.encode())

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
        self.send_command(TCPCommand("auth", [username, password]))
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_getinstances(self, _arg):
        """Gets the list of available instances"""
        self.send_command(TCPCommand("getinstances"))
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_createinstance(self, _arg):
        """Creates a new instance"""
        self.send_command(TCPCommand("new"))
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_attach(self, arg):
        """Attaches a user to the game (args: board_id)"""
        self.send_command(TCPCommand("attach", [arg]))
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        self.send_command(TCPCommand("detach"))
        TCPNotification.parse_message(self.s.recv(1024).decode()).print_message()

    def do_ready(self, arg):
        """Sets the user as ready"""
        self.send_command(TCPCommand("ready"))
        print('Waiting for other players to be ready...')

        message_thread = Thread(target=self.wait_message, args=())
        message_thread.start()

    def wait_message(self):
        while True:
            messages = self.s.recv(1024).decode()
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
