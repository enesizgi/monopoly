from .Cell import Cell


class Start(Cell):

    def __init__(self, location, salary):
        super().__init__(location)
        self.salary = salary

    def __str__(self):
        return f'Start {self.location}'
