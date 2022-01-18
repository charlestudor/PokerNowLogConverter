# -*- coding: utf-8 -*-
""" Provides the Action class as part of the PokerNowLogConverter data model"""
from dataclasses import dataclass

from player import Player


@dataclass
class Action:
    """ The Action class represents a single action made by a player in the active phase of the game.

    Args:
        player (:obj:`Player`): The player object who made this action
        action (str): A string stating which type of action this is.
            Valid actions include: "bet", "check", "fold", "call", "raise", "uncalled bet", "show", "collect
        bet_amount (float, optional): If the action includes a bet amount, it is provided here.
        bet_difference (float, optional): The difference between the bet and the previous bet by this player.
        cards_shown (str, optional): If this is a "show" action, this variable contains the cards shown.
            Note:
                This variable is a single string, not a Card object or list of Card objects.
    """
    player: Player
    action: str
    bet_amount: float = 0
    bet_difference: float = 0
    cards_shown: str = ''
