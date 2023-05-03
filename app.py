import time
import random
from socket import *
from User import User
from threading import *

from Board import Board
import argparse

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


def agent(c, addr):
    c.send(f'{addr} connected'.encode())
    is_auth = False
    user = None
    instance: Board = None

    request = c.recv(1024).decode()
    while request != '':
        request = request.split(' ')
        if request[0] == 'auth':
            username = request[1]
            password = request[2]
            monitor.lock_user_id_counter()
            global user_id_counter
            user = User(username=username, user_id=user_id_counter)
            user_id_counter += 1
            monitor.unlock_user_id_counter()
            if not user.auth(password):
                c.send('Authentication Failed'.encode())
                c.close()
            else:
                c.send('Authentication Successful'.encode())
                is_auth = True
        else:

            if not is_auth:
                c.send('You are not authenticated. Please authenticate!'.encode())

            elif request[0] == 'getinstances':
                ll = ''.join([str(i) for i in get_list_of_instances()])
                c.send(ll.encode())

            elif request[0] == 'attach':
                choice = int(request[1])
                monitor.lock_instance_array()
                instance = list_of_instances[choice]
                monitor.unlock_instance_array()

                with instance.lock:
                    if instance.started:
                        c.send('Board has been started'.encode())
                        continue
                    instance.attach(user)
                c.send('Attached'.encode())

            elif request[0] == 'detach':

                if user.attached_to is None:
                    c.send('You are not attached to any board'.encode())
                    continue

                with instance.lock:
                    instance.detach(user)

                c.send('Detached'.encode())

            elif request[0] == 'new':
                create_new_instance()
                c.send('New Board Created'.encode())

            elif request[0] == 'ready':
                if user.attached_to is None:
                    c.send('You are not attached to any board'.encode())
                    continue

                with instance.lock:
                    instance.ready(user)
                    while not instance.started:
                        instance.condition.wait()

                c.send('Game Started'.encode())
                break

        request = c.recv(1024).decode()

    while True:
        with instance.lock:
            current_turn = instance.determine_next_user()

            while current_turn.id != user.id:
                c.send(f'{current_turn.username} is playing'.encode())

                # check for multiple conditions maybe
                instance.condition.wait()

            # message queue maybe
            # callback and turncb check maybe
            c.send(f'Your turn'.encode())
            possible_commands = instance.get_possible_commands(user)
            c.send(f'Possible Commands: {possible_commands}'.encode())
            command = c.recv(1024).decode()

            # turn here ...


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
        t = Thread(target=agent, args=(c, addr))
        t.start()