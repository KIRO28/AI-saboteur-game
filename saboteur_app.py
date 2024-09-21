from saboteur_environment import SaboteurEnvironment, NUM_PLAYERS
from saboteur_game import SaboteurGame, GameGUI
from saboteur_player import SaboteurPlayer
from agent_program import agent_program_random, agent_program_gold_digger, agent_program_saboteur

if __name__ == "__main__":
    # Create the Saboteur Environment
    env = SaboteurEnvironment()

    # Add players to the environment
    for i in range(NUM_PLAYERS):
        player_name = f"Player_{i}"
        env.add_player(SaboteurPlayer(player_name, agent_program_gold_digger))  # Using random agent as default for all players

    # Option to run the game without GUI (uncomment to use)
    # saboteur_game = SaboteurGame(env)
    # saboteur_game.main()

    # Run the game with GUI
    app = GameGUI(SaboteurGame(env))
