import copy
import csv
import os
import random
from typing import List

from config import load_config


class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank

    def __repr__(self) -> str:
        return f"{self.rank} of {self.suit}"

    def value(self) -> int:
        if self.rank in ["J", "Q", "K"]:
            return 10
        elif self.rank == "A":
            return 11
        else:
            return int(self.rank)

    def count_value(self) -> int:
        """Returns the count value for the card for the running count."""
        if self.rank in ["2", "3", "4", "5", "6"]:
            return 1
        elif self.rank in ["10", "J", "Q", "K", "A"]:
            return -1
        else:
            return 0


class Deck:
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, num_decks: int = 1):
        self.num_decks = num_decks
        self.cards = self.build_deck()
        self.shuffle()
        self.running_count = 0

    def build_deck(self) -> List[Card]:
        return [
            Card(suit, rank) for suit in self.suits for rank in self.ranks
        ] * self.num_decks

    def shuffle(self) -> None:
        random.shuffle(self.cards)
        self.running_count = 0

    def deal_card(self) -> Card:
        card = self.cards.pop()
        self.update_running_count(card)
        return card

    def update_running_count(self, card: Card) -> None:
        self.running_count += card.count_value()


class Player:
    def __init__(self, name: str = "Player"):
        self.name = name
        self.hand: List[Card] = []

    def hit(self, card: Card) -> None:
        self.hand.append(card)

    def hand_value(self) -> int:
        value = sum(card.value() for card in self.hand)
        aces = sum(1 for card in self.hand if card.rank == "A")
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_bust(self) -> bool:
        return self.hand_value() > 21

    def is_blackjack(self) -> bool:
        return self.hand_value() == 21 and len(self.hand) == 2

    def can_split(self) -> bool:
        return len(self.hand) == 2 and self.hand[0].rank == self.hand[1].rank

    def split(self) -> List[List[Card]]:
        return [[self.hand.pop()], [self.hand.pop()]]

    def show_hand(self) -> str:
        return ", ".join(map(str, self.hand))


class Dealer(Player):
    def __init__(self, name: str = "Dealer"):
        super().__init__(name)

    def should_hit(self, dealer_hits_on_soft_17: bool) -> bool:
        value = self.hand_value()
        has_soft_17 = value == 17 and any(card.rank == "A" for card in self.hand)
        return value < 17 or (has_soft_17 and dealer_hits_on_soft_17)


def calculate_win_likelihood(player: Player, dealer: Dealer, deck: Deck) -> float:
    player_value = player.hand_value()
    if player_value > 21:
        return 0.0
    elif player_value == 21:
        return 1.0

    wins = 0
    simulations = 1_000

    for _ in range(simulations):
        simulated_deck = copy.copy(deck.cards)
        random.shuffle(simulated_deck)

        simulated_hand = [dealer.hand[0]]
        while sum(card.value() for card in simulated_hand) < 17:
            simulated_hand.append(simulated_deck.pop())

        dealer_value = sum(card.value() for card in simulated_hand)
        if dealer_value > 21 or player_value > dealer_value:
            wins += 1

    return wins / simulations


def recommend_best_move(win_likelihood: float) -> str:
    return "Stand" if win_likelihood >= 0.51 else "Hit"


def save_game_result(player_amount, bet, player_hand, dealer_hand) -> None:
    file_exists = os.path.isfile("game_results.csv")
    with open("game_results.csv", "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Player Amount", "Bet", "Player Hand", "Dealer Hand"])
        writer.writerow([player_amount, bet, player_hand, dealer_hand])


def play_blackjack(config_dict: dict) -> None:
    print("Loaded Configurations:")
    for key, value in config_dict.items():
        print(f"{key}: {value}")

    deck = Deck(num_decks=config_dict["num_decks"])
    player_amount = config_dict["starting_amount"]

    while player_amount > 0:
        if len(deck.cards) < config_dict["reshuffle_threshold"]:
            print("Reshuffling the deck...")
            deck = Deck(num_decks=config_dict["num_decks"])

        print(f"\nCurrent amount: ${player_amount}")
        while True:
            try:
                bet = int(input("Enter your bet: "))
                if bet > player_amount:
                    print(
                        "Bet exceeds your available amount. Please bet within your limit."
                    )
                elif bet <= 0:
                    print("Bet must be a positive number.")
                else:
                    break
            except ValueError:
                print("Invalid input. Please enter a number.")

        player = Player()
        dealer = Dealer()

        player.hit(deck.deal_card())
        player.hit(deck.deal_card())
        dealer.hit(deck.deal_card())
        dealer.hit(deck.deal_card())

        print(f"Dealer's hand: {dealer.hand[0]} and [Hidden]")
        print(f"Your hand: {player.show_hand()}")

        if config_dict["auto_print_hand_sum"]:
            print(
                f"Your hand value: {player.hand_value()} vs {dealer.hand[0].value()+10} (implied)"
            )

        if config_dict["insurance_allowed"] and dealer.hand[0].rank == "A":
            insurance_bet = input(
                "Dealer shows an Ace. Would you like to buy insurance? (y/n): "
            ).lower()
            if insurance_bet == "y":
                insurance_bet = min(bet / 2, player_amount)
                if dealer.is_blackjack():
                    print("Dealer has Blackjack! Insurance pays 2:1.")
                    player_amount += insurance_bet * 2
                else:
                    print("Dealer does not have Blackjack. You lose the insurance bet.")
                    player_amount = max(0, player_amount - insurance_bet)

        while True:
            if player.is_blackjack():
                print("Blackjack! You win!")
                player_amount += bet * 1.5
                break

            if config_dict["show_hints"]:
                win_likelihood = calculate_win_likelihood(player, dealer, deck)
                print(f"Your current win likelihood: {win_likelihood * 100:.2f}%")
                print(f"Hint: {recommend_best_move(win_likelihood)}")

            if config_dict["show_running_count"]:
                print(f"Running count: {deck.running_count}")

            if player.can_split():
                move = input(
                    "Would you like to (h)it, (s)tand, (d)ouble down, or s(p)lit? "
                ).lower()
            elif len(player.hand) == 2:
                move = input(
                    "Would you like to (h)it, (s)tand, or (d)ouble down? "
                ).lower()
            else:
                move = input("Would you like to (h)it or (s)tand? ").lower()

            if move == "h":
                player.hit(deck.deal_card())
                print(f"Your hand: {player.show_hand()}")
                if config_dict["auto_print_hand_sum"]:
                    print(
                        f"Your hand value: {player.hand_value()} vs {dealer.hand[0].value()+10} (implied)"
                    )
                if player.is_bust():
                    print("You busted! Dealer wins.")
                    player_amount -= bet
                    break
            elif move == "s":
                break
            elif move == "d" and len(player.hand) == 2:
                player_amount -= bet
                bet *= 2
                player.hit(deck.deal_card())
                print(f"Your hand: {player.show_hand()}")
                if config_dict["auto_print_hand_sum"]:
                    print(
                        f"Your hand value: {player.hand_value()} vs {dealer.hand[0].value()+10} (implied)"
                    )
                if player.is_bust():
                    print("You busted! Dealer wins.")
                    break
                break
            elif move == "p" and player.can_split():
                split_hands = player.split()
                split_bets = [bet] * 2
                for i, split_hand in enumerate(split_hands):
                    print(f"Playing hand {i + 1}: {player.show_hand()}")
                    while True:
                        if player.is_blackjack():
                            print("Blackjack! You win!")
                            player_amount += split_bets[i] * 1.5
                            break

                        if config_dict["show_hints"]:
                            win_likelihood = calculate_win_likelihood(
                                player, dealer, deck
                            )
                            print(
                                f"Your current win likelihood: {win_likelihood * 100:.2f}%"
                            )
                            print(f"Hint: {recommend_best_move(win_likelihood)}")

                        if config_dict["show_running_count"]:
                            print(f"Running count: {deck.running_count}")

                        if player.is_bust():
                            print("You busted! Dealer wins.")
                            player_amount -= split_bets[i]
                            break
                        break

        if not player.is_bust():
            print(f"Dealer's hand: {dealer.show_hand()}")
            while dealer.should_hit(config_dict["dealer_hits_on_soft_17"]):
                dealer.hit(deck.deal_card())
                print(f"Dealer hits: {dealer.show_hand()}")
                if dealer.is_bust():
                    print("Dealer busted! You win.")
                    player_amount += bet
                    break

        if not player.is_bust() and not dealer.is_bust():
            player_value = player.hand_value()
            dealer_value = dealer.hand_value()

            print(f"Your hand value: {player_value}")
            print(f"Dealer's hand value: {dealer_value}")

            if dealer_value > player_value:
                print("Dealer wins.")
                player_amount -= bet
            elif dealer_value < player_value:
                print("You win!")
                player_amount += bet
            else:
                print("It's a tie!")

        save_game_result(player_amount, bet, player.show_hand(), dealer.show_hand())

    print("Game over! You've run out of money.")


config = load_config()
play_blackjack(config)
