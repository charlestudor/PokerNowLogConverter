#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" The main entrypoint for the PokerNowLogConverter tool"""

import argparse
import csv
import logging
import sys
from itertools import groupby
from pathlib import Path
from typing import List, Optional

from game import Game
from utils import currencyCCToSymbol, PNLogParsingException


def parse_file(filepath: str, currency: str = "USD", timezone: str = "ET") -> Optional[Game]:
    """ Converts a single file containing a PokerNow game log into a Game object

    Args:
        filepath (str): Path to the input file to be parsed
        currency (str): The currency used in this game. (Used in output)
        timezone (str): The desired timezone. (Used in output)

    Returns:
        obj:Game: The game object created by parsing the log file.
    """
    try:
        lines = []
        for line in csv.reader(open(filepath, encoding="utf-8"), delimiter=","):
            if line[0] != "entry":
                lines.append(line)
        lines.reverse()

        game = Game(poker_now_log=lines, currency=currency, timezone=timezone, original_filename=filepath)
        return game

    except PNLogParsingException:
        logging.error("Error when opening file: Could not parse file %s", filepath)
        return None


def save_game_to_file_pokerstars(game: Game, output_dir: str, new_filename: str = None) -> List[str]:
    """ Takes a game object and saves it as a text file in desired output directory.

    The outputted text file will in the PokerStars format.

    Args:
        game (obj:Game): The game object to be saved
        output_dir (str): The desired output directory to save the new log to.
        new_filename (str): If specified, the output file name.

    Returns:
        List[str]: The list of log lines that were saved to a file.
    """
    try:
        # Get lines to be saved to file
        formatted_lines = game.format_as_pokerstars_log()

        # Metadata used in filename
        first_hand_date_formatted = game.hand_list[0].hand_start_datetime.strftime("%Y-%m-%d-%H%M")
        first_hand_bb = game.hand_list[0].big_blind_amount
        first_hand_ss = game.hand_list[0].small_blind_amount
        first_hand_type = game.hand_list[0].hand_type

        if not new_filename:
            new_filename = f"ConvertedPNLog-{first_hand_date_formatted}-" \
                           f"{first_hand_ss}-{first_hand_bb}-{first_hand_type}.txt"

        # Create output directory create it if it doesn't exist already
        output_path = Path(output_dir).resolve()
        if not output_path.exists():
            output_path.mkdir()
        logging.info("Output directory set to: %s", output_path)

        # Construct path for new file
        new_filename_path = output_path / new_filename

        with open(new_filename_path, "w", encoding="utf-8") as out_file:
            _ = [print(line, file=out_file) for line in formatted_lines]

        logging.info("Saved output file: %s", new_filename_path)
        return formatted_lines
    except Exception as err:
        logging.error("Could not save converted output for game")
        raise err


def add_aliases_interactively(game: Game) -> None:
    """ Groups players seen during a game and asks for user input to provide an alias for each player.

    Called when using tool from command line with -i flag.

    Args:
        game (obj:Game): The Game object to add aliases for.

    Returns:
        None
    """
    seen_players = sorted(list(game.seen_players), key=lambda x: x.player_id)
    seen_players_list = ", ".join(list(map(lambda x: x.player_name_with_id, seen_players)))
    logging.info("*** INTERACTIVE ALIAS SETUP ***")
    logging.info("The following %i players have been seen: %s", len(seen_players), seen_players_list)

    # Group players by ID for better UX when adding aliases
    alias_list = []
    players_grouped = groupby(seen_players, key=lambda x: x.player_id)
    for _, group in players_grouped:
        groups = list(group)
        player = groups[0]
        example_hand = game.find_hand_with_player(player)
        example_hand_time = example_hand.hand_start_datetime.strftime("%Y-%m-%d %H:%M")
        example_hand_players = ", ".join(
            list(map(lambda x: x.alias_name or x.player_name_with_id, example_hand.players)))
        logging.info("Player: %s was seen at %s. Other players were: %s", player.player_name_with_id, example_hand_time,
                     example_hand_players)

        if len(groups) > 1:
            logging.info("This player also went by the names of: %s",
                         ", ".join(list(map(lambda x: x.player_name_with_id, groups))))

        new_alias = input(f"Set a new alias for player: {player.player_name_with_id} (ENTER to skip): ")
        if new_alias:
            for player in groups:
                updated_count = game.update_player_aliases(player.player_name_with_id, new_alias)
                logging.info("Alias %s} was added for player %s (matching %i hands)", new_alias,
                             player.player_name_with_id, updated_count)
                alias_list.append(f"{player.player_name_with_id}={new_alias}")

    updated_seen_players = game.seen_players
    updated_seen_players_list = ", ".join(list(map(lambda x: x.alias_name or x.player_name, updated_seen_players)))
    logging.info("Finished adding aliases. Final aliases are: \"%s\"", ",".join(alias_list))
    logging.info("Final names of players: %s", updated_seen_players_list)


def setup_arg_parser():
    """ Sets up argument parser. Called when running as script / module. """
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputDir", type=str,
                        help="Specify output directory to save logs to. Defaults to current folder.")
    parser.add_argument("-H", "--heroName", type=str,
                        help="Specify the name of the hero. This should match an alias or unique "
                             "'name @ id' of the player who cards are being dealt to.")
    parser.add_argument("-a", "--aliases", type=str,
                        help="Specify a mapping of player ids to aliases. The format should be:"
                             "\'player1=alias1,player2=alias2\'")
    parser.add_argument("-c", "--currency", type=str, help="Set currency being used in games. Defaults to USD")
    parser.add_argument("-tz", "--timezone", type=str, help="Set timezone these games were recorded in. Defaults to ET")

    f_group = parser.add_mutually_exclusive_group()
    f_group.add_argument("-f", "--filename", type=str, help="Specify PokerNow Log file to convert.")
    f_group.add_argument("-d", "--directory", type=str,
                         help="Specify directory containing PokerNow Log files to convert.")

    i_group = parser.add_mutually_exclusive_group()
    i_group.add_argument("-q", "--quiet", action="store_true",
                         help="Run converter tool without outputting to terminal.")
    i_group.add_argument("-i", "--interactive", action="store_true",
                         help="Use interactive mode to set the aliases of players seen in the log")

    args = parser.parse_args()
    return args


def convert_poker_now_files(hero_name: str, input_filename: str = None, input_directory: str = None,
                            raw_input: List = None, output_directory: str = None, currency: str = "USD",
                            timezone: str = "ET", aliases: List[List[str]] = None, save_file: bool = True)\
        -> List[List[str]]:
    """ Converts one or more poker now log files to Pokerstars format.

    Intended to be used as a library function. Not invoked by main script endpoint.

    Args:
        hero_name (str): Hero name
        input_filename (str, optional): File to be converted, if only one to be processed.
        input_directory (str, optional): Path to directory, if converting multiple files.
        raw_input (list, optional): The raw list of log lines, to be used instead of reading from a file.
        output_directory (str, optional): An output directory if files are to be outputted.
        currency (str, optional): Currency to use. USD is default.
        timezone (str, optional): Timezone to use. ET is default
        aliases (List[List[str]], optional): A list of aliases to use in format: [["P1Name", "P1Alias"],..]
        save_file (bool): Whether to save the file to the provided output directory. Default is True.

    Returns:
        List[List[str]]: A list of parsed log lines for each game.
    """

    if not input_filename and not input_directory and not raw_input:
        raise ValueError("Illegal Arguments: Must specify input file, directory or raw input to convert.")

    files_to_convert = []
    if input_filename:
        file_path = Path(input_filename).resolve()
        files_to_convert.append(file_path)

        if not output_directory:
            output_directory = file_path.parent

    elif input_directory:
        dir_path = Path(input_directory).resolve()
        for child in dir_path.iterdir():
            if child.suffix in [".csv", ".txt"]:
                files_to_convert.append(child)

        if not output_directory:
            output_directory = dir_path

    game_objects = []
    for file in files_to_convert:
        logging.info("Attempting to load file: \"%s\"", file)
        parsed = parse_file(file, currency=currency, timezone=timezone)
        if parsed:
            game_objects.append(parsed)
        else:
            logging.error("Error when parsing game from file %s", file)

    if raw_input:
        for ri_log in raw_input:
            # Assuming log isn't already reversed!
            ri_log.reverse()
            parsed = Game(poker_now_log=ri_log, currency=currency, timezone=timezone)
            if parsed:
                game_objects.append(parsed)
            else:
                logging.error("Error when parsing game from raw input")

    formatted_output = []
    for parsed_game in game_objects:
        if aliases:
            for alias in aliases:
                parsed_game.update_player_aliases(alias[0], alias[1])

        # Set hero name
        parsed_game.set_hero(hero_name)

        if save_file:
            # Convert to pokerstars format and save to file
            output = save_game_to_file_pokerstars(parsed_game, output_dir=output_directory)
            formatted_output.append(output)
        else:
            output = parsed_game.format_as_pokerstars_log()
            formatted_output.append(output)
    return formatted_output


def main() -> int:
    """ Main entry point for running converter as a script or module.

    Returns:
        int: Status code 0 or 1. Code 0 does not guarantee conversion was successful.
    """
    args = setup_arg_parser()

    if args.quiet:
        logging.basicConfig(level=logging.ERROR, format="Error: %(message)s", stream=sys.stderr)
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)

    logging.info("Poker Now Log Converter Started...")

    # Enforce various argument requirements

    if not args.heroName:
        logging.error("Hero name must be set (The player cards are being dealt to)."
                      "Use the [-H] flag e.g: main.py -H MyPokerName ./MyPNLog.txt")
        return 1

    if not args.directory and not args.filename:
        logging.error(
            "No files selected. Please use the [-d] flag to specify a directory, or [-f] to specify an individual file")
        return 1

    if args.currency and args.currency not in currencyCCToSymbol.keys():
        logging.error("Specified currency %s not supported. Supported currencies: USD, GBP, EUR, CAD, SEK, PLY",
                      args.currency)
        return 1
    elif args.currency and args.currency in currencyCCToSymbol.keys():
        logging.info("Set currency to: %s (%s)", args.currency, currencyCCToSymbol[args.currency])
        currency = args.currency
    else:
        logging.info("No currency specified. Using USD")
        currency = "USD"

    if args.timezone:
        timezone = args.timezone
    else:
        logging.info("No timezone specified. Using ET")
        timezone = "ET"

    # Get either single file or multiple to convert from arguments
    files_to_convert = []
    if args.filename:
        file_path = Path(args.filename).resolve()
        files_to_convert.append(file_path)
    else:
        dir_path = Path(args.directory).resolve()
        for child in dir_path.iterdir():
            if child.suffix in [".csv", ".txt"]:
                files_to_convert.append(child)

    # Attempt to convert each file
    for file in files_to_convert:
        logging.info("Attempting to load file: \"%s\"", file)

        # Parse file and create game object
        parsed_game = parse_file(file, currency=currency, timezone=timezone)

        if not parsed_game:
            logging.error("File \"%s\" could not be loaded. Skipping...", file)
            continue

        logging.info("File \"%s\" has been loaded. %i hands were found.", file, len(parsed_game.hand_list))

        if args.aliases:
            try:
                aliases = args.aliases.split(",")
                for alias_str in aliases:
                    player_name_with_id = alias_str.split("=")[0]
                    alias_name = alias_str.split("=")[1]
                    updated_count = parsed_game.update_player_aliases(player_name_with_id, alias_name)
                    logging.info("Alias %s was added for player %s (matching %i hands)", alias_name,
                                 player_name_with_id, updated_count)
            except ValueError:
                logging.error("Error adding aliases. Please check format is: \"Player @ ID=\"")

        if args.interactive:
            # If interactive mode set, allow for adding aliases in terminal window
            add_aliases_interactively(parsed_game)

        # Set hero name
        found_hero = parsed_game.set_hero(args.heroName)
        logging.info("Hero %s was found in %i hands.", args.heroName, found_hero)

        # If no output directory was set, use parent of file
        output_directory = args.outputDir if args.outputDir else file.parent

        # Finally export log in correct format
        save_game_to_file_pokerstars(parsed_game, output_dir=output_directory)

    logging.info("Poker Now Log Converter Finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
