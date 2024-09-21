class Card:
    pass

class ActionCard(Card):
    def __init__(self, action):
        assert action in ['map', 'sabotage', 'mend', 'dynamite'], "The parameter action must be either map, sabotage, mend or dynamite"
        self._action = action

    def get_action(self):
        return self._action

class InvalidTunnel(Exception):
    pass

class PathCard(Card):
    gold = False
    def __init__(self, tunnels, special_card=None):
        assert isinstance(tunnels, list), "The parameter tunnels must be a list of tuples"
        assert special_card in ['start', 'goal', 'gold', None], "The parameter special_card must be either None, start, goal or gold"

        for tunnel in tunnels:
            if not self._is_valid_tunnel(tunnel):
                raise InvalidTunnel(f"The tunnel '{tunnel}' is invalid for this card.")

        self._special_card = special_card
        self._revealed = True
        if special_card:
            cross_road = PathCard.cross_road()
            self._tunnels = cross_road.get_tunnels()
            if special_card in ['goal', 'gold']:
                self._revealed = False
        else:
            self._tunnels = tunnels

    @staticmethod
    def cross_road(special_card=None):
        return PathCard(
            [
                ('north', 'south'),
                ('north', 'east'),
                ('north', 'west'),
                ('south', 'east'),
                ('south', 'west'),
                ('east', 'west')
            ], special_card=special_card
        )

    def get_exits(self):
        exits = []
        for tunnel in self._tunnels:
            for exit in tunnel:
                if exit not in exits and exit is not None:
                    exits.append(exit)
        return exits

    @staticmethod
    def vertical_tunnel():
        return PathCard([('north', 'south')])

    @staticmethod
    def horizontal_tunnel():
        return PathCard([('east', 'west')])

    @staticmethod
    def vertical_junction():
        return PathCard([('north', 'south'), ('north', 'east'), ('south', 'east')])

    @staticmethod
    def horizontal_junction():
        return PathCard([('east', 'north'), ('west', 'north'), ('east', 'west')])

    @staticmethod
    def turn():
        return PathCard([('south', 'east')])

    @staticmethod
    def reversed_turn():
        return PathCard([('south', 'west')])

    @staticmethod
    def dead_end(directions):
        tunnels = [(direction, None) for direction in directions]
        return PathCard(tunnels)


    def _is_valid_tunnel(self, tunnel):
        if not isinstance(tunnel, tuple) or len(tunnel) != 2:
            return False
        for direction in tunnel:
            if direction not in ['north', 'east', 'south', 'west', None]:
                return False
        if tunnel[0] is None and tunnel[1] is None:
            return False
        if tunnel[0] == tunnel[1]:
            return False
        return True

    def is_special_card(self):
        return self._special_card is not None

    def is_gold(self):
        return self._special_card == 'gold'

    def reveal_card(self):
        self._revealed = True

    def is_revealed(self):
        """Returns whether the card has been revealed."""
        return self._revealed

    def turn_card(self):
        """Rotate the card's tunnels by 90 degrees."""
        tunnels = []
        opposite = {
            'north': 'east',
            'east': 'south',
            'south': 'west',
            'west': 'north',
        }

        for tunnel in self._tunnels:
            new_tunnel = (
                opposite[tunnel[0]] if tunnel[0] is not None else None,
                opposite[tunnel[1]] if tunnel[1] is not None else None
            )
            tunnels.append(new_tunnel)

        self._tunnels = tunnels
        return self

    def get_tunnels(self):
        return self._tunnels.copy()

    def __str__(self):
        card_rep = ['   ', ' . ', '   ']

        if self._revealed:
            for tunnel in self._tunnels:
                for direction in tunnel:
                    if direction == 'north':
                        card_rep[0] = ' ↑ '
                    elif direction == 'south':
                        card_rep[2] = ' ↓ '
                    elif direction == 'east':
                        card_rep[1] = card_rep[1][:2] + '→'
                    elif direction == 'west':
                        card_rep[1] = '←' + card_rep[1][1:]
        else:
            return '   \n ? \n   '

        return '\n'.join(card_rep)

