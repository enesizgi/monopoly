import json
import sys
from threading import Thread, Lock, Condition

import websockets
from websockets.sync.server import serve
from Board import Board
from User import User
from TCPMessage import TCPNotification, TCPCommand

def singleton(cls):
    instance = None

    def wrapper(*args, **kwargs):
        nonlocal instance
        if instance is None:
            instance = cls(*args, **kwargs)
        return instance

    return wrapper

@singleton
class BoardManager:

    def __init__(self):
        self.boards = {}
        self.lock = Lock()
        self.newboard = Condition(self.lock)
        self.board_id_counter = 1

    def createboard(self):
        self.lock.acquire()
        b = Board(file='input.json', board_id=self.board_id_counter)
        self.boards[self.board_id_counter] = b
        self.board_id_counter += 1
        self.lock.release()

    def getboard(self, id):
        self.lock.acquire()
        if id not in self.boards:
            b = Board(file='input.json', board_id=id)
            self.boards[id] = b
        else:
            b = self.boards[id]
        self.lock.release()
        return b

    def getboards(self):
        self.lock.acquire()
        boards = list(self.boards.values())
        self.lock.release()
        return boards


class WRAgent(Thread):
    def __init__(self, conn, board):
        self.conn = conn
        self.board = board
        self.current = 0
        Thread.__init__(self)

    def run(self):
        oldmess = self.board.getmessages()
        self.current += len(oldmess)
        self.conn.send(json.dumps(oldmess))
        notexit = True
        while notexit:
            self.board.lock.acquire()
            self.board.newmess.wait()
            self.board.lock.release()
            oldmess = self.board.getmessages(current=self.current)
            self.current += len(oldmess)
            try:
                self.conn.send(json.dumps(oldmess))
            except:
                notexit = False


def serveconnection(sc):
    print("started")
    # get instance from socket path

    bm = BoardManager()

    if sc.request.path != '/':
        instance_id = sc.request.path.split('/')[-2]
        username = sc.request.path.split('/')[-1]

        board = bm.getboard(instance_id)
        user = User(username=username, user_id=len(board.users), initial_budget=board.salary)
        with board.lock:
            board.attach(user)

        wr = WRAgent(sc, board=board)
        wr.start()

    try:
        request = sc.recv()
        while request:
            request = TCPCommand.parse_command(request)

            if request.command == 'detach':
                with board.lock:
                    board.detach(user)
                break

            elif request.command == 'create_board':
                bm.createboard()
                boards = bm.getboards()
                sc.send(json.dumps([b.getboardstate() for b in boards]))

            elif request.command == 'get_boards':
                boards = bm.getboards()
                sc.send(json.dumps([b.getboardstate() for b in boards]))

            elif request.command == 'ready':
                with board.lock:
                    board.ready(user)

            elif request.command == 'turn':
                with board.lock:
                    cmd = {'type': request.args[0], 'args': request.args[1:]}
                    board.turn(user, cmd)

            request = sc.recv()

        # while inp:
        #     cr.newmessage(inp)
        #     print('waiting next')
        #     inp = sc.recv(1024)
        # print('client is terminating')
        # conn.close()
    except websockets.exceptions.ConnectionClosed:

        conn.close()
        wr.terminate()


HOST = ''
PORT = 5678
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.bind((HOST, PORT))

with serve(lambda nc: serveconnection(nc), host=HOST, port=PORT) as server:
    print("serving")
    server.serve_forever()

