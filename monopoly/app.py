from socket import *
from .User import User
from threading import *
from .TCPMessage import TCPNotification, TCPCommand

from .Board import Board
import json
from .BankruptcyError import BankruptcyError


def singleton(cls):
    instance = None

    def wrapper(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return wrapper

@singleton
class Server(object):
    def __init__(self):
        self.users: [User] = {}
        self.list_of_instances: [Board] = {}
        self.user_id_counter = 0
        self.board_id_counter = 0

    # def __new__(cls):
    #     if not hasattr(cls, 'instance'):
    #         cls.instance = super(Server, cls).__new__(cls)
    #     return cls.instance

    def create_new_instance(self):
        """
        This function creates a new Board instance for users. They can attach to this instance.
        :return:
        """
        print('Creating new instance...')
        monitor.lock_board_id_counter()
        instance = Board(file='monopoly/input.json', board_id=self.board_id_counter)
        self.board_id_counter += 1
        monitor.unlock_board_id_counter()

        monitor.lock_instance_array()
        self.list_of_instances[instance.id] = instance
        monitor.unlock_instance_array()
        print('new function is running...', self.list_of_instances)

    def get_list_of_instances(self):
        """
        This functions lists all available board instances. Users can choose and attach one of them.
        :return:
        """
        ret_val = []
        monitor.lock_instance_array()
        for instance in self.list_of_instances.values():
            # Excluding games already have ended.
            if instance.started and len(instance.users) == 0:
                continue
            ret_val.append({
                'id': instance.id,
                'started': instance.started,
                'users': [user.username for user in instance.users.values()],
            })
        monitor.unlock_instance_array()
        return ret_val

    def notification_agent(self, c, user):
        """
        This method is run by a thread that is responsible for sending the message queue to the user.
        :param c: connection
        :param user: user instance
        """
        while True:
            # Lock the user instance and tries to send the message queue as a whole.
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
                    # Empty the message queue
                    user.message_queue = []

    def game_agent(self, c, user, instance):
        """
        This method is run by a thread that is responsible for keeping track of the game state and handles game commands
        from user.
        :param c: connection
        :param user: user instance
        :param instance: attached instance
        :return:
        """

        # Agent will wait until it is notified that the game is started
        with instance.lock:
            while not instance.started:
                instance.condition.wait()

        while True:
            # Lock the instance to be able to operate on it safely
            with instance.lock:

                # If the user does not have the turn
                while instance.current_user.id != user.id:
                    user.append_message(TCPNotification('notification', f'{instance.current_user.username} is playing'))
                    with user.lock:
                        user.possible_commands = []
                    instance.condition.wait()

                    # Other users has bankrupted or detached, current user wins
                    if len(instance.users) <= 1:
                        instance.detach(user)
                        user.append_message(TCPNotification('notification', 'You have won!'))
                        return
                    c.send(json.dumps(user.message_queue).encode())

                # If the user has the turn
                user.append_message(TCPNotification('notification', 'Your turn'))
                try:
                    possible_commands = instance.get_possible_commands(user)
                    with user.lock:
                        user.possible_commands = possible_commands

                # get_possible_commands method handles payments like rent and tax and it raises exception in case of
                # a bankruptcy
                except BankruptcyError:
                    instance.detach(user)
                    return
                print('possible_commands', possible_commands, user.username)

                # User does not have any possible moves
                if len(possible_commands) == 0:
                    user.append_message(TCPNotification('notification', 'You have no possible moves'))
                else:
                    user.append_message(TCPNotification('notification', possible_commands))
                    while True:
                        instance.condition.wait()
                        with user.lock:
                            for command in possible_commands:

                                # If the user who has the turn decides to detach
                                if user.current_command == "detach":
                                    return
                                if not isinstance(user.current_command, list):
                                    user.current_command = user.current_command.split(' ')

                                # The following code segment parses the command for the turn method of the instance
                                # and then calls the method.
                                if command["type"] == user.current_command[0]:
                                    command_args = []
                                    if len(user.current_command) > 1:
                                        command_args = user.current_command[1:]
                                    command = {'type': user.current_command[0], "args": command_args}
                                    print(command, user.current_command)
                                    instance.turn(user, command)
                                    break

                            # If the user tries to execute a command that is not applicable at the moment
                            else:
                                message = f'Unavailable command. Commands: {possible_commands}'
                                user.append_message(TCPNotification('notification', message))
                                continue
                            break
                instance.current_user = instance.determine_next_user()
                instance.condition.notify_all()

    def agent(self, c, addr):
        """
        This agent takes the necessary commands from client.py and changes user and board.
        Board logic is not included in this thread. It is in the game_agent.
        :param c: user connected from this socket.
        :param addr: user address
        :return:
        """
        c.send(json.dumps([TCPNotification('notification', f'{addr} connected').make_message()]).encode())
        is_auth = False
        user = None
        instance: Board | None = None

        while True:
            request = TCPCommand.parse_command(c.recv(1024).decode())
            print('agent', request.command, request.args)
            if request.command == 'auth':
                # Handle auth requests
                username = request.args[0]
                # password = request.args[1]
                monitor.lock_user_id_counter()
                user = User(username=username, user_id=self.user_id_counter)
                self.users[username] = user
                # Create a notification thread to be able to send users messages.
                notification_thread = Thread(target=self.notification_agent, args=(c, user))
                notification_thread.start()
                self.user_id_counter += 1
                monitor.unlock_user_id_counter()
                # if not user.auth(password):
                #     user.append_message(TCPNotification('notification', 'Authentication Failed'))
                # else:
                user.append_message(TCPNotification('notification', 'Authentication Successful'))
                is_auth = True
            else:

                if not is_auth:
                    c.send(json.dumps(
                        [TCPNotification('notification', 'Authentication Required').make_message()]).encode())

                elif request.command == 'getinstances':
                    ll = ''.join([str(i) for i in self.get_list_of_instances()])
                    user.append_message(TCPNotification('notification', ll))

                elif request.command == 'attach':
                    choice = int(request.args[0])
                    monitor.lock_instance_array()
                    instance = self.list_of_instances[choice]
                    game_thread = Thread(target=self.game_agent, args=(c, user, instance))
                    game_thread.start()
                    monitor.unlock_instance_array()

                    with instance.lock:
                        if instance.started:
                            user.append_message(TCPNotification('notification', 'Game has already started'))
                            continue
                        instance.attach(user)
                    user.append_message(TCPNotification('notification', 'Attached to board'))

                elif request.command == 'detach':

                    if user.attached_to is None:
                        user.append_message(TCPNotification('notification', 'You are not attached to any board'))
                        continue

                    with instance.lock:
                        instance.detach(user)
                        instance = None

                    user.append_message(TCPNotification('notification', 'Detached from board'))

                    monitor.lock_user_id_counter()
                    del self.users[user.username]
                    monitor.unlock_user_id_counter()

                elif request.command == 'new':
                    self.create_new_instance()
                    user.append_message(TCPNotification('notification', 'New Board Created'))

                elif request.command == 'ready':
                    if user.attached_to is None:
                        user.append_message(TCPNotification('notification', 'You are not attached to any board'))
                        continue

                    with instance.lock:
                        instance.ready(user)

                elif request.command == 'getboardstate' and user.attached_to is not None:
                    try:
                        user.append_message(TCPNotification('notification', instance.getboardstate()))
                    except:
                        pass

                elif request.command == 'getuserstate' and user.attached_to is not None:
                    try:
                        requested_user = instance.users[int(request.args[0])]
                        user.append_message(TCPNotification('notification', instance.getuserstate(requested_user)))
                    except:
                        pass

                elif request.command == 'turn' and user.attached_to is not None:
                    with instance.lock:
                        with user.lock:
                            if instance.current_user.id == user.id:
                                user.current_command = request.args[0]
                                instance.condition.notify_all()
                            else:
                                user.append_message(TCPNotification('notification', 'Not your turn'))


class Monitor:
    """
    This monitor class protects the counters and the list of instances
    """

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

# if __name__ == '__main__':
#     server1 = Server()
#     server2 = Server()
#     print(server1 is server2)
# Socket arrangements
# s = socket(AF_INET, SOCK_STREAM)
# args = parser.parse_args()
# port = args.port
# s.bind(('localhost', int(port)))
# s.listen(5)
#
# # Initially create an instance
# create_new_instance()
#
# print('Server is running...')
# while True:
#     # For each connection request, create a new agent responsible for user
#     c, addr = s.accept()
#     print(f'Connection accepted from {addr}')
#     t = Thread(target=agent, args=(c, addr))
#     t.start()
