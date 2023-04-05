from .Cell import Cell


class GotoJail(Cell):

    def __init__(self, location):
        super().__init__(location)

    def __str__(self):
        return f'GotoJail {self.location}'

    def goto_jail(self, user, jail_location):
        user.location = jail_location
        user.jail = True