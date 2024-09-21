import time
from saboteur_environment import SaboteurEnvironment
import tkinter as tk
from tkinter import font
import sys

num_players = 8


class SaboteurGame:
    def __init__(self, environment: SaboteurEnvironment) -> None:
        # Check if the environment is an instance of the SaboteurEnvironment class
        assert type(environment).__name__ == 'SaboteurEnvironment', ("environment must be an instance of a subclass of "
                                                                     "the class SaboteurEnvironment")
        self._agents = [environment.get_player(i)[0] for i in range(num_players)]
        self._environment = environment

    def _play_step(self, num_steps=1, log=True):
        for _ in range(num_steps):
            if self._environment.is_terminal():
                break
            cur_player = self._environment.turn()
            # SENSE: update sensors by function get_percepts
            self._agents[cur_player].sense(self._environment)
            # THINK: use agent_program to think
            actions = self._agents[cur_player].think()
            if log: print(f"{cur_player} is playing action: {actions[-1]}")
            # ACT: update the environment by actions (action affect actuators and actuators affect environment)
            self._agents[cur_player].act(actions, self._environment)

    def main(self):
        while not self._environment.is_terminal():
            self._play_step()
            print(self._environment.get_game_board())


class GameGUI:
    def __init__(self, saboteur_game: SaboteurGame):
        self.root = tk.Tk()
        self.root.title("Saboteur Game Status")

        # Saboteur game instance
        self.saboteur_game = saboteur_game

        # Set up the font for better readability
        self.custom_font = font.Font(family="Courier", size=14)  # Use fixed-width font for alignment

        # Create a frame to hold the canvas and scrollbar
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Configure a 2-column layout: game board (left) and agents (right)
        self.main_frame.columnconfigure(0, weight=4)  # More space for the game board
        self.main_frame.columnconfigure(1, weight=1)  # Less space for agents

        # Create a canvas for the game board
        self.canvas = tk.Canvas(self.main_frame, width=600, height=600)  # Increased size for the game board
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.grid(row=0, column=0, sticky="nse")

        # Configure the canvas to work with the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the content
        self.board_frame = tk.Frame(self.canvas)

        # Place the board_frame on the canvas
        self.canvas.create_window((0, 0), window=self.board_frame, anchor="nw")

        # Ensure that the board_frame size is dynamically adjusted
        self.board_frame.bind("<Configure>", self.on_frame_configure)

        # Game board display label (inside the frame)
        self.board_label = tk.Label(self.board_frame, text="", font=self.custom_font, justify=tk.LEFT, anchor="nw")
        self.board_label.pack(pady=10, padx=10, fill="both", expand=True)

        # Agents display label (right side)
        self.agents_label = tk.Label(self.main_frame, text="", font=self.custom_font, justify=tk.LEFT, anchor="nw")
        self.agents_label.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Start the game loop
        self.update_game_status()

        # Start the Tkinter main loop
        self.root.mainloop()

    def on_frame_configure(self, event):
        """Adjust the canvas scroll region when the frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def update_game_status(self):
        """Updates the game status in the GUI."""

        # Update the game by one step
        self.saboteur_game._play_step(num_steps=2, log=False)

        # Get the game board and player actions from SaboteurGame
        game_board = self.saboteur_game._environment.get_game_board()
        players_status = "\n".join(str(player) for player in self.saboteur_game._agents)

        # Update the GUI labels to show the current state of the game board
        self.board_label.config(text=f"Game Board:\n{game_board}")

        # Get player's actuator values and update the agent's status in the GUI
        agents_string = ""
        for id, player in enumerate(self.saboteur_game._agents):
            card_selected = player.read_actuator_value('card-selected')
            play_type = player.read_actuator_value('play-type')
            position = player.read_actuator_value('position')
            agents_string += f"Player {id}: card={card_selected}, action={play_type}, pos={position}\n"

        self.agents_label.config(text=agents_string)

        # update the display
        self.root.update()
        time.sleep(0.80)

        # Check if the game has reached a terminal state
        if self.saboteur_game._environment.is_terminal():
            # Display the winner immediately
            if self.saboteur_game._environment.get_winner() == 'Gold-Digger':
                self.board_label.config(text="Gold-Digger wins! The gold has been found!")
            else:
                self.board_label.config(text="Saboteurs win! The gold-diggers couldn't find the gold.")

            # Final update to show the winner
            self.root.update()
            return  # Stop further updates

        # Schedule the next update
        self.root.after(200, self.update_game_status)

