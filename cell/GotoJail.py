from .Cell import Cell


class GotoJail(Cell):

    def __init__(self, location, cell_type):
        super().__init__(location, cell_type)

    def __str__(self):
        return f'GotoJail {self.location}'

    def goto_jail(self, user, jail_location):
        user.location = jail_location
        user.inJail = True

    def getstate(self):
        return {
            "location": self.location,
            "type": "GotoJail"
        }

