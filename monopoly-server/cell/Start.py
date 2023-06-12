from cell.Cell import Cell


class Start(Cell):

    """
    This class represents a start cell in the board.
    """

    def __init__(self, location, salary, cell_type):
        super().__init__(location, cell_type)
        self.salary = salary
        self.name = 'Start'

    def __str__(self):
        return f'Start {self.location}'

    def getstate(self):
        return {
            'location': self.location,
            'salary': self.salary,
            'type': 'Start'
        }
