from typing import List

from Board import Board
from User import User


# def turncb(user, board, commands: List[dict]):
#     print('Commands:')
#     for i, command in enumerate(commands):
#         print(f'{i}: {command["name"]}')
#
#     command = int(input("Select possible command (0,1,2...)"))
#     if commands[command]['type'] == 'roll':
#         board.turn(user, {'type': 'roll'})
#     elif commands[command]['type'] == 'buy':
#         board.turn(user, {'type': 'buy', 'property': commands[command]['property']})





if __name__ == '__main__':
    board = Board('input.json')
    user1 = User(board.salary, 0)
    user2 = User(board.salary, 1)
    board.attach(user1, print, user1.notifyTurn)
    board.attach(user2, print, user2.notifyTurn)
    board.ready(user1)
    board.ready(user2)
    board.start()
