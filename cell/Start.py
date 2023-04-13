from .Cell import Cell


class Start(Cell):

    def __init__(self, location, salary, cell_type):
        super().__init__(location, cell_type)
        self.salary = salary

    def __str__(self):
        return f'Start {self.location}'

    def getstate(self):
        return {
            'location': self.location,
            'salary': self.salary,
            'type': 'Start'
        }
