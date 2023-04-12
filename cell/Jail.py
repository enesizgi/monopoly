from .Cell import Cell


class Jail(Cell):

    def __init__(self, location, jail_bail: int):
        super().__init__(location)
        self.jail_bail = jail_bail

    def __str__(self):
        return f'Jail {self.location}'

    def pay_bail(self, user):
        user.budget -= self.jail_bail
        user.inJail = False
        user.jailTurns = 0
