import random
from game_board import GOAL_LOCATIONS
from saboteur_environment import SaboteurEnvironment

def agent_program_pass(percepts, actuators):
    """
    This agent always passes its turn by discarding the first card.
    """
    return ['pass-0']

def agent_program_random(percepts, actuators):
    """
    This agent makes a random legal move based on its current percepts.
    If no legal moves are available, it will pass the turn.
    """
    legal_moves = SaboteurEnvironment.generate_legal_moves_from_percepts(percepts)
    if len(legal_moves) > 0:
        return [random.choice(legal_moves)]
    return agent_program_pass(percepts, actuators)


def agent_program_gold_digger(percepts, actuators):
    """
    Gold-Digger agent that focuses on revealing and reaching the gold card efficiently.
    """
    legal_moves = SaboteurEnvironment.generate_legal_moves_from_percepts(percepts)
    goal_locations = GOAL_LOCATIONS

    # Prioritize using "map" actions if close to a hidden goal card
    map_moves = [move for move in legal_moves if 'map' in move]
    if map_moves:
        return [random.choice(map_moves)]

    # Prioritize path moves toward the goal locations
    path_moves = [move for move in legal_moves if 'play' in move]
    best_move = None
    min_distance = float('inf')  # Initialize with a large value

    for move in path_moves:
        # Extract coordinates from the move
        move_parts = move.split('-')
        move_x, move_y = int(move_parts[2]), int(move_parts[3])

        # Calculate Manhattan distance to the closest goal location
        for goal_x, goal_y in goal_locations:
            distance = abs(goal_x - move_x) + abs(goal_y - move_y)
            if distance < min_distance:
                min_distance = distance
                best_move = move

    # Prioritize the best move (minimizing the distance to the closest goal)
    if best_move:
        return [best_move]

    # If no path moves toward the goal, play any valid path card
    if path_moves:
        return [random.choice(path_moves)]

    # If no valid moves, fall back to random or pass
    return agent_program_random(percepts, actuators)






def agent_program_saboteur(percepts, actuators):
    """
    This agent is designed for the 'Saboteur' role. Its goal is to disrupt the gold diggers by using sabotage and dynamite.
    The agent will prioritize sabotage and destruction over path creation.
    """
    legal_moves = SaboteurEnvironment.generate_legal_moves_from_percepts(percepts)

    # Prioritize sabotage moves
    sabotage_moves = [move for move in legal_moves if 'sabotage' in move]
    if len(sabotage_moves) > 0:
        return [random.choice(sabotage_moves)]

    # Prioritize dynamite moves to destroy useful paths for gold diggers
    dynamite_moves = [move for move in legal_moves if 'dynamite' in move]
    if len(dynamite_moves) > 0:
        return [random.choice(dynamite_moves)]

    # Play path cards to build unnecessary, complex paths to delay gold diggers
    path_moves = [move for move in legal_moves if 'play' in move]
    if len(path_moves) > 0:
        return [random.choice(path_moves)]

    # Use Map to gather information and mislead the gold diggers
    map_moves = [move for move in legal_moves if 'map' in move]
    if len(map_moves) > 0:
        return [random.choice(map_moves)]

    # If no valid move, fall back to random or pass
    return agent_program_random(percepts, actuators)
