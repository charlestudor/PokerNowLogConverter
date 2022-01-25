# -*- coding: utf-8 -*-
""" Provides the Hand class as part of the PokerNowLogConverter data model"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from random import getrandbits, seed
from typing import List

from action import Action
from card import Card
from player import Player
from seat import Seat
from utils import PNLogParsingException


@dataclass
class Hand:
    """ The Hand class represents a hand of poker that takes place within a Game.

    The Hand is constructed in the Game module by reading the log line by line.

    Note:
        The hand "begins" when the "--- begin hand #X ---" log line is read, however the hand does not "end" until
        the following "--- begin hand #X+1 ---" log line is observed (or the end of the file is reached). This is
        because some actions such as a player voluntarily showing their cards at the end of the hand are reported
        between the "--- end hand #X ---" and the "--- begin hand #X+1 ---" lines

    Attributes:
        raw_strings (List[str]): For debug purposes. All of the log strings that were used to construct this object

        hand_type (str): If this is a Texas Hold'Em hand or Omaha. TODO: ( omaha not currently supported)
        hand_start_datetime (datetime): The time of the hand starting. Note: Timezone is not provided by the PN log so
                                        must be provided by the user.
        hand_number (int): The numerical hand number provided by the PN log.
        seats (List[Seat]): A list of Seat objects, one for each player sat down at the table.

        hole_cards (List[Card]): The hole cards dealt to the hero, if observed.
        flop_cards (List[Card]): The community flop cards, if dealt.
        turn_card (obj:Card): The community turn card, if dealt.
        river_card (obj:Card): The community river card, if dealt.
        board (List[Card]): A list of all community cards.
        total_pot (float): The size of the pot at the end of the hand.

        players (List[Player]): A list of player objects for each player in this hand.
        dealer (obj:Player): The player object for the dealer in this hand. Note: dealer is also known as the button
        hero_player (obj:Player): The player object for the hero in this hand, if there is a match. Hero is set using
                                the set_hero() function after the game is parsed.

        small_blind_player (obj:Player): The player object for the small blind player.
        small_blind_seat (obj:Seat): The seat object for the small blind player.
        small_blind_amount (float): The size of the small blind in this hand

        big_blind_players (List[Player]): The list of players posting a big blind in this hand. (Can be multiple)
        big_blind_seats (List[Seat]): The list of big blind seats in this hand. (Can be multiple)
        big_blind_amount (float): The size of the big blind in this hand

        missing_small_blinds (List[Player]): The list of players who posted a missing or penalty small blind this hand.

        pre_flop_actions (List[Action]): List of Actions that occurred before the flop
        flop_actions (List[Action]): List of Actions that occurred on the flop
        turn_actions (List[Action]): List of Actions that occurred on the turn
        river_actions (List[Action]): List of Actions that occurred on the river
        showdown_actions (List[Action]): List of Actions that occurred at showdown
    """
    raw_strings: List[str] = field(default_factory=list)
    hand_type: str = None
    hand_start_datetime: datetime = None
    hand_number: int = 0
    seats: List[Seat] = field(default_factory=list)

    hole_cards: List[Card] = field(default_factory=list)
    flop_cards: List[Card] = field(default_factory=list)
    turn_card: Card = None
    river_card: Card = None
    board: List[Card] = field(default_factory=list)
    total_pot: float = 0

    players: List[Player] = field(default_factory=list)
    dealer: Player = None
    hero_player: Player = None
    small_blind_player: Player = None
    small_blind_seat: Seat = None
    small_blind_amount: float = 0
    big_blind_players: List[Player] = field(default_factory=list)
    big_blind_seats: List[Seat] = field(default_factory=list)
    big_blind_amount: float = 0

    missing_small_blinds: List[Player] = field(default_factory=list)

    pre_flop_actions: List[Action] = field(default_factory=list)
    flop_actions: List[Action] = field(default_factory=list)
    turn_actions: List[Action] = field(default_factory=list)
    river_actions: List[Action] = field(default_factory=list)
    showdown_actions: List[Action] = field(default_factory=list)

    def get_seat_by_player_name_with_id(self, player_name_with_id: str) -> Seat:
        """ Gets a seat in this hand where a given player is sat, if it exists.

        Args:
            player_name_with_id (str): The player to find.

        Returns:
            obj:Seat: The matched seat
        """
        return next((seat for seat in self.seats if seat.seat_player.player_name_with_id == player_name_with_id), None)

    def get_player_by_player_name_with_id(self, player_name_with_id: str) -> Player:
        """ Gets a player in this hand that matches a player name with id, if it exists

        Args:
            player_name_with_id (str): The player to find.

        Returns:
            obj:Player: The matched player
        """
        return next((p for p in self.players if p.player_name_with_id == player_name_with_id), None)

    def get_player_by_player_alias(self, player_alias: str) -> Player:
        """ Gets a player in this hand that matches an alias, if it exists

        Args:
            player_alias (str): The player to find.

        Returns:
            obj:Player: The matched player
        """
        return next((p for p in self.players if p.alias_name == player_alias), None)

    def get_player_by_player_name(self, player_name: str) -> Player:
        """ Gets a player in this hand that matches a player name, if it exists

        Args:
            player_name (str): The player to find.

        Returns:
            obj:Player: The matched player
        """
        return next((p for p in self.players if p.player_name == player_name), None)

    def set_hero(self, hero_name: str) -> Player:
        """ Sets the hero in this hand.

        The hero is the player who cards are being dealt to. This information is difficult to work out from the log
        itself, so it's easier if the user states which player is themselves.

        Args:
            hero_name (str): The player to find, input can be player name, name with id, or alias.

        Returns:
            obj:Player: The matched player that is set as the hero, if they are found.
        """
        hero = self.get_player_by_player_alias(hero_name) or self.get_player_by_player_name_with_id(
            hero_name) or self.get_player_by_player_name(hero_name)
        self.hero_player = hero
        return self.hero_player

    @staticmethod
    def format_actions_pokerstars(action_list: List[Action], currency_symbol: str) -> List[str]:
        """ Converts Action objects into the format required by a PokerStars log

        Args:
            action_list (List[Action]): The player actions to be formatted.
            currency_symbol (str): The desired currency symbol to prefix amount values with in the output.

        Returns:
            List[str]: A list of formatted action strings, one for each input action object.
        """
        output_lines = []
        for action in action_list:
            if action.action == "bet":
                output_lines.append(f"{action.player.alias_name or action.player.player_name}: bets "
                                    f"{currency_symbol}{action.bet_amount:,.2f}")
            elif action.action == "check":
                output_lines.append(f"{action.player.alias_name or action.player.player_name}: checks")
            elif action.action == "fold":
                output_lines.append(f"{action.player.alias_name or action.player.player_name}: folds")
            elif action.action == "call":
                output_lines.append(f"{action.player.alias_name or action.player.player_name}: calls "
                                    f"{currency_symbol}{action.bet_amount:,.2f}")
            elif action.action == "raise":
                output_lines.append(f"{action.player.alias_name or action.player.player_name}: raises "
                                    f"{currency_symbol}{action.bet_difference:,.2f} to "
                                    f"{currency_symbol}{action.bet_amount:,.2f}")
            elif action.action == "uncalled bet":
                output_lines.append(f"Uncalled bet ({currency_symbol}{action.bet_amount:,.2f}) returned to "
                                    f"{action.player.alias_name or action.player.player_name}")
            elif action.action == "show":
                output_lines.append(
                    f"{action.player.alias_name or action.player.player_name}: shows {action.cards_shown}")
            elif action.action == "collect":
                output_lines.append(f"{action.player.alias_name or action.player.player_name} collected "
                                    f"{currency_symbol}{action.bet_amount:,.2f} from pot")
            else:
                raise PNLogParsingException(f"Invalid action in actions list: {action}")
        return output_lines

    def format_as_pokerstars_hand(self, currency: str, currency_symbol: str, timezone: str,
                                  file_path_seed: str = None) -> List[str]:
        """ Converts Action objects into the format required by a PokerStars log

        Args:
            currency (str): The name of the currency to add to the hand metadata. (e.g GBP)
            currency_symbol (str): The desired currency symbol to prefix amount values with in the output. (e.g £)
            timezone (str): Timezone to append to the hand datetime (e.g GMT)
            file_path_seed (str, optional): The original file path to be used as a seed to be used for
                                                    generating a hand ID.

        Returns:
            List[str]: A list of strings representing this Hand, in valid PokerStars log hand notation.
        """
        output_lines = []

        # For hand id generate a random number, but deterministic if the seed parameter is supplied
        # This keeps hand ids consistent between generations.
        random_seed = f"{Path(file_path_seed).stem}-{self.hand_number}" if file_path_seed else None
        seed(a=random_seed)
        hand_id = getrandbits(64)

        # Currency formatting
        big_blind = f"{currency_symbol}{self.big_blind_amount:,.2f}"
        small_blind = f"{currency_symbol}{self.small_blind_amount:,.2f}"

        # Date format specified by PokerStars logs
        date_formatted = self.hand_start_datetime.strftime(f"%Y/%m/%d %H:%M:%S {timezone}")

        if not self.dealer:
            # Dead button, select the seat before the small blind
            # (this isn't technically correct, as the button could be an empty seat instead, however it seems to work
            # for now)
            button_seat_id = self.small_blind_seat.seat_number - 1 if self.small_blind_seat.seat_number > 0 else 10
        else:
            button_seat = self.get_seat_by_player_name_with_id(self.dealer.player_name_with_id)
            button_seat_id = button_seat.seat_number

        output_lines.append(
            f"PokerStars Hand #{hand_id}: {self.hand_type} ({small_blind}/{big_blind} {currency}) - {date_formatted}")
        output_lines.append(f"Table 'PNLogConverter' 10-max Seat #{button_seat_id} is the button")

        # List seats
        for seat in self.seats:
            output_lines.append(f"Seat {seat.seat_number}: "
                                f"{seat.seat_player.alias_name or seat.seat_player.player_name} "
                                f"({currency_symbol}{seat.stack_size:,.2f} in chips)")

        # Small blind posted
        if self.small_blind_player:
            output_lines.append(f"{self.small_blind_player.alias_name or self.small_blind_player.player_name}: "
                                f"posts small blind {small_blind}")

        # Big blind(s) posted
        for bb_player in self.big_blind_players:
            output_lines.append(f"{bb_player.alias_name or bb_player.player_name}: "
                                f"posts big blind {big_blind}")

        # Missing / penalty small blinds posted
        for missing_small in self.missing_small_blinds:
            output_lines.append(f"{missing_small.alias_name or missing_small.player_name}: "
                                f"posts small blind {small_blind}")

        # Hole cards dealt to hero
        output_lines.append("*** HOLE CARDS ***")
        if self.hero_player and self.hole_cards:
            hole_cards = " ".join(list(map(lambda x: x.card_str, self.hole_cards)))
            output_lines.append(f"Dealt to "
                                f"{self.hero_player.alias_name or self.hero_player.player_name} "
                                f"[{hole_cards}]")

        # Preflop
        pre_flop_actions_str = self.format_actions_pokerstars(self.pre_flop_actions, currency_symbol=currency_symbol)
        output_lines.extend(pre_flop_actions_str)

        # Flop
        flop_cards = " ".join(list(map(lambda x: x.card_str, self.flop_cards))) if len(self.flop_cards) > 0 else None
        if flop_cards:
            output_lines.append(f"*** FLOP *** [{flop_cards}]")
            flop_actions_str = self.format_actions_pokerstars(self.flop_actions, currency_symbol=currency_symbol)
            output_lines.extend(flop_actions_str)

        # Turn
        turn_card = self.turn_card.card_str if self.turn_card else None
        if turn_card:
            output_lines.append(f"*** TURN *** [{flop_cards}] [{turn_card}]")
            turn_actions_str = self.format_actions_pokerstars(self.turn_actions, currency_symbol=currency_symbol)
            output_lines.extend(turn_actions_str)

        # River
        river_card = self.river_card.card_str if self.river_card else None
        if river_card:
            output_lines.append(f"*** RIVER *** [{flop_cards} {turn_card}] [{river_card}]")
            river_actions_str = self.format_actions_pokerstars(self.river_actions, currency_symbol=currency_symbol)
            output_lines.extend(river_actions_str)

        # Showdown
        output_lines.append("*** SHOW DOWN ***")
        showdown_actions_str = self.format_actions_pokerstars(self.showdown_actions, currency_symbol=currency_symbol)
        output_lines.extend(showdown_actions_str)

        # Summary
        output_lines.append("*** SUMMARY ***")
        output_lines.append(f"Total pot: {currency_symbol}{self.total_pot:,.2f} | Rake 0")

        if len(self.board) > 0:
            board = " ".join(list(map(lambda x: x.card_str, self.board)))
            output_lines.append(f"Board: [{board}]")

        for seat in self.seats:
            summary = f"Seat {seat.seat_number}: " \
                      f"{seat.seat_player.alias_name or seat.seat_player.player_name}{seat.seat_desc} " \
                      f"{seat.seat_summary}"
            # If we know the hole cards (and they weren't mentioned earlier in the summary, put them at the end)
            if "showed" not in seat.seat_summary and seat.seat_hole_cards:
                summary += " " + seat.seat_hole_cards
            output_lines.append(summary)

        return output_lines
