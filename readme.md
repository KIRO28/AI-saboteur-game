# Saboteur Game - AI Implementation

## Introduction
Welcome to the **Saboteur Game**! This game is an implementation of a social deduction game where players take on roles as either *Gold-Diggers* or *Saboteurs*. The goal of the Gold-Diggers is to reach the gold by constructing paths, while the Saboteurs secretly work to hinder this progress.

This project utilizes AI agents with different behaviors, all working towards their objectives within a grid-based game board.

## Setup Instructions

### Prerequisites
Before running the application, ensure you have the following installed on your machine:
- minimum version Python 3.12
- Libraries: `tkinter` for GUI, and any additional AI-related packages (e.g., `une_ai`).

To install dependencies, run:
```bash
pip install tkinter
```
## Main Files Required for this program
files in this project are:
- **`saboteur_app.py`**: Entry point for the game.
- **`saboteur_environment.py`**: Manages the game environment and game logic.
- **`saboteur_game.py`**: Contains the game loop and GUI setup.
- **`deck.py`**: Defines the deck of cards and shuffling mechanics.
- **`game_board.py`**: Manages the game board logic.
- **`agent_program.py`**: Defines the AI behaviors for both Gold-Diggers and Saboteurs.
- **`saboteur_player.py`**: Defines the player logic and actions.

## Running the Game
1. **Clone the repository** or download the source files to your local machine.
2. To clone this is the url ```https://github.com/KIRO28/AI-saboteur-game.git```
3**Navigate to the directory** containing the source files.
4. Open the file in visual studio or pycharm whichever ide is suitable
3. **Run the game** using the following command:
   ```bash
   python saboteur_app.py
   ```
   
## Game Execution
The game will initialize a graphical user interface (GUI) using `tkinter`. From here, you can observe the interaction of AI players as they attempt to either reach the gold or sabotage each other’s progress. And, it also depends upon the agent user which can be gold-diggers who tries to move towards the gold or Saboteurs who tries to block or destroy the path to gold.


### GUI Overview
- The left side of the GUI displays the **game board**, where path cards are placed.
- The right side shows the **status of players** and their current actions.

## Testing and Verification
To verify your setup:
1. Ensure the game initializes without errors.
2. Observe the players take turns according to their roles.
3. The game should declare a winner once a path is completed or if no legal moves remain.
4. When running you can view the terminal to see if the agent is doing what it supposed to do as, I used it to grasp the program flow and implement my logic.

## Game Mechanics
- **Gold-Diggers**: Aim to build a path from the start to the hidden gold.
- **Saboteurs**: Try to hinder the Gold-Diggers by using sabotage and dynamite cards.


