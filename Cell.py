class Cell:
    def __init__(self, cell, location):
        self.type = cell['type']
        self.name = cell.get('name', None)
        # self.cell_id = cell.get('cell', None)
        self.color = cell.get('color', None)
        self.price = cell.get('price', None)
        self.rents = cell.get('rents', None)
        self.level = 0
        self.location = location

    def __str__(self):
        return f'{self.name} {self.type} {self.color} {self.price} {self.rents} {self.level} {self.location}'
