from .Cell import Cell


class Teleport(Cell):

    def __init__(self, location, teleport_fee, cell_type):
        super().__init__(location, cell_type)
        self.teleport_fee = teleport_fee

    def __str__(self):
        return f'Teleport {self.location}'

    def teleport(self, user, destination):
        print(f'{user.username} is teleporting to {destination} for {self.teleport_fee}.')
        user.location = destination
        user.budget -= self.teleport_fee

    def getstate(self):
        return {
            'location': self.location,
            'teleport_fee': self.teleport_fee,
            'type': 'Teleport'
        }

