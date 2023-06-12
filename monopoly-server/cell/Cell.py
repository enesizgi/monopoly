class Cell:

    """
    This class represents a cell in the board.
    """
    def __init__(self, location=None, type=None):
        self.location = location
        self.type = type

    def getstate(self):
        return self.__dict__

    def __str__(self):
        return f'{self.name} {self.type} {self.color} {self.price} {self.rents} {self.level} {self.location}'
