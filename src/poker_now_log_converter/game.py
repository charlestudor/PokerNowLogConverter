# -*- coding: utf-8 -*-
""" Provides the Game class as part of the PokerNowLogConverter data model """

import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, DefaultDict

from action import Action
from card import Card
from hand import Hand
from player import Player
from seat import Seat
from utils import currencyCCToSymbol, eval_final_hand


class Game:
    """ A class representing a game of poker, which is comprised of many hands of poker.

    The Game class is initialised using a list of strings which comprise a PokerNow log. The initializer reads the
    log line by line, creating Hand objects for each hand in the log, which are stored in a list of hands.

    Once the game object is initialised, the hero name or aliases can be set, which propagates to each hand in the list.

    Finally, the game can be output in the desired format (currently only PokerStars format) using the
    format_as_pokerstars_log() function.

    Attributes:
        self.hand_list (List[Hand]): The list of hands that happened during this game.
        self.currency (str): The currency used during this game. (e.g GBP)
        self.currency_symbol (str): The currency symbol used during this game. (e.g £)
        self.timezone (str): The timezone of this game (e.g GMT)
        self.original_file_path (str): If this game was constructed using a log file, this contains the path.
        self.seen_players (Set[Player]): The set of players observed in all of the hands in this game. It is
                                         calculated after all hands have been constructed.

    """

    def __init__(self, poker_now_log: List[List[str]], currency: str = "USD", timezone: str = "ET",
                 original_filename: str = None):
        """ The initializer for a game object. Requires PokerNow log strings as input to parse

        Args:
            poker_now_log (List[List[str]]): The list of PokerNow log lines to parse.
            currency (str): The currency used in this game (e.g USD)
            timezone (str): The timezone of this game (e.g GMT)
            original_filename (str): If this game was constructed using a log file, this contains the path.
        """
        self.hand_list: List[Hand] = []
        self.currency: str = currency
        self.currency_symbol: str = currencyCCToSymbol[currency]
        self.timezone: str = timezone
        self.original_file_path: str = original_filename

        self.is_bomb_pot = False
        # The hand currently being parsed during initialisation. This initial Hand object won't actually be
        # used, it should encounter a -- starting hand -- statement straight away.
        current_hand: Hand = Hand()
        # The game state of the hand being parsed
        current_hand_state: str = "before Flop"
        # The current largest bet in this street of the hand being parsed
        current_hand_street_max_bet: float = 0

        # Helper dictionary to keep track of what a given player did last in this hand while parsing.
        # The key is the player_name_with_id attribute.
        prev_action_dict: DefaultDict[str, float] = defaultdict(float)
        street_action_dict: Dict[str, List[Action]] = {}

        poker_now_log = self.preprocess_log(poker_now_log)

        # Iterate over the log, building a new Hand object for each played hand
        for row in poker_now_log:
            line = row[0]

            if "-- starting hand " in line:
                # Initialise new hand object
                current_hand = Hand()
                prev_action_dict = defaultdict(float)
                street_action_dict = {"before Flop": current_hand.pre_flop_actions,
                                      "on the Flop": current_hand.flop_actions,
                                      "on the Turn": current_hand.turn_actions,
                                      "on the River": current_hand.river_actions,
                                      "at Showdown": current_hand.showdown_actions,
                                      "at second Showdown": current_hand.run_it_twice_showdown_actions}
                current_hand_state = "before Flop"
                current_hand_street_max_bet = 0

                if "Hold\'em" in line:
                    current_hand.hand_type = "Hold\'em No Limit"
                else:
                    current_hand.hand_type = "Omaha Pot Limit"

                if "dealer:" in line:
                    dealer_name_with_id = line.split("dealer: \"")[1].split("\") --")[0]
                    dealer_name = dealer_name_with_id.split(" @ ")[0]
                    dealer_id = dealer_name_with_id.split(" @ ")[1]
                    current_hand.dealer = Player(player_name=dealer_name, player_name_with_id=dealer_name_with_id,
                                                 player_id=dealer_id)

                current_hand.hand_start_datetime = datetime.fromisoformat(row[1][:-1])
                current_hand.hand_number = int(line.split("hand #")[1].split(" (")[0])

            elif "-- ending hand " in line:
                self.hand_list.append(current_hand)
                if current_hand.dealer:
                    current_hand.get_seat_by_player_name_with_id(
                        current_hand.dealer.player_name_with_id).seat_desc += " (button)"

            elif "posts a bet of" in line and "bomb pot bet" in line:
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                bet_amount_str = line.split("posts a bet of ")[1].split(" (bomb pot bet)")[0]
                bet_amount = float(bet_amount_str)
                current_hand_street_max_bet = bet_amount
                prev_action_dict[player_name_with_id] = bet_amount

                current_hand.is_bomb_pot = True
                current_hand.pre_flop_actions.append(Action(player=p_obj, bet_amount=bet_amount, action="bet"))

                # Update button and blind positions based on the UTG player
                utg_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                utg_seat_number = utg_seat.seat_number

                # Clear previous blind and button information
                current_hand.dealer = None
                current_hand.small_blind_seat = None
                current_hand.small_blind_player = None
                current_hand.small_blind_amount = 0
                current_hand.big_blind_seats = []
                current_hand.big_blind_players = []
                current_hand.big_blind_amount = 0

                # Update button and blind positions
                num_seats = len(current_hand.seats)
                available_seats = [seat for seat in current_hand.seats if seat.stack_size > 0]

                if available_seats:
                    utg_seat = available_seats[0]
                    utg_seat_number = utg_seat.seat_number

                    button_seat_number = (utg_seat_number - 2) % num_seats
                    small_blind_seat_number = (utg_seat_number - 1) % num_seats
                    big_blind_seat_number = utg_seat_number

                    button_seat = next(
                        (seat for seat in current_hand.seats if seat.seat_number == button_seat_number), None)
                    small_blind_seat = next(
                        (seat for seat in current_hand.seats if seat.seat_number == small_blind_seat_number), None)
                    big_blind_seat = next(
                        (seat for seat in current_hand.seats if seat.seat_number == big_blind_seat_number), None)

                    if button_seat:
                        current_hand.dealer = button_seat.seat_player
                    if small_blind_seat:
                        current_hand.small_blind_seat = small_blind_seat
                        current_hand.small_blind_player = small_blind_seat.seat_player
                    if big_blind_seat:
                        current_hand.big_blind_seats = [big_blind_seat]
                        current_hand.big_blind_players = [big_blind_seat.seat_player]
                else:
                    # If no available seats, assume button is at seat 1
                    button_seat = next((seat for seat in current_hand.seats if seat.seat_number == 1), None)
                    if button_seat:
                        current_hand.dealer = button_seat.seat_player

            elif "\" raises" in line:
                line = line.replace(" and go all in", "")
                line = line.replace(" and all in", "")
                line = line.replace("with ", "to ")
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                raise_amount = float(line.split("to ")[1])
                difference = raise_amount - current_hand_street_max_bet
                current_hand_street_max_bet = raise_amount
                prev_action_dict[player_name_with_id] = raise_amount

                street_action_dict[current_hand_state].append(
                    Action(player=p_obj, bet_amount=raise_amount, bet_difference=difference, action="raise"))

                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if p_seat:
                    p_seat.seat_did_bet = True

            elif "\" bets" in line:
                line = line.replace(" and go all in", "")
                line = line.replace(" and all in", "")
                line = line.replace(" with", "")
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                bet_amount = float(line.split("bets ")[1])
                current_hand_street_max_bet = bet_amount
                prev_action_dict[player_name_with_id] = bet_amount

                street_action_dict[current_hand_state].append(Action(player=p_obj, bet_amount=bet_amount, action="bet"))

                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if p_seat:
                    p_seat.seat_did_bet = True

            elif "\" calls" in line:
                line = line.replace(" and go all in", "")
                line = line.replace(" and all in", "")
                line = line.replace(" with", "")
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)

                if "bomb pot bet" in line:
                    call_amount_str = line.split("calls ")[1].split(" (bomb pot bet)")[0]
                else:
                    call_amount_str = line.split("calls ")[1]

                call_amount = float(call_amount_str)
                difference = call_amount - prev_action_dict[player_name_with_id]
                prev_action_dict[player_name_with_id] = call_amount

                street_action_dict[current_hand_state].append(
                    Action(player=p_obj, bet_amount=difference, action="call"))

                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if p_seat:
                    p_seat.seat_did_bet = True
            elif "\" checks" in line:
                # print(line)
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)

                street_action_dict[current_hand_state].append(Action(player=p_obj, action="check"))

                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if p_seat:
                    p_seat.seat_did_bet = True

            elif line.startswith("Uncalled bet"):
                player_name_with_id = line.split(" \"")[1].split("\"")[0]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                uncalled_bet_amount = float(line.split("Uncalled bet of ")[1].split(" returned")[0])
                current_hand.uncalledBetSize = uncalled_bet_amount
                current_hand_street_max_bet -= uncalled_bet_amount

                street_action_dict[current_hand_state].append(
                    Action(player=p_obj, bet_amount=uncalled_bet_amount, action="uncalled bet"))

                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if p_seat:
                    p_seat.seat_did_bet = True

            elif "\" folds" in line:
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                p_seat.seat_summary = f"folded {current_hand_state}"
                if not p_seat.seat_did_bet:
                    p_seat.seat_summary += " (didn\'t bet)"

                street_action_dict[current_hand_state].append(Action(player=p_obj, action="fold"))

            elif " big blind of " in line:
                line = line.replace(" and go all in", "")
                line = line.replace("missed ", "")
                big_blind_amount = float(line.split("\" posts a big blind of ")[1])
                big_blind_player_name_with_id = line.split("\" ")[0].split("\"")[1]
                # big_blind_player_name = line.split("\" ")[0].split("\"")[1].split(" @ ")[0]
                big_blind_seat = next((seat for seat in current_hand.seats if
                                       seat.seat_player.player_name_with_id == big_blind_player_name_with_id), None)
                big_blind_seat.seat_did_bet = True
                big_blind_seat.seat_desc = " (big blind)"
                if big_blind_amount > current_hand_street_max_bet:
                    current_hand_street_max_bet = big_blind_amount
                prev_action_dict[big_blind_player_name_with_id] = big_blind_amount

                current_hand.big_blind_seats.append(big_blind_seat)
                current_hand.big_blind_amount = big_blind_amount
                current_hand.big_blind_players.append(
                    current_hand.get_player_by_player_name_with_id(big_blind_player_name_with_id))

            elif " posts a straddle " in line:
                line = line.replace(" and go all in", "")
                straddle_amount = float(line.split("\" posts a straddle of ")[1])
                straddle_player_name_with_id = line.split("\" ")[0].split("\"")[1]
                straddle_player = current_hand.get_player_by_player_name_with_id(straddle_player_name_with_id)
                straddle_seat = next((seat for seat in current_hand.seats if
                                      seat.seat_player.player_name_with_id == straddle_player_name_with_id), None)
                straddle_seat.seat_did_bet = True
                if straddle_amount > current_hand_street_max_bet:
                    current_hand_street_max_bet = straddle_amount
                prev_action_dict[straddle_player_name_with_id] = straddle_amount

                current_hand.straddle_player = straddle_player
                current_hand.straddle_amount = straddle_amount
                current_hand.straddle_seat = straddle_seat

            elif " small blind of " in line:
                line = line.replace(" and go all in", "")
                if "missing " in line:
                    line = line.replace("missing ", "")
                    small_blind_amount = float(line.split("\" posts a small blind of ")[1])
                    small_blind_player_name_with_id = line.split("\" ")[0].split("\"")[1]
                    # small_blind_player_name = line.split("\" ")[0].split("\"")[1].split(" @ ")[0]
                    small_blind_seat = current_hand.get_seat_by_player_name_with_id(small_blind_player_name_with_id)
                    small_blind_seat.seat_did_bet = True
                    small_blind_seat.seat_desc = " (small blind)"
                    if small_blind_amount > current_hand_street_max_bet:
                        current_hand_street_max_bet = small_blind_amount

                    # prev_action_dict[small_blind_player_name_with_id] = small_blind_amount

                    current_hand.missing_small_blinds.append(
                        current_hand.get_player_by_player_name_with_id(small_blind_player_name_with_id))
                else:
                    small_blind_amount = float(line.split("\" posts a small blind of ")[1])
                    small_blind_player_name_with_id = line.split("\" ")[0].split("\"")[1]
                    # small_blind_player_name = line.split("" ")[0].split(""")[1].split(" @ ")[0]
                    small_blind_seat = next((seat for seat in current_hand.seats if
                                             seat.seat_player.player_name_with_id == small_blind_player_name_with_id),
                                            None)
                    small_blind_seat.seat_did_bet = True
                    small_blind_seat.seat_desc = " (small blind)"
                    if small_blind_amount > current_hand_street_max_bet:
                        current_hand_street_max_bet = small_blind_amount
                    prev_action_dict[small_blind_player_name_with_id] = small_blind_amount

                    current_hand.small_blind_seat = small_blind_seat
                    current_hand.small_blind_amount = small_blind_amount
                    current_hand.small_blind_player = current_hand.get_player_by_player_name_with_id(
                        small_blind_player_name_with_id)

            elif line.startswith("Players stacks"):
                # Legacy log format has an s on Players (and other changes)
                seat_number = 0
                players = line.split("Players stacks: ")[1].split(" | ")
                for player in players:
                    seat_number += 1
                    player_name_with_id = player.split("\"")[1].split("\"")[0]
                    player_name = player_name_with_id.split(" @ ")[0]
                    player_id = player_name_with_id.split(" @ ")[1]
                    player_obj = Player(player_name=player_name, player_name_with_id=player_name_with_id,
                                        player_id=player_id)
                    stack_size = float(player.split("\" (")[1].split(")")[0])

                    current_hand.players.append(player_obj)
                    current_hand.seats.append(
                        Seat(seat_player=player_obj, seat_number=seat_number, stack_size=stack_size))

            elif line.startswith("Player stacks"):
                players = line.split("Player stacks: ")[1].split(" | ")
                for player in players:
                    player_name_with_id = player.split(" \"")[1].split("\"")[0]
                    player_name = player_name_with_id.split(" @ ")[0]
                    player_id = player_name_with_id.split(" @ ")[1]
                    player_obj = Player(player_name=player_name, player_name_with_id=player_name_with_id,
                                        player_id=player_id)
                    seat_number = int(player.split(" \"")[0].split("#")[1])
                    stack_size = float(player.split("\" (")[1].split(")")[0])

                    current_hand.players.append(player_obj)
                    current_hand.seats.append(
                        Seat(seat_player=player_obj, seat_number=seat_number, stack_size=stack_size))
            elif line.startswith("Your hand"):
                hole_cards = [Card(x) for x in line.split("Your hand is ")[1].split(", ")]
                current_hand.hole_cards = hole_cards
            elif line.startswith("flop:") or line.startswith("Flop:"):
                flop_cards = [Card(x) for x in line.split("[")[1].split("]")[0].split(", ")]
                current_hand.flop_cards = flop_cards
                current_hand.board.extend(flop_cards)
                current_hand_state = "on the Flop"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif line.startswith("turn:") or line.startswith("Turn:"):
                turn_card = Card(line.split("[")[1].split("]")[0])
                current_hand.turn_card = turn_card
                current_hand.board.append(turn_card)
                current_hand_state = "on the Turn"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif line.startswith("river:") or line.startswith("River:"):
                river_card = Card(line.split("[")[1].split("]")[0])
                current_hand.river_card = river_card
                current_hand.board.append(river_card)
                current_hand_state = "on the River"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif line.startswith("Flop (second run):"):
                second_flop_cards = [Card(x) for x in line.split("[")[1].split("]")[0].split(", ")]
                current_hand.run_it_twice_flop_cards = second_flop_cards
                current_hand.run_it_twice_board.extend(second_flop_cards)
                current_hand_state = "on the Flop"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif line.startswith("Turn (second run):"):
                second_turn_card = Card(line.split("[")[1].split("]")[0])
                current_hand.run_it_twice_turn_card = second_turn_card
                current_hand.run_it_twice_board.append(second_turn_card)
                current_hand_state = "on the Turn"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif line.startswith("River (second run):"):
                second_river_card = Card(line.split("[")[1].split("]")[0])
                current_hand.run_it_twice_river_card = second_river_card
                current_hand.run_it_twice_board.append(second_river_card)
                current_hand_state = "on the River"
                current_hand_street_max_bet = 0
                prev_action_dict = defaultdict(float)
            elif "\" shows a " in line:
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)

                card_objects = [Card(x) for x in line.split('shows a ')[1].split('.')[0].split(', ')]
                cards = f"[{' '.join([c.card_str for c in card_objects])}]"
                p_seat.seat_hole_cards = cards
                p_seat.seat_hole_cards_obj = card_objects

                street_action_dict[current_hand_state].append(Action(player=p_obj, action="show", cards_shown=cards))

            elif "\" collected " in line or "\" gained " in line or " wins " in line:
                line = line.replace("gained", "collected")
                current_hand_state = "at second Showdown" if "second run" in line else "at Showdown"

                if " wins " in line:
                    # Legacy log format
                    collected_amount = float(line.split("\" wins ")[1].split(" with")[0])
                else:
                    collected_amount = float(line.split("\" collected ")[1].split(" from pot")[0])

                # PokerNow seems to calculate collected amount wrong when there are missing small blinds, so subtract
                # them here. Double check this is not an issue, then remove this comment block
                # TODO: What happens with a split pot and missing small blind?
                # if len(current_hand.missing_small_blinds) > 0:
                #     collected_amount -= (current_hand.small_blind_amount * len(current_hand.missing_small_blinds))

                current_hand.total_pot += collected_amount

                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_seat = current_hand.get_seat_by_player_name_with_id(player_name_with_id)
                if "second run" in line:
                    p_seat.collected_amount_second_run += collected_amount
                else:
                    p_seat.collected_amount += collected_amount

                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                street_action_dict[current_hand_state].append(
                    Action(player=p_obj, action="collect", bet_amount=collected_amount))

                if " with " in line:

                    # This is for old logs, you had to get their hole cards from this collection line
                    if "(hand: " in line:
                        hole_card_objects = [Card(x) for x in line.split("(hand: ")[1].split(")")[0].split(", ")]
                        hole_cards = " ".join([c.card_str for c in hole_card_objects])
                        p_seat.seat_hole_cards = f"[{hole_cards}]"
                        p_seat.seat_hole_cards_obj = hole_card_objects

                    # If this is a second run, handle it slightly differently
                    if "second run" in line:
                        # Calculate the winning hand ourselves
                        winning_hand = eval_final_hand(p_seat.seat_hole_cards_obj + current_hand.run_it_twice_board)[0]

                        # OLD: get the hand result from log itself
                        # winning_hand = line.split("with ")[1].split(" on the second run")[0]

                        # Beware of the collected amount here, it is not the total collected, but just from this board
                        p_seat.seat_run_it_twice_summary = ", and won " \
                                                           f"({self.currency_symbol}" \
                                                           f"{p_seat.collected_amount_second_run:,.2f}) " \
                                                           f"with {winning_hand}"

                    else:
                        # Calculate the winning hand ourselves
                        winning_hand = eval_final_hand(p_seat.seat_hole_cards_obj + current_hand.board)[0]

                        # OLD: get the hand result from log itself
                        # winning_hand = line.split("with ")[1].split(" (")[0]

                        p_seat.seat_summary = f"showed {p_seat.seat_hole_cards} and won " \
                            f"({self.currency_symbol}" \
                            f"{p_seat.collected_amount:,.2f}) " \
                            f"with {winning_hand}"
                else:
                    p_seat.seat_summary = f"collected ({self.currency_symbol}{p_seat.collected_amount:,.2f})"

            elif "All players in hand choose to run it twice." == line:
                current_hand.run_it_twice = True
                current_hand.run_it_twice_from_street = current_hand_state
                current_hand.run_it_twice_board = current_hand.board[:]
            elif " posts an ante of " in line:
                player_name_with_id = line.split("\" ")[0].split("\"")[1]
                p_obj = current_hand.get_player_by_player_name_with_id(player_name_with_id)
                ante_amount = float(line.split(" posts an ante of ")[1])
                current_hand.antes.append((p_obj, ante_amount))
            else:
                if not (
                        "joined" in line or "requested" in line or "quits" in line or "created" in line or "approved"
                        in line or "changed" in line or "enqueued" in line or " stand up " in line or " sit back " in
                        line or " canceled the seat " in line or " decide whether to run it twice" in line or
                        "chooses to  run it twice." in line or "Dead Small Blind" == line or "The admin updated the "
                                                                                             "player " in line or
                        "the admin queued the stack change " in line or "Undealt cards: " in line or "not run it "
                                                                                                     "twice." in line):
                    logging.warning("State not considered: %s", line)

            if current_hand:
                current_hand.raw_strings.append(line)

        self.seen_players = set()
        self.refresh_seen_players()

    @staticmethod
    def preprocess_log(poker_now_log: List[List[str]]) -> List[List[str]]:
        """ Before processing log, remove offending characters that might break parsing.

        Args:
            poker_now_log (List[List[str]]): The log to pre-process

        Returns:
             List[List[str]]: The pre-processed log
        """
        for row in poker_now_log:
            line = row[0]

            # Regex to match players in quotes
            player_regex = re.compile("\"(.*?@.*?)\".*?")
            matches = re.finditer(player_regex, line)
            for match in matches:
                player_str = match.group(1)

                # Split player into name and id
                split_index = player_str.rfind(" @ ")
                name_part = player_str[0:split_index]
                id_part = player_str[split_index + 3:]

                # Remove spaces and double quotes
                name_part = name_part.replace(' ', '').replace('\"', '')

                # Reconstruct player
                processed_player = f"{name_part} @ {id_part}"

                if processed_player != player_str:
                    line = line.replace(player_str, processed_player)
                    row[0] = line

        return poker_now_log

    def set_hero(self, player_name: str):
        """ Sets the hero for every hand in this game.

        This function should be called before outputting a log, as otherwise the "Dealt [cards] to Hero" line
        will not be correct.

        Args:
            player_name (str): This can either be in the PokerNow default format of "Player @ ID" or an alias
                can be used instead, as long as the alias has already been set previously.

        Returns:
            int: Returns the number of hands in which this hero was located.
            This is useful for identifying if the hero was not input correctly (or an alias was not set correctly).
        """
        found_hero_count = 0
        for hand in self.hand_list:
            found = hand.set_hero(player_name)
            if found:
                found_hero_count += 1
        return found_hero_count

    def update_player_aliases(self, player_name_with_id: str, alias: str):
        """ Adds an alias to player mapping to every hand in this game.

        Once an alias is set, it will be used instead of the old "Player @ ID" format when outputting as a new log.
        If a player does not have an alias when the game is output, the standard "Player @ ID" will be used instead.

        Args:
            player_name_with_id (str): The player name in the logs, should be in the format "Player @ ID"
            alias (str): The new name which this player will now be known as.
        Returns:
            int: Returns the number of hands in which this player was located.
            This is useful for identifying if the player name was not set correctly.
        """
        found_match_count = 0
        for hand in self.hand_list:
            player = hand.get_player_by_player_name_with_id(player_name_with_id)
            if player:
                found_match_count += 1
                player.alias_name = alias
        return found_match_count

    def find_hand_with_player(self, player: Player):
        """ Finds any hand that contains a certain player

        Used by the interactive mode to show an example hand containing a player, to aid identification.

        Args:
            player (obj:Player): The player of interest

        Returns:
            obj:Hand: Returns the Hand this player was found in, or None if the player is not found in any hand.
        """
        for hand in self.hand_list:
            if player in hand.players:
                return hand
        return None

    def refresh_seen_players(self):
        """Updates the seen_players class attribute, checking all hands in the hand list."""
        self.seen_players = set()
        for hand in self.hand_list:
            for player in hand.players:
                self.seen_players.add(player)

    def format_as_pokerstars_log(self) -> List[str]:
        """ Converts a Game object to a list of strings representing each hand in the game in the PokerStars format

        Returns:
            List[str]: A list of strings representing the game. Each hand is output in turn, with three blank lines
            separating hands.
        """
        output_lines = []

        for hand in self.hand_list:
            hand_pokerstars_output = hand.format_as_pokerstars_hand(currency=self.currency,
                                                                    currency_symbol=self.currency_symbol,
                                                                    timezone=self.timezone,
                                                                    file_path_seed=self.original_file_path)
            output_lines.extend(hand_pokerstars_output)

            # End with blank lines
            output_lines.append("")
            output_lines.append("")
            output_lines.append("")

        return output_lines
