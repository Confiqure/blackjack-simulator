# Blackjack Simulator

This repository contains a Python-based blackjack simulator that allows you to play a configurable game of blackjack. The game includes features like running count tracking, win likelihood calculation, and game result saving to a CSV file. The simulator can be configured using a configuration file.

## Features

- Simulate blackjack games with custom configurations
- Track running count to help with strategy
- Calculate win likelihood based on player's hand and deck state
- Configurable dealer behavior (e.g., hit on soft 17)
- Support for splitting hands, doubling down, and insurance
- Save game results to a CSV file for analysis

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Confiqure/blackjack-simulator.git
cd blackjack-simulator
```

### 2. Set up a virtual environment

It is recommended to use a virtual environment to manage dependencies. You can create and activate a virtual environment as follows:

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install dependencies

Once the virtual environment is activated, install the required dependencies:

```bash
pip install -r requirements.txt
```

### 4. Run the game

You can start the blackjack game by running the `main.py` script:

```bash
python main.py
```

## Configuration

The game can be configured using a configuration file (`config.json`). This file should include the following settings:

- `num_decks`: Number of decks to use in the game.
- `starting_amount`: The initial amount of money the player has.
- `reshuffle_threshold`: The number of cards remaining in the deck before a reshuffle occurs.
- `dealer_hits_on_soft_17`: Boolean value indicating whether the dealer should hit on a soft 17.
- `auto_print_hand_sum`: Automatically print the sum of the player's hand after each move.
- `insurance_allowed`: Whether insurance is allowed when the dealer shows an Ace.
- `show_hints`: Display hints and win likelihoods during the game.
- `show_running_count`: Display the running count for the deck during the game.

## Game Instructions

1. Run the game using `python main.py`.
2. Enter your bet when prompted.
3. Follow the instructions to hit, stand, double down, or split.
4. The game will track your hand, the dealer's hand, and the running count.
5. Game results will be saved in `game_results.csv`.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
