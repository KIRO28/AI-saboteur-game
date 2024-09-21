import time

from game_board import GameBoard, GOAL_LOCATIONS
from une_ai.models import GameEnvironment, Agent
from deck import Deck
from card import Card, PathCard, ActionCard
import random
import copy

# Players and their roles
PLAYER_ROLES = ('Gold-Digger', 'Saboteurs')
NUM_PLAYERS = 8
_roles = random.sample(PLAYER_ROLES, counts=[6, 3], k=NUM_PLAYERS)

# Game constants
BOARD_SIZE = 20
HAND_SIZE = 4
ACTION_TYPES = ('play', 'map', 'sabotage', 'mend', 'dynamite', 'pass')
CARD_ACTIONS = ('map', 'sabotage', 'mend', 'dynamite')
DIRECTIONS = ('north', 'east', 'south', 'west')
DIRECTION_OFFSET: dict[str, tuple[int, int]] = {
    'north': (0, -1),
    'south': (0, 1),
    'west': (-1, 0),
    'east': (1, 0)
}

START_POS = (6, 10)
GOAL_CARDS = GOAL_LOCATIONS


class SaboteurEnvironment(GameEnvironment):
    def __init__(self):
        super().__init__("Saboteur Environment")
        # Initialize the game environment
        self._players: dict[int, tuple[Agent, str]] = {}  # {player_id: (agent, role)}
        self._players_hands: dict[int, list[Card]] = {}
        self._sabotaged_players: list[bool] = [False for _ in range(NUM_PLAYERS)]
        self._game_board = GameBoard()
        self._deck = Deck()
        self._deck.shuffle()
        self._player_turn = random.randint(0, NUM_PLAYERS - 1)
        self._move_list: list[str] = []
        self._game_over = False

    def get_game_board(self):
        return self._game_board

    def get_game_board_gridmap(self):
        return self._game_board.get_board()

    def set_environment(self, game_state: dict):
        self._deck = game_state['game-deck']
        self._game_board = game_state['game-board']
        self._player_turn = game_state['player-turn']
        self._players_hands = game_state['player-hands']
        self._sabotaged_players = game_state['sabotaged-players']

    def add_player(self, player: Agent):
        """Adds a player to the game, assigns them a role and gives them cards."""
        assert len(self._players) < NUM_PLAYERS, "Cannot add more than 8 players."
        player_id = len(self._players)
        role = _roles[player_id]
        self._players[player_id] = (player, role)
        self._players_hands[player_id] = [self._deck.draw() for _ in range(HAND_SIZE)]
        return player_id

    def get_game_state(self):
        """Returns the current game state."""
        return {
            'game-board': self._game_board.get_board(),
            'game-deck': self._deck,
            'sabotaged-players': self._sabotaged_players,
            'player-turn': self._player_turn,
            'player-hands': self._players_hands,
        }

    def turn(self, game_state=None):
        """Returns the current player turn."""
        if game_state is None:
            return self._player_turn
        else:
            return game_state['player-turn']

    def get_percepts(self):
        """Returns the percepts of the current player."""
        cur_player = self.turn()
        return {
            'game-board-sensor': self._game_board.get_board(),
            'player-turn': cur_player,
            'player-hand': self._players_hands[cur_player].copy(),
            'player-role': self._players[cur_player][1],
            'sabotaged-players': self._sabotaged_players.copy()
        }

    def state_transition(self, agent_actuators):
        """
        Processes the state transition based on the action derived from agent actuators.
        """
        card_selected = agent_actuators['card-selected']
        action_type = agent_actuators['play-type']
        player_id = self._player_turn

        # Handle the player's selected action
        if action_type == 'play':
            params = [card_selected, agent_actuators['position'][0], agent_actuators['position'][1],
                      agent_actuators['card-turned']]
            self._handle_play_action(params, self._players_hands[player_id][card_selected])
        elif action_type == 'map':
            params = [card_selected, agent_actuators['position'][0], agent_actuators['position'][1],
                      agent_actuators['tell-truth']]
            self._handle_map_action(params, self._players_hands[player_id][card_selected])
        elif action_type == 'dynamite':
            params = [card_selected, agent_actuators['position'][0], agent_actuators['position'][1]]
            self._handle_dynamite_action(params, self._players_hands[player_id][card_selected])
        elif action_type in ['sabotage', 'mend']:
            params = [card_selected, agent_actuators['player-select']]
            self._handle_sabotage_mend_action(action_type, params, self._players_hands[player_id][card_selected])
        elif action_type == 'pass':
            print(f"Player {player_id} passes the turn.")

        # Remove the played card and draw a new one if available
        if action_type != 'pass':
            try:
                played_card = self._players_hands[player_id][card_selected]
                print(f"Played card: {played_card}")
                self._players_hands[player_id].remove(played_card)

                if self._deck:
                    drew_card = self._deck.draw()
                    if drew_card is not None:
                        self._players_hands[player_id].append(drew_card)

                print(f"Card successfully removed. Player's hand after removal: {self._players_hands[player_id]}")
            except ValueError:
                print("Warning: Played card not found in player's hand. Skipping removal.")

        # Move to the next player and check for the terminal state
        self._player_turn = (player_id + 1) % NUM_PLAYERS

        if self.is_terminal():
            print(f"Game Over! Winner: {self.get_winner()}")
            return
        return

    def is_winning(self):
        """Checks if the Gold-Diggers have won by reaching the gold."""
        for goal_location in GOAL_CARDS:
            goal_card = self._game_board.get_board().get_item_value(*goal_location)
            if goal_card and goal_card.is_gold() and self._game_board.is_connected(goal_location):
                goal_card.reveal_card()
                return True
        return False

    def no_legal_moves_remaining(self):
        """Checks if no legal moves are available."""
        # To check if the deck is empty and all players have no cards
        if all(len(hand) == 0 for hand in self._players_hands.values()) and not self._deck:
            return True

        # To check if no player has any valid moves left
        for player_id in range(NUM_PLAYERS):
            legal_actions = self.get_legal_actions_for_player(player_id)
            if legal_actions:
                return False  # At least one valid move remains

        return True  # No legal moves left

    def get_legal_actions_for_player(self, player_id):
        """Returns all legal actions for a specific player."""
        actions = []
        players_hand = self._players_hands[player_id]

        if not self._sabotaged_players[player_id]:
            actions += self.generate_playable_pathcards(players_hand, self._game_board)
        actions += self.generate_playable_actions(player_id, players_hand, self._sabotaged_players, self._game_board)

        for i in range(len(players_hand)):
            actions.append(f"pass-{i}")

        return actions

    def get_winner(self):
        """Determines the winner based on the game state."""
        if self.is_winning():
            return 'Gold-Digger'
        else:
            return 'Saboteurs'

    def _handle_play_action(self, params, played_card):
        """
        Handles the 'play' action by placing a path card on the board.
        """
        assert isinstance(played_card, PathCard)
        x, y, turned = int(params[1]), int(params[2]), params[3] == "True"

        if turned:
            played_card.turn_card()

        # Attempt to place the path card on the board at the specified position
        success = self._game_board.try_place_with_rotation(x, y, played_card)
        if not success:
            print(f"Card placement failed at ({x}, {y}). Passing the turn.")
            self.state_transition({'play-type': 'pass', 'card-selected': 0})
        else:
            pass

    def _handle_map_action(self, params, played_card: ActionCard):
        """
        Handles the 'map' action by revealing or falsifying goal information.
        """
        x, y = int(params[1]), int(params[2])
        tell_truth = params[3] == "True"
        goal_card: PathCard = self._game_board.get_board().get_item_value(x, y)
        real_answer = "gold" if goal_card.is_gold() else None
        revealed_info = real_answer if tell_truth else ("gold" if real_answer is None else None)

        # implemented just to display the revealed information
        print(f"Player {self._player_turn} reveals: {revealed_info}")

    def _handle_dynamite_action(self, params, played_card: ActionCard):
        """
        Handles the 'dynamite' action by removing a path card from the board.
        """
        x, y = int(params[1]), int(params[2])
        self._game_board.remove_path_card(x, y)
        print(f"Dynamite used at ({x}, {y}). Card removed.")

    def _handle_sabotage_mend_action(self, action_type, params, played_card: ActionCard):
        """
        Handles the 'sabotage' or 'mend' actions by updating player states.
        """
        player_index = int(params[1])
        is_sabotage = action_type == 'sabotage'
        self._sabotaged_players[player_index] = is_sabotage
        action_str = "sabotaged" if is_sabotage else "mended"
        print(f"Player {player_index} has been {action_str}.")

    def is_terminal(self):
        """Checks if the game has reached a terminal state."""
        if self.is_winning():
            return True

        if self.no_legal_moves_remaining():
            print("No legal moves remaining. Saboteurs win!")
            return True

        return False

    def get_winner(self):
        """Determines the winner based on the game state."""
        if self.is_winning():
            return 'Gold-Digger'
        return 'Saboteurs'

    @staticmethod
    def generate_playable_pathcards(players_hand, game_board):
        """Generates all playable path cards based on the current game state."""
        actions = []
        path_cards = [(players_hand[index], index, False) for index in range(len(players_hand)) if isinstance(players_hand[index], PathCard)]
        turned_path_cards = [(copy.deepcopy(card).turn_card(), index, True) for card, index, _ in path_cards]
        all_path_cards = path_cards + turned_path_cards

        seen = []
        queue = [START_POS]

        while queue:
            cur_pos = queue.pop(0)
            if cur_pos in seen:
                continue
            seen.append(cur_pos)

            cur_card = game_board.get_board().get_item_value(*cur_pos)
            if cur_card is None:
                continue

            exits = cur_card.get_exits()
            for dir in exits:
                next_pos = game_board.future_state(cur_pos, dir)[1]
                if next_pos is None:
                    continue
                if game_board.get_board().get_item_value(*next_pos) is None:
                    for card, index, turned in all_path_cards:
                        actions.append(f"play-{index}-{next_pos[0]}-{next_pos[1]}-{turned}")
                else:
                    queue.append(next_pos)

        return actions

    @staticmethod
    def generate_playable_actions(current_player, players_hand, sabotaged_players, game_board):
        """Generates all playable action cards based on the current game state."""
        actions = []
        action_cards = [(players_hand[index], index) for index in range(len(players_hand)) if isinstance(players_hand[index], ActionCard)]

        for card, index in action_cards:
            card_action = card.get_action()

            if card_action == 'map':
                for goal_pos in GOAL_CARDS:
                    for tell_truth in [True, False]:
                        actions.append(f"map-{index}-{goal_pos[0]}-{goal_pos[1]}-{tell_truth}")

            elif card_action == 'dynamite':
                for x in range(BOARD_SIZE):
                    for y in range(BOARD_SIZE):
                        item = game_board.get_board().get_item_value(x, y)
                        if item is not None and not item.is_special_card():
                            actions.append(f"dynamite-{index}-{x}-{y}")

            elif card_action == 'sabotage':
                for i in range(NUM_PLAYERS):
                    if not sabotaged_players[i] and i != current_player:
                        actions.append(f"sabotage-{index}-{i}")

            elif card_action == 'mend':
                for i in range(NUM_PLAYERS):
                    if sabotaged_players[i]:
                        actions.append(f"mend-{index}-{i}")

        return actions

    def get_legal_actions(self):
        """Returns all legal actions for the current player."""
        current_player = self._player_turn
        players_hand = self._players_hands[current_player]

        actions = []
        if not self._sabotaged_players[current_player]:
            actions += SaboteurEnvironment.generate_playable_pathcards(players_hand, self._game_board)
        actions += SaboteurEnvironment.generate_playable_actions(current_player, players_hand, self._sabotaged_players, self._game_board)

        for i in range(len(players_hand)):
            actions.append(f"pass-{i}")

        return actions

    @staticmethod
    def generate_legal_moves_from_percepts(percepts):
        """Generates legal moves based on percepts."""
        actions = []
        current_player = percepts['player-turn']
        game_board = GameBoard(percepts['game-board-sensor'])
        players_hand = percepts['player-hand']
        sabotaged_players = percepts['sabotaged-players']

        if not sabotaged_players[current_player]:
            actions += SaboteurEnvironment.generate_playable_pathcards(players_hand, game_board)
        actions += SaboteurEnvironment.generate_playable_actions(current_player, players_hand, sabotaged_players, game_board)

        for i in range(len(players_hand)):
            actions.append(f"pass-{i}")

        return actions

    @staticmethod
    def transition_result(game_state: dict, action: str):
        """
        Simulates a state transition based on an action and returns the new game state.
        This is used to check what the game state will look like after applying an action.
        """
        new_env = SaboteurEnvironment()  # Create a new instance of the environment
        new_env.set_environment(game_state)  # Set the environment with the current game state
        # Split the action string to understand the type and parameters
        action_parts = action.split('-')
        action_type = action_parts[0]

        # Construct actuators (simulate the agent's action)
        actuators = {
            'card-selected': int(action_parts[1]),  # card selected
            'play-type': action_type
        }

        if action_type == 'play':
            actuators['position'] = (int(action_parts[2]), int(action_parts[3]))  # x, y coordinates
            actuators['card-turned'] = action_parts[4] == 'True'
        elif action_type in ['map', 'dynamite']:
            actuators['position'] = (int(action_parts[2]), int(action_parts[3]))
        elif action_type in ['sabotage', 'mend']:
            actuators['player-select'] = int(action_parts[2])
        elif action_type == 'pass':
            pass  # No additional parameters

        # Perform the state transition
        new_env.state_transition(actuators)
        return new_env.get_game_state()  # Return the new game state

    def payoff_self(self, player_name):
        """
        Computes the payoff (reward) for the current player based on whether the game has ended and who won.
        If the game is not over, the payoff is 0. If the player’s team won, the payoff is 1; otherwise, it’s -1.
        """
        if not self.is_terminal():
            return 0  # Game is not over, no payoff
        winner = self.get_winner()
        # Check if the player's team is the winner
        if self._players[player_name][1] == winner:
            return 1  # Player's team won
        else:
            return -1  # Player's team lost

    @staticmethod
    def payoff(game_state, player_name):
        """
        Simulates the payoff for a player in a specific game state.
        It sets the game state in a new environment instance and calculates the payoff for the player.
        """
        new_env = SaboteurEnvironment()  # Create a new environment instance
        new_env.set_environment(game_state)  # Set the current game state
        return new_env.payoff_self(player_name)  # Compute the payoff for the given player