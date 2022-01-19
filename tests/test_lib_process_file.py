import csv
from pathlib import Path
from typing import List

from game import Game
from main import parse_file


def test_can_open_input_file_one() -> List[List[str]]:
    test_path = Path("./tests/input_examples/Input_Log_001.txt")
    assert test_path.exists()

    lines = []
    for line in csv.reader(open(test_path, encoding="utf-8"), delimiter=","):
        if line[0] != "entry":
            lines.append(line)
    lines.reverse()

    assert len(lines) == 58

    return lines


def test_can_construct_game_from_input_file_one() -> Game:
    test_path = './tests/input_examples/Input_Log_001.txt'
    game_obj = parse_file(test_path)

    assert game_obj is not None
    print(type(game_obj))
    print(Game)
    assert type(game_obj) is Game

    assert len(game_obj.hand_list) == 4

    return game_obj


def test_can_open_output_file_one() -> List[str]:
    test_path = Path("./tests/output_examples/Converted_Log_001.txt")
    assert test_path.exists()

    lines = []
    for line in csv.reader(open(test_path, encoding="utf-8")):
        lines.append(line[0] if line else "")

    assert len(lines) == 95

    return lines


def test_input_file_one_converts_to_output_file_one() -> None:
    output_lines = test_can_open_output_file_one()

    input_game = test_can_construct_game_from_input_file_one()

    # These settings were used to convert originally
    input_game.update_player_aliases("CT @ eNVKMq2Tcb", "CT")
    input_game.set_hero("CT")
    input_game_converted = input_game.format_as_pokerstars_log()

    assert len(output_lines) == len(input_game_converted)

    for i in range(len(output_lines)):

        if "PokerStars Hand" in input_game_converted[i]:
            input_game_converted[i] = ":".join(input_game_converted[i].split(":")[1:])
            output_lines[i] = ":".join(output_lines[i].split(":")[1:])

        assert output_lines[i] == input_game_converted[i]