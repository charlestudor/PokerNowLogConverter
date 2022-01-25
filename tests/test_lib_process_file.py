import csv
from pathlib import Path
from typing import List

from game import Game
from main import parse_file
from utils import open_text_file


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


def test_can_construct_game_from_input_file_two() -> Game:
    test_path = './tests/input_examples/Input_Log_002.csv'
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
    lines = open_text_file(test_path)
    assert len(lines) == 95
    return lines


def test_can_open_output_file_two() -> List[str]:
    test_path = Path("./tests/output_examples/Converted_Log_002.txt")
    assert test_path.exists()
    lines = open_text_file(test_path)
    assert len(lines) == 107
    return lines


def test_input_file_one_converts_to_output_file_one() -> None:
    output_lines = test_can_open_output_file_one()
    input_game = test_can_construct_game_from_input_file_one()

    # These settings were used to convert originally
    input_game.set_hero("CT")
    input_game_converted = input_game.format_as_pokerstars_log()

    assert len(output_lines) == len(input_game_converted)

    for i in range(len(output_lines)):
        assert output_lines[i] == input_game_converted[i]


def test_input_file_two_converts_to_output_file_two() -> None:
    output_lines = test_can_open_output_file_two()
    input_game = test_can_construct_game_from_input_file_two()

    input_game_converted = input_game.format_as_pokerstars_log()

    assert len(output_lines) == len(input_game_converted)

    for i in range(len(output_lines)):
        assert output_lines[i] == input_game_converted[i]
