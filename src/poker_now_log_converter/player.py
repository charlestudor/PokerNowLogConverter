# -*- coding: utf-8 -*-
""" Provides the Player class as part of the PokerNowLogConverter data model"""

from dataclasses import dataclass


@dataclass
class Player:
    """ The Player class represents a player in a particular hand of poker.

    Players start without an alias, which can be set using a method once the game object is constructed. Once an
    alias is set it is
    used in place of the player name when outputting to a log.

    Args:
        player_name (str): The player name from the log. The first part in the "Player @ ID" PokerNow format.
        player_id (str): The ID given by the PokerNow server. The second part in the "Player @ ID" format.
        player_name_with_id (str): This is the entire PokerNow player string in the format "Player @ ID".
        alias_name (str): An alias for this player.
    """
    player_name: str
    player_id: str
    player_name_with_id: str
    alias_name: str = None

    def __hash__(self):
        """ Hash function. If two players have the same name with id, they are identical"""
        return hash(self.player_name_with_id)
