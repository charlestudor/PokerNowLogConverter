# -*- coding: utf-8 -*-
""" Provides the Card class as part of the PokerNowLogConverter data model"""

from dataclasses import dataclass
from typing import Dict, List

strToEmoji: Dict[str, str] = {"c2": "2♣", "c3": "3♣", "c4": "4♣", "c5": "5♣", "c6": "6♣", "c7": "7♣", "c8": "8♣",
                              "c9": "9♣", "cT": "10♣", "cJ": "J♣", "cQ": "Q♣", "cK": "K♣", "cA": "A♣", "d2": "2♦",
                              "d3": "3♦", "d4": "4♦", "d5": "5♦", "d6": "6♦", "d7": "7♦", "d8": "8♦", "d9": "9♦",
                              "dT": "10♦", "dJ": "J♦", "dQ": "Q♦", "dK": "K♦", "dA": "A♦", "h2": "2♥", "h3": "3♥",
                              "h4": "4♥", "h5": "5♥", "h6": "6♥", "h7": "7♥", "h8": "8♥", "h9": "9♥", "hT": "10♥",
                              "hJ": "J♥", "hQ": "Q♥", "hK": "K♥", "hA": "A♥", "s2": "2♠", "s3": "3♠", "s4": "4♠",
                              "s5": "5♠", "s6": "6♠", "s7": "7♠", "s8": "8♠", "s9": "9♠", "sT": "10♠", "sJ": "J♠",
                              "sQ": "Q♠", "sK": "K♠", "sA": "A♠"}

emojiToStr: Dict[str, str] = {"2♣": "2c", "3♣": "3c", "4♣": "4c", "5♣": "5c", "6♣": "6c", "7♣": "7c", "8♣": "8c",
                              "9♣": "9c", "10♣": "Tc", "J♣": "Jc", "Q♣": "Qc", "K♣": "Kc", "A♣": "Ac", "2♦": "2d",
                              "3♦": "3d", "4♦": "4d", "5♦": "5d", "6♦": "6d", "7♦": "7d", "8♦": "8d", "9♦": "9d",
                              "10♦": "Td", "J♦": "Jd", "Q♦": "Qd", "K♦": "Kd", "A♦": "Ad", "2♥": "2h", "3♥": "3h",
                              "4♥": "4h", "5♥": "5h", "6♥": "6h", "7♥": "7h", "8♥": "8h", "9♥": "9h", "10♥": "Th",
                              "J♥": "Jh", "Q♥": "Qh", "K♥": "Kh", "A♥": "Ah", "2♠": "2s", "3♠": "3s", "4♠": "4s",
                              "5♠": "5s", "6♠": "6s", "7♠": "7s", "8♠": "8s", "9♠": "9s", "10♠": "Ts", "J♠": "Js",
                              "Q♠": "Qs", "K♠": "Ks", "A♠": "As"}

ranks_order: List[str] = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]
suits_order: List[str] = ["s", "h", "d", "c"]


class InvalidCardException(Exception):
    def __init__(self, message, card):
        super().__init__(message)
        self.card = card
        self.message = message


@dataclass(frozen=True)
class Card:
    """ Class for representing a single card from a standard 52 card deck.

    Contains a standard string representation of rank and suit e.g "8s",
    and also a version including a unicode emoji for the suit (used by default in the PokerNow logs)
    """
    __slots__ = ["rank", "suit", "card_str", "card_emoji_str"]
    card_str: str
    card_emoji_str: str
    rank: str
    suit: str

    def __init__(self, name: str):
        """
        Initializer for the Card class.
        Args:
            name: String representing the card, in either standard or emoji format
        """
        if name in strToEmoji:
            # Frozen is set to True, so cannot change these in the usual manner
            super().__setattr__("card_emoji_str", strToEmoji.get(name))
            super().__setattr__("card_str", emojiToStr.get(self.card_emoji_str))
            super().__setattr__("rank", self.card_str[0])
            super().__setattr__("suit", self.card_str[1:])

        elif name in emojiToStr:
            super().__setattr__("card_emoji_str", name)
            super().__setattr__("card_str", emojiToStr.get(name))
            super().__setattr__("rank", self.card_str[0])
            super().__setattr__("suit", self.card_str[1:])

        else:
            raise InvalidCardException(f"Invalid Card {name}", name)

    def __repr__(self):
        return self.card_str

    def __hash__(self):
        return hash(self.card_str)

    def __gt__(self, other):
        if ranks_order.index(self.rank) > ranks_order.index(other.rank):
            return True
        if ranks_order.index(self.rank) == ranks_order.index(other.rank):
            if suits_order.index(self.suit) > suits_order.index(other.suit):
                return True
            else:
                return False
        return False
