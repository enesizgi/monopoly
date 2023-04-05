from Board import Board
from User import User

if __name__ == '__main__':
    board = Board('input.json')
    user1 = User(board.salary, 0)
    user2 = User(board.salary, 1)
    board.attach(user1, print, print)
    board.attach(user2, print, print)


