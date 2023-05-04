import json

class TCPNotification:

    def __init__(self, message_type, message):
        self.message_type = message_type
        self.message = message

    def make_message(self):
        return json.dumps({"type": self.message_type, "message": self.message})

    @staticmethod
    def parse_message(message):
        message = json.loads(message)
        return TCPNotification(message["type"], message["message"])

    def print_message(self):
        print(self.message)

class TCPCommand:

    def __init__(self, command, args=None):
        self.command = command
        self.args = args

    def make_command(self):
        return json.dumps({'command': self.command, 'args': self.args})

    @staticmethod
    def parse_command(command):
        command = json.loads(command)
        return TCPCommand(command['command'], command['args'])

