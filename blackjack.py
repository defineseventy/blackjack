'''
Creating a simple Blackjack or 21 program.
Blackjack, also known as 21, is a card game where players 
try to get as close to 21 points as possible without going over. 
This program uses images drawn with text characters, called ASCII art. 
American Standard Code for Information Interchange (ASCII) is a 
mapping of text characters to numeric codes that computers used before 
Unicode replaced it. 
The playing cards in this program are an example of ASCII art
'''

import random
import json
import os
import sys

# Suits
HEARTS = '♥'
DIAMONDS = '♦'
SPADES = '♠'
CLUBS = '♣'
BACKSIDE = 'BACKSIDE'
SAVE_FILE = "blackjack_save.json"

# -------- Save & Load --------
def save_game(money, stats):
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "money": money,
            "wins": stats["wins"],
            "losses": stats["losses"],
            "pushes": stats["pushes"]
        }, f)

def load_game():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            return data.get("money", 5000), {
                "wins": data.get("wins", 0),
                "losses": data.get("losses", 0),
                "pushes": data.get("pushes", 0)
            }
    return 5000, {"wins": 0, "losses": 0, "pushes": 0}

# -------- Game Entry Point --------
def game():
    print("Welcome to ASCII Blackjack!")
    money, stats = load_game()

    while True:
        if money <= 0:
            print("You're out of money! Game over.")
            save_game(money, stats)
            sys.exit()

        print(f"\nYou have ${money}")
        print(f"Wins: {stats['wins']} | Losses: {stats['losses']} | Pushes: {stats['pushes']}")
        bet = get_bet(money)

        deck = get_deck()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        final_bet, surrendered = player_turn(player_hand, dealer_hand, deck, bet, money)

        if surrendered:
            print("You surrendered. You lose half your bet.")
            money -= final_bet // 2
            stats["losses"] += 1
        else:
            dealer_turn(player_hand, dealer_hand, deck)
            money = resolve_game(player_hand, dealer_hand, final_bet, money, stats)

        save_game(money, stats)
        input("\nPress Enter to continue...\n")

# -------- Game Functions --------
def get_bet(max_bet):
    while True:
        print(f"Enter your bet (1 - {max_bet}, or QUIT):")
        choice = input("> ").strip().upper()
        if choice == "QUIT":
            print("Thanks for playing!")
            sys.exit()
        if not choice.isdigit():
            continue
        bet = int(choice)
        if 1 <= bet <= max_bet:
            return bet

def get_deck():
    deck = []
    for suit in (HEARTS, DIAMONDS, SPADES, CLUBS):
        for rank in range(2, 11):
            deck.append((str(rank), suit))
        for rank in ('J', 'Q', 'K', 'A'):
            deck.append((rank, suit))
    random.shuffle(deck)
    return deck

def get_hand_value(hand):
    value = 0
    aces = 0
    for card in hand:
        rank = card[0]
        if rank == 'A':
            aces += 1
        elif rank in ('J', 'Q', 'K'):
            value += 10
        else:
            value += int(rank)
    value += aces
    for _ in range(aces):
        if value + 10 <= 21:
            value += 10
    return value

def display_hands(player, dealer, show_dealer=False):
    print()
    if show_dealer:
        print(f"DEALER ({get_hand_value(dealer)}):")
        print(display_ascii_cards(dealer))
    else:
        print("DEALER:")
        print(display_ascii_cards([BACKSIDE] + dealer[1:]))

    print(f"\nPLAYER ({get_hand_value(player)}):")
    print(display_ascii_cards(player))

def player_turn(player, dealer, deck, bet, money):
    can_double = len(player) == 2 and money >= 2 * bet
    display_hands(player, dealer, show_dealer=False)

    while True:
        print("\nChoose: (H)it, (S)tand, (D)ouble down, (Su)rrender")
        move = input("> ").strip().upper()
        if move == 'H':
            player.append(deck.pop())
            display_hands(player, dealer, show_dealer=False)
            if get_hand_value(player) > 21:
                break
        elif move == 'S':
            break
        elif move == 'D' and can_double:
            bet *= 2
            player.append(deck.pop())
            print("You doubled down!")
            display_hands(player, dealer, show_dealer=False)
            break
        elif move == 'SU':
            return bet, True
    return bet, False

def dealer_turn(player, dealer, deck):
    if get_hand_value(player) > 21:
        return
    while get_hand_value(dealer) < 17:
        dealer.append(deck.pop())

def resolve_game(player, dealer, bet, money, stats):
    display_hands(player, dealer, show_dealer=True)
    player_val = get_hand_value(player)
    dealer_val = get_hand_value(dealer)

    if player_val > 21:
        print("You busted!")
        stats["losses"] += 1
        return money - bet
    elif dealer_val > 21:
        print(f"Dealer busted. You win ${bet}!")
        stats["wins"] += 1
        return money + bet
    elif player_val > dealer_val:
        print(f"You win ${bet}!")
        stats["wins"] += 1
        return money + bet
    elif player_val < dealer_val:
        print("Dealer wins.")
        stats["losses"] += 1
        return money - bet
    else:
        print("Push. Bet returned.")
        stats["pushes"] += 1
        return money

# -------- ASCII Card Display --------
def ascii_card(rank, suit):
    rank_str = str(rank).ljust(2)
    return [
        "┌─────────┐",
        f"│{rank_str}       │",
        "│         │",
        f"│    {suit}    │",
        "│         │",
        f"│       {rank_str}│",
        "└─────────┘"
    ]

def display_ascii_cards(cards):
    rows = [''] * 7
    for card in cards:
        if card == BACKSIDE:
            art = [
                "┌─────────┐",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "│░░░░░░░░░│",
                "└─────────┘"
            ]
        else:
            rank, suit = card
            art = ascii_card(rank, suit)
        for i in range(7):
            rows[i] += art[i] + '  '
    return '\n'.join(rows)

# -------- Start Game --------
if __name__ == "__main__":
    game()