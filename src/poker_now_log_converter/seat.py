# -*- coding: utf-8 -*-
""" Provides the Seat class as part of the PokerNowLogConverter data model"""

from dataclasses import dataclass, field
from typing import List

from card import Card
from player import Player


@dataclass
class Seat:
    """ The Seat class represents a seat in a particular hand of poker.

    The Seat class is initialised at the start of a new hand being processed, and is updated as more information
    is gathered. After every line in a hand has been read, the Seat object should be in the correct state for
    providing a summary and other information required to output in the correct format.

    Args:
        seat_number (int): The number of the seat, from 1-10
        seat_player (obj:Player): The Player object sitting at this seat
        stack_size (float): The stack size at the **start** of the hand. This is useful for the Seat summary when
            in the converted log.
        seat_desc (str): The seat description. This is used if the seat is of any particular significance.
            Possible values include " (big blind)", " (small blind)", " (button)"
            Note:
                The space at the start of the seat_desc is important for formatting reasons.
        seat_summary (str): The summary of what happened to the player at the seat.
        seat_run_it_twice_summary (str): A second summary to be appended if the hand was run twice
        seat_hand (str): The final hand this seat had at the end
        seat_hole_cards (str): A string representation of the player's cards if they showed them during the hand.
        seat_hole_cards_obj: (List[Card]): The player's cards if showed (Card objects)
        seat_did_bet (bool): Whether this player bet or not at any point during the hand.
            If they did not, "didn't bet" is added to the summary of this seat at the end.
        collected_amount (float): If the seat ended up collecting chips, the quantity is provided here
    """
    seat_number: int
    seat_player: Player
    stack_size: float
    seat_desc: str = ''
    seat_summary: str = 'didn\'t show and lost'
    seat_run_it_twice_summary: str = ''
    seat_hand: str = ''
    seat_hole_cards: str = ''
    seat_hole_cards_obj: List[Card] = field(default_factory=list)
    seat_did_bet: bool = False
    collected_amount: float = 0
    collected_amount_second_run: float = 0
