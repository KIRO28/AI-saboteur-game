from une_ai.models import GridMap
from card import PathCard
import random

GOAL_LOCATIONS = [(14, 8), (14, 10), (14, 12)]


class GameBoard():
    DIRECTIONS = ['north', 'south', 'east', 'west']
    OPPOSITES = {
        'north': 'south',
        'south': 'north',
        'east': 'west',
        'west': 'east',
    }
    DIRECTION_MOVEMENT: dict[str, tuple[int, int]] = {
        'north': (0, -1),
        'south': (0, 1),
        'east': (1, 0),
        'west': (-1, 0),
    }

    def __init__(self, board: GridMap | None = None):
        if board is not None:
            assert isinstance(board, GridMap), "board is not correct gridmap"
            self._board = board
            return
        self._board = GridMap(20, 20, None)

        start_card = PathCard.cross_road(special_card='start')
        goal_cards = []
        gold_idx = random.choice([0, 1, 2])
        for i in range(3):
            if gold_idx == i:
                label = 'gold'
            else:
                label = 'goal'
            goal_cards.append(PathCard.cross_road(special_card=label))

        self._board.set_item_value(6, 10, start_card)
        goal_locations = [(14, 8), (14, 10), (14, 12)]
        for i, goal in enumerate(goal_cards):
            self._board.set_item_value(goal_locations[i][0], goal_locations[i][1], goal)

    def get_board(self):
        return self._board

    def can_place_card_at(self, x, y, path_card):
        """Check if the card can be placed at (x, y) by verifying neighboring exits."""
        direction_offsets = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0),
        }
        opposite_directions = {
            'north': 'south',
            'south': 'north',
            'east': 'west',
            'west': 'east',
        }

        path_exits = path_card.get_exits()

        # Check all neighboring positions
        for direction, (dx, dy) in direction_offsets.items():
            adj_x, adj_y = x + dx, y + dy
            adj_card = self._board.get_item_value(adj_x, adj_y)

            if adj_card is not None:  # There is a neighboring card
                adj_exits = adj_card.get_exits()
                opposite_dir = opposite_directions[direction]

                # This is to ensure that the card being placed and the adjacent card have matching exits
                if direction in path_exits and opposite_dir in adj_exits:
                    continue  # Valid connection
                elif direction not in path_exits and opposite_dir in adj_exits:
                    return False  # Neighboring card expects a connection, but none exists
        return True

    def try_place_with_rotation(self, x, y, path_card):
        """Try to place the card at (x, y) by rotating it up to 3 times."""
        for _ in range(4):  # Trying all rotations (0°, 90°, 180°, 270°)
            if self.can_place_card_at(x, y, path_card):
                # Place the card if it fits
                self._board.set_item_value(x, y, path_card)
                return True
            # Rotate the card and try again
            path_card.turn_card()
        return False  # Couldn't place the card after all rotations

    def add_path_card(self, x, y, path_card):
        assert isinstance(path_card, PathCard), "The parameter path_card must be an instance of PathCard"
        assert 0 <= x < 20, "The x coordinate must be 0 <= x < 20"
        assert 0 <= y < 20, "The y coordinate must be 0 <= y < 20"
        assert self._board.get_item_value(x, y) is None, f"There is already a card on the board at ({x}, {y})"

        # Debugger to display the initial state of the card's exits before rotation attempts
        print(f"Trying to place card at ({x}, {y}) with initial exits: {path_card.get_exits()}")

        # Trying to place the card with different rotations
        for rotation in range(4):
            print("Checking neighboring cards and their exits:")
            for direction, (dx, dy) in GameBoard.DIRECTION_MOVEMENT.items():
                adj_x, adj_y = x + dx, y + dy
                adj_card = self._board.get_item_value(adj_x, adj_y)
                if adj_card is not None:
                    print(f"Neighbor at ({adj_x}, {adj_y}) in direction {direction} has exits: {adj_card.get_exits()}")
                else:
                    print(f"No neighbor in direction {direction}")

            # Rotate the card for the next attempt
            path_card.turn_card()
        raise Exception(f"Could not place card at ({x}, {y}), all rotations failed.")

    def future_state(self, cur_location: tuple[int, int], direction: str):
        cur_x, cur_y = cur_location
        new_x, new_y = (cur_x + GameBoard.DIRECTION_MOVEMENT[direction][0],
                        cur_y + GameBoard.DIRECTION_MOVEMENT[direction][1])

        try:
            value: PathCard | None = self._board.get_item_value(new_x, new_y)
            new_location = (new_x, new_y)
        except:
            value = None
            new_location = None

        return value, new_location

    def remove_path_card(self, x, y):
        assert x >= 0 and x < 20, "The x coordinate must be 0 <= x < 20"
        assert y >= 0 and y < 20, "The y coordinate must be 0 <= y < 20"
        assert self._board.get_item_value(x, y) is not None and not self._board.get_item_value(x,
                                                                                               y).is_special_card(), "There is no valid card to remove at coordinates ({0}, {1})".format(
            x, y)

        self._board.set_item_value(x, y, None)

    def is_connected(self, goal_location):
        """
        Check if there is a valid path between the start card and the specified goal location.
        We will use BFS (or DFS) to find if there's a connected path.
        """
        start_x, start_y = 6, 10  # Starting card position
        goal_x, goal_y = goal_location

        visited = set()
        queue = [(start_x, start_y)]

        while queue:
            cur_x, cur_y = queue.pop(0)
            if (cur_x, cur_y) == (goal_x, goal_y):
                return True  # A path to the goal has been found

            # Mark the current position as visited
            visited.add((cur_x, cur_y))

            # Get the current card and its exits
            cur_card = self._board.get_item_value(cur_x, cur_y)
            if cur_card is None:
                continue

            exits = cur_card.get_exits()
            for direction in exits:
                # Find the adjacent card based on the current exit direction
                dx, dy = GameBoard.DIRECTION_MOVEMENT[direction]
                next_x, next_y = cur_x + dx, cur_y + dy

                # Check if the next card exists and is not visited
                if (next_x, next_y) not in visited:
                    next_card = self._board.get_item_value(next_x, next_y)
                    if next_card is not None:
                        # Check if the next card has a matching exit in the opposite direction
                        opposite_dir = GameBoard.OPPOSITES[direction]
                        if opposite_dir in next_card.get_exits():
                            queue.append((next_x, next_y))

        # If the queue is empty and the goal was not found, return False
        return False

    def __str__(self):
        no_card = '   \n   \n   '
        board_map = self._board.get_map()
        board_str = ''

        for row in board_map:
            for i in range(3):
                for card in row:
                    if card is None:
                        board_str += no_card.split('\n')[i]
                    else:
                        # Check if the card is revealed and is a gold card
                        if card.is_revealed() and card.is_gold():
                            if i == 1:  # Modify the middle line to show 'G'
                                board_str += ' G '
                            else:
                                board_str += '   '  # Empty spaces for the top and bottom lines
                        else:
                            board_str += str(card).split('\n')[i]
                board_str += '\n'  # Move to the next line of the row

        return board_str


if __name__ == '__main__':
    board = GameBoard()
    print(board)
    print('-----------------')
    # create path card instances for a player
    path_card_cr = PathCard.cross_road()
    board.add_path_card(7, 10, path_card_cr)
    print(board)
    print('-----------------')
    board.remove_path_card(7, 10)
    print(board)
