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


lock1 = Lock()
cond = Condition(lock1)


class Monitor:
    def __init__(self):
        self.lock = Lock()

    def insert_instance(self, instance):
        with self.lock:
            global list_of_instances
            list_of_instances[instance.id] = instance

    def increase_counter(self):
        with self.lock:
            global user_id_counter
            user_id_counter += 1

    def decrease_counter(self):
        with self.lock:
            global user_id_counter
            user_id_counter -= 1

    def create_board(self, file, sock):
        with self.lock:
            global board_id_counter
            board = Board(file=file, sock=sock, board_id=board_id_counter)
            board_id_counter += 1
            return board

    def create_user(self, username):
        with self.lock:
            global user_id_counter
            user = User(username=username, user_id=user_id_counter)
            user_id_counter += 1
            return user

    def attach_user(self, board_id, user):
        global list_of_instances
        with self.lock:
            inst = list_of_instances[board_id]
            if inst.get_user_count() == 4:
                return False
            inst.attach(user)
            if inst.get_user_count() == 4:
                new()
            return inst


monitor = Monitor()


def new():
    # randomly create port from 1000 ro 9999 except 1234 use random
    port = random.randint(1235, 9999)

    s = socket(AF_INET, SOCK_STREAM)
    s.bind(('localhost', port))

    instance = monitor.create_board('input.json', s)
    # list_of_instances.append(instance)
    monitor.insert_instance(instance)
    print('new function is running...')
    instance.start()


def get_list_of_instances():
    return list_of_instances


# list_of_instances[i].

def client_thread(port):
    with lock1:
        s = socket(AF_INET, SOCK_STREAM)
        input('Press enter to connect to server')
        while True:
            try:
                s.connect(('localhost', int(port)))
                break
            except:
                time.sleep(1)

        print(s.recv(1024).decode())
        username, password = input('Enter username and password with a space: ').split(' ')
        s.send(f'{username} {password}'.encode())

        # get the list of available instances
        print(s.recv(1024).decode())

        # time.sleep(1)

        command = input('Enter room: ')
        s.send(command.encode())

        cond.wait()



def agent(c, addr):
    global user_id_counter
    print('Got connection from', addr)
    c.send('Provide Authentication'.encode())
    username, password = c.recv(1024).decode().split(' ')
    user = monitor.create_user(username=username)
    if not user.auth(password):
        c.send('Authentication Failed'.encode())
        c.close()

    ll = ''.join([list_of_instances[i].getboardinfo() for i in list_of_instances.keys()])
    c.send(f"Auth successful. Select room to join.\n{ll}".encode())

    # send the enumareted list of instances
    choice = int(c.recv(1024).decode())
    print(choice)

    monitor.attach_user(choice, user)

    # while choice != '':
    #     if choice == 'P':
    #         for instance in list_of_instances:
    #             if instance.get_user_count() < 4:
    #                 inst = instance
    #                 instance.attach(user)
    #                 break
    #         else:
    #             new()
    #
    #     elif choice == 'J':
    #         pass
    #     elif choice == 'L':
    #         c.send(str(list_of_instances).encode())
    #
    #     choice = c.recv(1024).decode()
    #     print(choice)

    c.close()


if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    args = parser.parse_args()
    port = args.port
    s.bind(('localhost', int(port)))
    s.listen(5)

    new()

    client = Thread(target=client_thread, args=(port,))
    client.start()

    client1 = Thread(target=client_thread, args=(port,))
    client1.start()

    while True:
        c, addr = s.accept()
        t = Thread(target=agent, args=(c, addr))
        t.start()
