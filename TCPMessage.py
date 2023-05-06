import json

class TCPNotification:

    def __init__(self, message_type, message):
        self.message_type = message_type
        self.message = message

    def make_message(self):
        return json.dumps({"type": self.message_type, "message": self.message})

    @staticmethod
    def parse_message(message):
        try:
            message = json.loads(message)
            print(message)
            return TCPNotification(message["type"], message["message"])
        except Exception as e:
            print(e)

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
        try:
            print(command)
            command = json.loads(command)
            print(command)
            return TCPCommand(command['command'], command['args'])
        except Exception as e:
            print(e)

