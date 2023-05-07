import time
import random
from socket import *
from User import User
from threading import *
from TCPMessage import TCPNotification, TCPCommand

from Board import Board
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8000)

list_of_instances: [Board] = {}
user_id_counter = 0
board_id_counter = 0


class Monitor:
    def __init__(self):
        self.user_id_counter_lock = RLock()
        self.board_id_counter_lock = RLock()
        self.instance_lock = RLock()

        self.user_id_state = True
        self.board_id_state = True
        self.instance_state = True

        self.user_id_condition = Condition(self.user_id_counter_lock)
        self.board_id_condition = Condition(self.board_id_counter_lock)
        self.instance_condition = Condition(self.instance_lock)

    def lock_instance_array(self):
        with self.instance_lock:
            while not self.instance_state:
                self.instance_condition.wait()
            self.instance_state = False

    def unlock_instance_array(self):
        with self.instance_lock:
            self.instance_state = True
            self.instance_condition.notify_all()

    def lock_user_id_counter(self):
        with self.user_id_counter_lock:
            while not self.user_id_state:
                self.user_id_condition.wait()
            self.user_id_state = False

    def unlock_user_id_counter(self):
        with self.user_id_counter_lock:
            self.user_id_state = True
            self.user_id_condition.notify_all()

    def lock_board_id_counter(self):
        with self.board_id_counter_lock:
            while not self.board_id_state:
                self.board_id_condition.wait()
            self.board_id_state = False

    def unlock_board_id_counter(self):
        with self.board_id_counter_lock:
            self.board_id_state = True
            self.board_id_condition.notify_all()


monitor = Monitor()


def create_new_instance():
    monitor.lock_board_id_counter()
    global board_id_counter
    instance = Board(file='input.json', board_id=board_id_counter)
    board_id_counter += 1
    monitor.unlock_board_id_counter()

    monitor.lock_instance_array()
    list_of_instances[instance.id] = instance
    monitor.unlock_instance_array()
    print('new function is running...')


def get_list_of_instances():
    ret_val = []
    monitor.lock_instance_array()
    for instance in list_of_instances.values():
        ret_val.append({
            'id': instance.id,
            'started': instance.started,
            'users': [user.username for user in instance.users.values()],
        })
    monitor.unlock_instance_array()
    return ret_val


def notification_agent(c, user):
    while True:
        with user.lock:
            if len(user.message_queue) > 0:
                try:
                    c.send(json.dumps(user.message_queue).encode())
                except Exception as e:
                    print(e)
                    messages = []
                    for i in user.message_queue:
                        if isinstance(i, TCPNotification):
                            messages.append(i.make_message())
                        else:
                            messages.append(i)
                    c.send(json.dumps(messages).encode())
                user.message_queue = []


def game_agent(c, user, instance):
    with instance.lock:
        while not instance.started:
            instance.condition.wait()

    while True:
        with instance.lock:
            print('Instance lock acquired', user.username, instance.current_user.username)

            while instance.current_user.id != user.id:
                user.append_message(TCPNotification('notification', f'{instance.current_user.username} is playing'))

                # check for multiple conditions maybe
                print('Current user', instance.current_user.username)
                instance.condition.wait()
                print('Not blocking')
                # is callback called
                c.send(json.dumps(user.message_queue).encode())

            # message queue maybe
            # callback and turncb check maybe
            # c.send(f'N Your turn'.encode())
            possible_commands = instance.get_possible_commands(user)
            print('possible_commands', possible_commands, user.username)
            if len(possible_commands) == 0:
                user.append_message(TCPNotification('notification', 'You have no possible moves'))
            else:
                user.append_message(TCPNotification('notification', possible_commands))
                while True:
                    instance.condition.wait()
                    for command in possible_commands:
                        user.current_command = user.current_command.split(' ')
                        if command["type"] == user.current_command[0]:
                            command_args = []
                            if len(user.current_command) > 1:
                                command_args = user.current_command[1:]
                            command = {'type': user.current_command[0], "args": command_args}
                            print(command, user.current_command)
                            instance.turn(user, command)
                            break
                    else:
                        message = f'Unavailable command. Commands: {possible_commands}'
                        user.append_message(TCPNotification('notification', message))
                        continue
                    break
            instance.current_user = instance.determine_next_user()
            instance.condition.notify_all()


def agent(c, addr):
    c.send(f'{addr} connected'.encode())
    is_auth = False
    user = None
    instance: Board = None

    while True:
        request = TCPCommand.parse_command(c.recv(1024).decode())
        print('agent', request.command, request.args)
        if request.command == 'auth':
            username = request.args[0]
            password = request.args[1]
            monitor.lock_user_id_counter()
            global user_id_counter
            user = User(username=username, user_id=user_id_counter)
            notification_thread = Thread(target=notification_agent, args=(c, user))
            notification_thread.start()
            user_id_counter += 1
            monitor.unlock_user_id_counter()
            if not user.auth(password):
                c.send(TCPNotification('notification', 'Authentication Failed').make_message().encode())
            else:
                c.send(TCPNotification('notification', 'Authentication Successful').make_message().encode())
                is_auth = True
        else:

            if not is_auth:
                c.send(TCPNotification('notification', 'Authentication Required').make_message().encode())

            elif request.command == 'getinstances':
                ll = ''.join([str(i) for i in get_list_of_instances()])
                c.send(TCPNotification('notification', ll).make_message().encode())

            elif request.command == 'attach':
                choice = int(request.args[0])
                monitor.lock_instance_array()
                instance = list_of_instances[choice]
                game_thread = Thread(target=game_agent, args=(c, user, instance))
                game_thread.start()
                monitor.unlock_instance_array()

                with instance.lock:
                    if instance.started:
                        c.send(TCPNotification('notification', 'Game has already started').make_message().encode())
                        continue
                    instance.attach(user)
                c.send(TCPNotification('notification', 'Attached to board').make_message().encode())

            elif request.command == 'detach':

                if user.attached_to is None:
                    c.send(TCPNotification('notification', 'You are not attached to any board').make_message().encode())
                    continue

                with instance.lock:
                    instance.detach(user)

                c.send(TCPNotification('notification', 'Detached from board').make_message().encode())

            elif request.command == 'new':
                create_new_instance()
                c.send(TCPNotification('notification', 'New Board Created').make_message().encode())

            elif request.command == 'ready':
                if user.attached_to is None:
                    c.send(TCPNotification('notification', 'You are not attached to any board').make_message().encode())
                    continue

                with instance.lock:
                    instance.ready(user)

            elif request.command == 'getboardstate':
                try:
                    user.append_message(TCPNotification('notification', instance.getboardstate()))
                except:
                    pass

            elif request.command == 'getuserstate':
                try:
                    requested_user = instance.users[int(request.args[0])]
                    user.append_message(TCPNotification('notification', instance.getuserstate(requested_user)))
                except:
                    pass

            elif request.command == 'turn':
                with instance.lock:
                    if instance.current_user.id == user.id:
                        with user.lock:
                            user.current_command = request.args[0]
                        instance.condition.notify_all()
                    else:
                        user.append_message(TCPNotification('notification', 'Not your turn'))


if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    args = parser.parse_args()
    port = args.port
    s.bind(('localhost', int(port)))
    s.listen(5)

    create_new_instance()

    print('Server is running...')
    while True:
        c, addr = s.accept()
        print(f'Connection accepted from {addr}')
        t = Thread(target=agent, args=(c, addr))
        t.start()
