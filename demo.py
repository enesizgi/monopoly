import json
from typing import List

from Board import Board
from User import User
import cmd


class Demo(cmd.Cmd):

    def __init__(self):
        super().__init__()
        self.board = Board("input.json")
        self.prompt = "demo> "

    def do_attach(self, arg):
        '''Attaches a user to the game (args: user_id, username)'''

        arg = arg.split()
        user_id = arg[0]
        username = arg[1]
        user = User(self.board.salary, user_id, username=username)
        self.board.attach(user, lambda x:x, user.notifyTurn)
        print("User attached")
        # print(self.board.users)

    def do_detach(self, arg):
        '''Detaches a user from the game (args: user_id)'''
        user_id = arg
        user = self.board.users[user_id]
        self.board.detach(user)
        print("User detached")
        print(self.board.users)

    def do_getboardstate(self, arg):
        '''Gets the board state'''
        print(self.board.getboardstate())

    def do_getuserstate(self, arg):
        '''Gets the user state (args: user_id)'''
        user_id = arg
        user = self.board.users[user_id]
        print(self.board.getuserstate(user))

    def do_turn(self, arg):
        '''Applies turn commands (args: user_id, command)'''
        arg = arg.split()
        user_id = arg[0]
        command = arg[1]
        user = self.board.users[user_id]
        self.board.turn(user, { 'type': command })


    def do_ready(self, arg):
        '''User makes it state ready. (args: user_id)'''
        user_id = arg[0]
        user = self.board.users[user_id]
        self.board.ready(user)
        print(self.board.started)

if __name__ == '__main__':
    Demo().cmdloop()
