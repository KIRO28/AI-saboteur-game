from card import PathCard, ActionCard
import random


class Deck():
    """
    Deck class representing a collection of cards used in the game.
    Handles the initialization, shuffling, and drawing of cards.
    """

    def __init__(self):
        self._deck = []
        self._initialise_deck()
        self.shuffle()

    def _initialise_deck(self):
        """
        Initialize the deck with path and action cards.
        This includes different types of path cards (tunnels, junctions, crossroads, dead ends)
        and action cards (map, sabotage, mend, dynamite).
        """

        # Add path cards to the deck
        for i in range(4):
            self._deck.append(PathCard.vertical_tunnel())  # Vertical tunnel cards

        for i in range(5):
            self._deck.append(PathCard.vertical_junction())  # Vertical junction cards

        for i in range(5):
            self._deck.append(PathCard.cross_road())  # Crossroad cards

        for i in range(5):
            self._deck.append(PathCard.horizontal_junction())  # Horizontal junction cards

        for i in range(3):
            self._deck.append(PathCard.horizontal_tunnel())  # Horizontal tunnel cards

        for i in range(4):
            self._deck.append(PathCard.turn())  # Turn cards

        for i in range(5):
            self._deck.append(PathCard.reversed_turn())  # Reversed turn cards

        # Add dead-end cards to the deck
        self._deck.append(PathCard.dead_end(['south']))  # Dead-end facing south
        self._deck.append(PathCard.dead_end(['north', 'south']))  # Dead-end facing north and south
        self._deck.append(PathCard.dead_end(['north', 'east', 'south']))  # Dead-end with three exits
        self._deck.append(PathCard.dead_end(['north', 'east', 'south', 'west']))  # Complete dead-end (all sides)
        self._deck.append(PathCard.dead_end(['west', 'north', 'east']))  # Dead-end with three exits
        self._deck.append(PathCard.dead_end(['west', 'east']))  # Horizontal dead-end
        self._deck.append(PathCard.dead_end(['south', 'east']))  # Dead-end facing south and east
        self._deck.append(PathCard.dead_end(['south', 'west']))  # Dead-end facing south and west
        self._deck.append(PathCard.dead_end(['west']))  # Dead-end facing west

        # Add action cards to the deck
        for i in range(6):
            self._deck.append(ActionCard('map'))  # Map action cards

        for i in range(9):
            self._deck.append(ActionCard('sabotage'))  # Sabotage action cards

        for i in range(9):
            self._deck.append(ActionCard('mend'))  # Mend action cards

        for i in range(3):
            self._deck.append(ActionCard('dynamite'))  # Dynamite action cards

    def shuffle(self):
        """
        Shuffle the deck randomly.
        """
        random.shuffle(self._deck)

    def draw(self):
        """
        Draw a card from the deck. If the deck is empty, return None.
        """
        if len(self._deck) > 0:
            return self._deck.pop()  # Remove and return the top card
        else:
            return None  # Return None if the deck is empty
