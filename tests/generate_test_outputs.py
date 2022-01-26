# -*- coding: utf-8 -*-
""" Provides utility function for generating the examples in the output_examples folder """
import logging
from pathlib import Path

from main import parse_file, save_game_to_file_pokerstars


def generate_outputs():
    """ Generates an example for each input in the input_examples folder"""

    input_folder = Path('.\input_examples').resolve()
    output_folder = Path('.\output_examples').resolve()

    files_to_convert = []
    for child in input_folder.iterdir():
        if child.suffix in [".csv", ".txt"]:
            files_to_convert.append(child)

    print(files_to_convert)

    for file in files_to_convert:
        # Get current input file number for use in output file name
        input_number = file.stem.rsplit('_', 1)[1]

        # Load into game object
        parsed = parse_file(filepath=file)
        if parsed:
            logging.info("File %s was loaded.", file)

            # Hero is CT in these tests
            parsed.set_hero('CT')
            # Save as file
            save_game_to_file_pokerstars(parsed, output_dir=output_folder, new_filename=f"Converted_"
                                                                                        f"Log_{input_number}.txt")
        else:
            raise logging.error("Error when parsing game from file %s", file)


if __name__ == "__main__":
    generate_outputs()
