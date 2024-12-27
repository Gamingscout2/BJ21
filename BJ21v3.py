# A simple 1-2 Player Black Jack port in Python
# An improvement of my BJ21 in C
# Preston Parsons, 12/25/2024
# Subject to the license terms found at:
# https://sirobivan.org/pcl1-1.html
# Uses the user's OS Entropy Pool for shuffling
#
# The major improvements versus my earlier ports:
# - The game is no longer played with randomly generated numbers, instead
#    the deck of cards is fully simulated (all 52) as a list
# - RNG is handled primarily with os.urandom instead of standard RNG libs
# - Multi-player support added so 2 players can go head to head
# as of 3.0, two-player needs implemented
import os
import random

card_dict = {
    'Ace of Spades': 1, '2 of Spades': 2, '3 of Spades': 3, '4 of Spades': 4, '5 of Spades': 5, '6 of Spades': 6,
    '7 of Spades': 7, '8 of Spades': 8, '9 of Spades': 9, '10 of Spades': 10, 'Jack of Spades': 10,
    'Queen of Spades': 10, 'King of Spades': 10,
    'Ace of Diamonds': 1, '2 of Diamonds': 2, '3 of Diamonds': 3, '4 of Diamonds': 4, '5 of Diamonds': 5,
    '6 of Diamonds': 6, '7 of Diamonds': 7, '8 of Diamonds': 8, '9 of Diamonds': 9, '10 of Diamonds': 10,
    'Jack of Diamonds': 10, 'Queen of Diamonds': 10, 'King of Diamonds': 10,
    'Ace of Hearts': 1, '2 of Hearts': 2, '3 of Hearts': 3, '4 of Hearts': 4, '5 of Hearts': 5, '6 of Hearts': 6,
    '7 of Hearts': 7, '8 of Hearts': 8, '9 of Hearts': 9, '10 of Hearts': 10, 'Jack of Hearts': 10,
    'Queen of Hearts': 10, 'King of Hearts': 10,
    'Ace of Clubs': 1, '2 of Clubs': 2, '3 of Clubs': 3, '4 of Clubs': 4, '5 of Clubs': 5, '6 of Clubs': 6,
    '7 of Clubs': 7, '8 of Clubs': 8, '9 of Clubs': 9, '10 of Clubs': 10, 'Jack of Clubs': 10,
    'Queen of Clubs': 10, 'King of Clubs': 10
}

def GAME():
    print('Welcome to BJ21 v 3.0!')
    print('Developed by Preston Parsons')
    num_players = int(input('1 or 2 Players?: '))
    if num_players == 1:
        SINGLE_PLAYER()
    else:
        TWO_PLAYER()


def SINGLE_PLAYER():
    # Player take's their turn and then the
    # dealer's turn occurs, at which point
    # the game's winner is determined
    print('You versus the Dealer')
    deck = list(card_dict.keys())
    deck = SHUFFLE(deck)
    player_hand, dealer_hand = [], []

    # Deal initial hands
    for _ in range(2):
        player_hand.append(deck.pop(0))
        dealer_hand.append(deck.pop(0))

    print(f"Dealer shows: {dealer_hand[1]}")
    print(f"Your hand: {player_hand}")

    # Player's turn
    while HAND_VALUE(player_hand) < 21:
        action = input("Hit or Stay? (H/S): ").strip().lower()
        if action == 'h':
            player_hand.append(deck.pop(0))
            print(f"Your hand: {player_hand}")
        elif action == 's':
            break
        else:
            print("Invalid option.")

    player_total = HAND_VALUE(player_hand)
    if player_total > 21:
        print("Bust! Dealer wins.")
        return

    # Dealer's turn
    print(f"Dealer's hand: {dealer_hand}")
    while HAND_VALUE(dealer_hand) < 17:
        dealer_hand.append(deck.pop(0))
        print(f"Dealer hits: {dealer_hand}")
        print(f"Dealer's updated hand: {dealer_hand}")

    dealer_total = HAND_VALUE(dealer_hand)
    if dealer_total > 21:
        print("Dealer busts! You win.")
    else:
        determine_winner(player_total, dealer_total)


def TWO_PLAYER():
    print("Two-player mode is under development. Check back soon!")


def HAND_VALUE(hand: list):
    # returns the total value of cards in a given hand
    total = 0  # Hand total value
    ace_count = 0  # Number of aces in hand
    # Calculate the initial total and count Aces
    for card in hand:
        value = card_dict.get(card, 0)  # Default to 0 if card is not in dictionary
        if 'Ace' in card:
            ace_count += 1
        total += value
    # Adjust Aces: Switch their value to 11 if it doesn't cause the hand to exceed 21
    while ace_count > 0 and total + 10 <= 21:
        total += 10
        ace_count -= 1
    return total


def SHUFFLE(deck: list):
    # Basic shuffling algorithm
    # Using system entropy
    # alternate: int(time.time()**2) % 100
    # This is overly-complex but achieves a satisfactory
    # shuffled effect for a simple game
    if len(deck) <= 1:
        return deck
    subdeck1 = list([])
    subdeck2 = list([])
    for card in deck:
        seed = int.from_bytes(os.urandom(4), byteorder="big")
        if (seed % 2 == 0):
            subdeck1.append(card)
        else:
            subdeck2.append(card)
    # subdeck1 and subdeck2
    # splitting the 2 subdecks into 4 lists by alternating index
    # then concatonating together randomly and splitting again
    sd3, sd4 = split_alt(subdeck1)  # sd --> subdeck
    sd5, sd6 = split_alt(subdeck2)

    concatenated = rng_concat(sd3, sd4, sd5, sd6)

    final_sd1, final_sd2 = split_alt(concatenated)

    sr1 = rng_concat(final_sd1, final_sd2)  # --> sr1 = sub-result 1
    sr2, sr3 = split_3(sr1)
    result = rng_concat(sr2, sr3)

    return result


def split_3(deck: list):
    # splits a deck into 2 subdecks by groups of 3
    # by index
    subdeck1 = []
    subdeck2 = []
    # Iterate through the deck in sections of 3
    for i in range(0, len(deck), 3):
        group = deck[i:i + 3]  # Get the current group of 3 cards
        if (i // 3) % 2 == 0:  # Alternate between subdeck1 and subdeck2
            subdeck1.extend(group)
        else:
            subdeck2.extend(group)

    return subdeck1, subdeck2


def split_deck(deck):
    # splits a deck directly in half
    half = len(deck) // 2
    return deck[:half], deck[half:]


def rng_concat(*decks):
    # Randomly concatenates a variable number of decks
    deck_list = list(decks)
    random.shuffle(deck_list)  # Shuffle the order of decks
    result = []
    for deck in deck_list:
        result.extend(deck)  # Concatenate each deck in the new shuffled order
    return result


def split_alt(deck: list):
    # splits cards in a deck into 2 lists
    # seperated by alternating index
    subdeck1 = []
    subdeck2 = []
    # Enumerate through the deck to track the index
    for index, card in enumerate(deck):
        if index % 2 == 0:  # Even index
            subdeck1.append(card)
        else:  # Odd index
            subdeck2.append(card)
    return subdeck1, subdeck2


def determine_winner(player_total, dealer_total):
    # basic logic determines the winner
    print(f"Your total: {player_total}")
    print(f"Dealer total: {dealer_total}")
    if player_total > dealer_total:
        print("You win!")
    elif player_total < dealer_total:
        print("Dealer wins.")
    else:
        print("It's a tie!")
    play_again()

def play_again():
    option = input("Would you like to play again? Y/N: ")
    if option == 'Y' or option == 'y':
        GAME()
    elif option == 'N' or option == 'n':
        return 0;
GAME()
