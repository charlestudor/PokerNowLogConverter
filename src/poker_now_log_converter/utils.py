# -*- coding: utf-8 -*-
""" Utils module provides useful helper dicts and custom exceptions for PokerNowLogConverter"""

currencyCCToSymbol = dict(USD='$', CAD='$', GBP='£', EUR='€', SEK='kr', PLY='P')


def open_text_file(path: str):
    with open(path, encoding="utf-8") as file:
        lines = file.readlines()
        lines = [line.rstrip() for line in lines]
    return lines


class PNLogParsingException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InvalidCardException(Exception):
    def __init__(self, message, card):
        super().__init__(message)
        self.card = card
        self.message = message
