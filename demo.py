from Board import Board
from User import User
import cmd


class Demo(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.board = Board("input.json")
        self.prompt = "demo> "

    def do_attach(self, arg):
        """Attaches a user to the game (args: user_id, username)"""

        arg = arg.split()
        user_id = arg[0]
        username = arg[1]
        user = User(self.board.salary, user_id, username=username)
        self.board.attach(user, lambda x: x, user.notifyTurn)
        print("User attached")
        # print(self.board.users)

    def do_detach(self, arg):
        """Detaches a user from the game (args: user_id)"""
        user_id = arg
        user = self.board.users[user_id]
        self.board.detach(user)
        print("User detached")
        print(self.board.users)

    def do_getboardstate(self, _arg):
        """Gets the board state"""
        print(self.board.getboardstate())

    def do_getuserstate(self, arg):
        """Gets the user state (args: user_id)"""
        user_id = arg
        user = self.board.users[user_id]
        print(self.board.getuserstate(user))

    def do_turn(self, arg):
        """Applies turn commands (args: user_id, command)"""
        if self.board.started:
            arg = arg.split()
            user_id = arg[0]
            command = arg[1]
            user = self.board.determine_next_user()
            if user_id != user.id:
                print("The user with id {} has the turn".format(user.id))
                return

            possible_commands = self.board.get_possible_commands(user)
            flag = False
            for possible_command in possible_commands:
                if possible_command['type'] == command:
                    flag = True
                    break

            if not flag:
                print("The command {} is not possible".format(command))
                return

            self.board.turn(user, {'type': command})

    def do_move(self, arg):
        """Moves a user to a specific location (args: user_id, location)"""
        arg = arg.split()
        user_id = arg[0]
        location = int(arg[1])
        user = self.board.users[user_id]
        user.location = location
        print(self.board.getuserstate(user))

    def do_getturn(self, arg):
        """Gets the turn for the user (args: user_id)"""
        user = self.board.determine_next_user()
        print(f'The user with id {user.id} has the turn')

    def do_getcommands(self, arg):
        """Gets the possible commands for the user (args: user_id)"""
        if self.board.started:
            user_id = arg
            user = self.board.determine_next_user()
            if user_id == user.id:
                print(self.board.get_possible_commands(user))

            else:
                print("The user with id {} has the turn".format(user.id))
        else:
            print("The game has not started yet")

    def do_ready(self, arg):
        """User makes it state ready. (args: user_id)"""
        user_id = arg[0]
        user = self.board.users[user_id]
        self.board.ready(user)

    def do_start(self, _arg):
        """Starts the game"""
        if all(user.ready for user in self.board.users.values()):
            self.board.start()
            print("Game started")


if __name__ == '__main__':
    Demo().cmdloop()
