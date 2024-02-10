# -*- coding: utf-8 -*-
""" Utils module provides useful helper dicts and custom exceptions for PokerNowLogConverter"""
from copy import deepcopy
from enum import IntEnum
from itertools import combinations
from typing import List, Tuple, Dict, Optional

from card import Card

currencyCCToSymbol = dict(USD='$', CAD='$', GBP='£', EUR='€', SEK='kr', PLY='P')

hand_rank_counter: Dict[str, int] = {"A": 0, "K": 0, "Q": 0, "J": 0, "T": 0, "9": 0, "8": 0, "7": 0, "6": 0, "5": 0,
                                     "4": 0, "3": 0, "2": 0}
hand_suit_counter: Dict[str, int] = {"c": 0, "d": 0, "h": 0, "s": 0}

hand_rank_names_singular: Dict[str, str] = {"A": "Ace", "K": "King", "Q": "Queen", "J": "Jack", "T": "Ten", "9": "Nine",
                                            "8": "Eight", "7": "Seven", "6": "Six", "5": "Five", "4": "Four",
                                            "3": "Three", "2": "Deuce"}

hand_rank_names_plural: Dict[str, str] = {"A": "Aces", "K": "Kings", "Q": "Queens", "J": "Jacks", "T": "Tens",
                                          "9": "Nines", "8": "Eights", "7": "Sevens", "6": "Sixes", "5": "Fives",
                                          "4": "Fours", "3": "Threes", "2": "Deuces"}

hand_rank_values: Dict[str, int] = {"A": 13, "K": 12, "Q": 11, "J": 10, "T": 9, "9": 8, "8": 7, "7": 6, "6": 5, "5": 4,
                                    "4": 3, "3": 2, "2": 1}


# Enum class for poker hands
class PokerHand(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


# Used in hash functions
BASE_K: int = 31


def open_text_file(path: str):
    with open(path, encoding="utf-8") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
    return lines


def hash_cards(cards: List[Card]) -> int:
    """ Creates a hash value for a set of cards. Should be ordered from highest to lowest rank in parameter."""
    cards = list(cards)  # Copy list
    cards.reverse()  # Sort High to low (default is low to high)

    hash_value = 0
    for i, c in enumerate(cards):
        hash_value += (hand_rank_values[c.rank] * pow(BASE_K, i))

    return hash_value


def eval_final_hand(cards: List[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ Turns a list of 7 cards into a string representation of the best hand possible with those 7 """
    cards.sort(reverse=True)

    # Get valid five card combinations
    five_card_hands = list(combinations(cards, r=5))

    # For each combination, get its best value result
    hands_with_value = []
    for hand in five_card_hands:
        if rf := is_royal_flush(hand):
            hands_with_value.append(rf)
            continue
        if sf := is_straight_flush(hand):
            hands_with_value.append(sf)
            continue
        if fk := is_four_of_a_kind(hand):
            hands_with_value.append(fk)
            continue
        if fh := is_full_house(hand):
            hands_with_value.append(fh)
            continue
        if f := is_flush(hand):
            hands_with_value.append(f)
            continue
        if s := is_straight(hand):
            hands_with_value.append(s)
            continue
        if tk := is_three_of_a_kind(hand):
            hands_with_value.append(tk)
            continue
        if tp := is_two_pair(hand):
            hands_with_value.append(tp)
            continue
        if p := is_pair(hand):
            hands_with_value.append(p)
            continue

        hc = high_card(hand)
        hands_with_value.append(hc)

    # Sort first by Hand rank descending, then value within that hand rank
    hands_with_value.sort(key=lambda x: x[2], reverse=True)
    hands_with_value.sort(key=lambda x: x[1], reverse=True)

    # Best pick is the first item in the list
    return hands_with_value[0]


def high_card(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ Return the high card string for this hand """
    rank_histogram, _ = create_cards_histogram(hand)

    for rank in rank_histogram:
        if rank_histogram[rank] > 0:
            return f"high card {hand_rank_names_singular[rank]}", PokerHand.HIGH_CARD, hash_cards(list(hand))

    return None


def is_pair(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a pair, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    highest_card = None
    for rank in rank_histogram:
        highest_card = rank if not highest_card and rank_histogram[rank] > 0 else highest_card
        if rank_histogram[rank] == 2:
            # Remove the pair from the list of cards
            remaining_cards = [c for c in hand if c.rank != rank]

            # Take the hash of the remaining cards, add to the hash of this pair (which is highest priority)
            hash_value = hash_cards(remaining_cards) + (hand_rank_values[rank] * pow(BASE_K, 3))

            return f"a pair of {hand_rank_names_plural[rank]}", PokerHand.PAIR, hash_value

    return None


def is_two_pair(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains two pair, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    two_pair = []
    highest_card = None
    for rank in rank_histogram:
        highest_card = rank if not highest_card and rank_histogram[rank] > 0 else highest_card
        if rank_histogram[rank] == 2:
            two_pair.append(rank)

            # If we've now found our second of the two pair
            if len(two_pair) == 2:
                # Remove the two pair from the list of cards (leaving just a single card)
                remaining_card = [c for c in hand if c.rank not in two_pair]

                # Take the hash of the remaining cards, add to the hashes of each of the two pair
                hash_value = hash_cards(remaining_card) + (hand_rank_values[two_pair[1]] * pow(BASE_K, 1)) + (
                        hand_rank_values[two_pair[0]] * pow(BASE_K, 2))

                return f"two pair, {hand_rank_names_plural[two_pair[0]]} and {hand_rank_names_plural[two_pair[1]]}", \
                       PokerHand.TWO_PAIR, hash_value

    return None


def is_three_of_a_kind(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a set, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    highest_card = None
    for rank in rank_histogram:
        highest_card = rank if not highest_card and rank_histogram[rank] > 0 else highest_card

        # If we've found our set
        if rank_histogram[rank] == 3:
            # Remove the set from the list of cards (leaving two cards)
            remaining_cards = [c for c in hand if c.rank != rank]
            # Add the hash of this set, which is higher priority than the kicker cards
            hash_value = hash_cards(remaining_cards) + (hand_rank_values[rank] * pow(BASE_K, 2))

            return f"three of a kind, {hand_rank_names_plural[rank]}", PokerHand.THREE_OF_KIND, hash_value

    return None


def is_straight(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a straight, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    streak = 0
    for i, rank in enumerate(rank_histogram.keys()):
        if i > 0 and rank_histogram[rank] > 0 and rank_histogram[list(rank_histogram.keys())[i - 1]] > 0:
            streak += 1
        else:
            streak = 0

        if streak >= 4:
            top_of_streak = list(rank_histogram.keys())[i - 4]

            # For the hash value, we can just use the top of the streak
            hash_value = hand_rank_values[top_of_streak]

            return f"a straight, {hand_rank_names_singular[rank]} to {hand_rank_names_singular[top_of_streak]}", \
                   PokerHand.STRAIGHT, hash_value

        # Account for low ace
        if i == len(list(rank_histogram.keys())) - 1 and streak == 3 and rank == "2" and any(
                [c for c in hand if c.rank == "A"]):
            # In this case, top is always 5
            top_of_streak = "5"
            # For the hash value, we can just use the top of the streak
            hash_value = hand_rank_values[top_of_streak]
            return f"a straight, {hand_rank_names_singular['A']} to {hand_rank_names_singular[top_of_streak]}", \
                   PokerHand.STRAIGHT, hash_value

    return None


def is_flush(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a flush, return string representation of it """
    rank_histogram, suit_histogram = create_cards_histogram(hand)

    flush_cards = []
    for card in hand:
        if suit_histogram[card.suit] >= 5:
            flush_cards.append(card)

    if len(flush_cards) < 5:
        return None

    highest_card = flush_cards[0].rank
    # For hash value, use highest card in the flush
    hash_value = hand_rank_values[highest_card]
    return f"a flush, {hand_rank_names_singular[highest_card]} high", PokerHand.FLUSH, hash_value


def is_full_house(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a full house, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    highest_three_of_a_kind = None
    highest_pair = None

    for rank in rank_histogram:
        if rank_histogram[rank] == 3:
            highest_three_of_a_kind = rank
            break

    for rank in rank_histogram:
        if rank_histogram[rank] == 2:
            highest_pair = rank
            break

    if highest_three_of_a_kind and highest_pair:
        # Hash value needs to prioritise the three of a kind over the pair
        hash_value = (hand_rank_values[highest_pair] * pow(BASE_K, 0)) + hand_rank_values[
            highest_three_of_a_kind] * pow(BASE_K, 1)

        return f"a full house, {hand_rank_names_plural[highest_three_of_a_kind]} full of " \
               f"{hand_rank_names_plural[highest_pair]}", PokerHand.FULL_HOUSE, hash_value

    return None


def is_four_of_a_kind(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains four of a kind, return string representation of it """
    rank_histogram, _ = create_cards_histogram(hand)

    highest_card = None
    for rank in rank_histogram:
        highest_card = rank if not highest_card and rank_histogram[rank] > 0 else highest_card
        if rank_histogram[rank] == 4:
            # Remove the four from the list of cards (leaving one card)
            remaining_card = [c for c in hand if c.rank != rank]
            # Add the hash of this set, which is higher priority than the kicker cards
            hash_value = hash_cards(remaining_card) + (hand_rank_values[rank] * pow(BASE_K, 1))

            return f"four of a kind, {hand_rank_names_plural[rank]}", PokerHand.FOUR_OF_KIND, hash_value

    return None


def is_straight_flush(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a straight flush, return string representation of it """
    rank_histogram, suit_histogram = create_cards_histogram(hand)

    flush_cards = []
    for card in hand:
        if suit_histogram[card.suit] >= 5:
            flush_cards.append(card)

    if len(flush_cards) < 5:
        return None

    # Check for a 5 card streak within the flush cards
    streak = 0
    for i, c in enumerate(flush_cards):
        if i > 0:
            this_rank_index = list(hand_rank_counter.keys()).index(c.rank)
            prev_rank_index = list(hand_rank_counter.keys()).index(flush_cards[i - 1].rank)
            if this_rank_index == prev_rank_index + 1:
                streak += 1

            if streak >= 4:
                top_of_streak = flush_cards[i - 4]

                # Hash value is simply highest card in straight
                hash_value = hand_rank_values[top_of_streak.rank]

                return f"a straight flush, {hand_rank_names_singular[c.rank]} to" \
                       f" {hand_rank_names_singular[top_of_streak.rank]}", PokerHand.STRAIGHT_FLUSH, hash_value

            # Account for low ace
            if i == len(flush_cards) - 1 and streak == 3 and c.rank == "2" and any([c for c in hand if c.rank == "A"]):
                # In this case, top is always 5
                top_of_streak = "5"
                # For the hash value, we can just use the top of the streak
                hash_value = hand_rank_values[top_of_streak]
                return f"a straight flush, {hand_rank_names_singular['A']} to" \
                       f" {hand_rank_names_singular[top_of_streak]}", PokerHand.STRAIGHT_FLUSH, hash_value

    return None


def is_royal_flush(hand: Tuple[Card]) -> Optional[Tuple[str, PokerHand, int]]:
    """ If this hand contains a royal flush, return string representation of it """
    straight_flush = is_straight_flush(hand)
    if straight_flush is not None and "Ten to Ace" in straight_flush[0]:
        # All royal straights are equal in hash value
        return "a royal flush", PokerHand.ROYAL_FLUSH, 0

    return None


def create_cards_histogram(cards: Tuple[Card]) -> Tuple[Dict[str, int], Dict[str, int]]:
    """ For a list of cards, return histograms of ranks and suits """
    rank_histogram = deepcopy(hand_rank_counter)
    suit_histogram = deepcopy(hand_suit_counter)

    for card in cards:
        rank_histogram[card.rank] += 1
        suit_histogram[card.suit] += 1

    return rank_histogram, suit_histogram


class PNLogParsingException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message
