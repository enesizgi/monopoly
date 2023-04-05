from .Cell import Cell


class Teleport(Cell):

    def __init__(self, location, teleport_fee):
        super().__init__(location)
        self.teleport_fee = teleport_fee

    def __str__(self):
        return f'Teleport {self.location}'

    def teleport(self, user, destination):
        user.location = destination
        user.budget -= self.teleport_fee
        # TODO Check budget before teleporting


