from une_ai.models import Agent, GridMap
from card import Card, PathCard


class SaboteurPlayer(Agent):
    NUM_PLAYERS = 8
    MAP_LENGTH = 20
    MAP_WIDTH = 20
    ROLES = ('Gold-Digger', 'Saboteurs')
    ACTION_TYPES = ('play', 'map', 'dynamite', 'sabotage', 'mend', 'pass')
    GOAL_LOCATIONS = ((14, 8), (14, 10), (14, 12))

    def __init__(self, agent_name, agent_program):
        super().__init__(agent_name, agent_program)

    def add_all_sensors(self):
        self.add_sensor('game-board-sensor', GridMap(20, 20, None), validate_game_board)
        self.add_sensor('player-turn', 0, lambda v: isinstance(v, int) and 0 <= v < SaboteurPlayer.NUM_PLAYERS)
        self.add_sensor('player-hand', [], lambda v: validate_list(v, lambda c: isinstance(c, Card)))
        self.add_sensor('player-role', SaboteurPlayer.ROLES[0], lambda v: v in SaboteurPlayer.ROLES)
        self.add_sensor('sabotaged-players', [False] * SaboteurPlayer.NUM_PLAYERS,
                        lambda v: validate_list(v, lambda x: isinstance(x, bool)))

    def add_all_actuators(self):
        self.add_actuator('card-selected', 0, lambda v: isinstance(v, int) and 0 <= v and v <= len(self.read_sensor_value('player-hand')))
        self.add_actuator('play-type', 'play', lambda v: v in SaboteurPlayer.ACTION_TYPES)
        self.add_actuator('position', (0, 0), validate_position)
        self.add_actuator('card-turned', False, lambda v: isinstance(v, bool))
        self.add_actuator('player-select', 0, lambda v: isinstance(v, int) and 0 <= v and v < SaboteurPlayer.NUM_PLAYERS)
        self.add_actuator('tell-truth', False, lambda v: isinstance(v, bool))

    def add_all_actions(self):
        self._add_card_play_actions()
        self._add_sabotage_mend_actions()
        self._add_pass_actions()

    def _add_card_play_actions(self):
        for card_select in range(4):
            for i in range(self.MAP_LENGTH):
                for j in range(self.MAP_WIDTH):
                    for turn in [True, False]:
                        self.add_action(
                            f'play-{card_select}-{i}-{j}-{turn}',
                            lambda card_selected=card_select, x=i, y=j, flip=turn: {
                                'card-selected': card_selected,
                                'play-type': 'play',
                                'position': (x, y),
                                'card-turned': flip
                            })
                    self.add_action(
                        f'dynamite-{card_select}-{i}-{j}',
                        lambda card_selected=card_select, x=i, y=j: {
                            'card-selected': card_selected,
                            'play-type': 'dynamite',
                            'position': (x, y)
                        }
                    )
            for i, j in SaboteurPlayer.GOAL_LOCATIONS:
                for tell_truth in [True, False]:
                    self.add_action(
                        f'map-{card_select}-{i}-{j}-{tell_truth}',
                        lambda card_selected=card_select, x=i, y=j, _tell_truth=tell_truth: {
                            'card-selected': card_selected,
                            'play-type': 'map',
                            'position': (x, y),
                            'tell-truth': _tell_truth
                        })

    def _add_sabotage_mend_actions(self):
        for card_select in range(4):
            for player_index in range(SaboteurPlayer.NUM_PLAYERS):
                self.add_action(
                    f'sabotage-{card_select}-{player_index}',
                    lambda card_selected=card_select, player_id=player_index: {
                        'card-selected': card_selected,
                        'play-type': 'sabotage',
                        'player-select': player_id
                    })
                self.add_action(
                    f'mend-{card_select}-{player_index}',
                    lambda card_selected=card_select, player_id=player_index: {
                        'card-selected': card_selected,
                        'play-type': 'mend',
                        'player-select': player_id
                    })

    def _add_pass_actions(self):
        for card_select in range(4):
            self.add_action(
                f'pass-{card_select}',
                lambda card_selected=card_select: {
                    'card-selected': card_selected,
                    'play-type': 'pass',
                }
            )


def validate_game_board(board):
    if ((not isinstance(board, GridMap)) or (board.get_width() != SaboteurPlayer.MAP_WIDTH)
            or (board.get_height() != SaboteurPlayer.MAP_LENGTH)):
        return False

    for i in range(20):
        for j in range(20):
            item = board.get_item_value(i, j)
            if item != None and (not isinstance(item, PathCard)):
                return False

    return True


def validate_list(test, item_validator):
    return isinstance(test, list) and all(item_validator(item) for item in test)


def validate_position(position):
    return isinstance(position, tuple) and len(position) == 2 and all(isinstance(coord, int) for coord in position)


def validate_action(action_str):
    if not isinstance(action_str, str):
        return False
    action_type = action_str.split("-")[0]
    return action_type in SaboteurPlayer.ACTION_TYPES
