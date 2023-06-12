from cell.Cell import Cell
from User import player_positions


class Teleport(Cell):

    """
    This class represents a teleport cell in the board.
    """

    def __init__(self, location, teleport_fee, cell_type):
        super().__init__(location, cell_type)
        self.teleport_fee = teleport_fee
        self.name = 'Teleport'

    def __str__(self):
        return f'Teleport {self.location}'

    def get_possible_cells_to_teleport(self, board, user):
        """
        This method returns the possible cells to teleport.
        :param board: Board object
        :return: list
        """
        possible_cells = []
        for cell in board.cells:
            if cell.type == 'property' and cell.owner_id == user.id:
                possible_cells.append({'location': cell.location, 'name': cell.name})
            elif cell.type == 'property' and cell.owner_id == -1:
                possible_cells.append({'location': cell.location, 'name': cell.name})
            elif cell.type == 'chance':
                possible_cells.append((cell.location, 'Chance'))
            elif cell.type == 'start':
                possible_cells.append((cell.location, 'Start'))
        return possible_cells

    def teleport(self, user, destination):
        """
        This method teleports the user to the destination.
        :param user: User object
        :param destination: int
        :return:
        """
        user.location = destination
        user.location_x = player_positions[destination]['x']
        user.location_y = player_positions[destination]['y']
        user.budget -= self.teleport_fee

    def getstate(self):
        return {
            'location': self.location,
            'teleport_fee': self.teleport_fee,
            'type': 'Teleport'
        }

