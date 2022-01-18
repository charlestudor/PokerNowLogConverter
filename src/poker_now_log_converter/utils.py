# -*- coding: utf-8 -*-
""" Utils module provides useful helper dicts and custom exceptions for PokerNowLogConverter"""

currencyCCToSymbol = dict(USD='$', CAD='$', GBP='£', EUR='€', SEK='kr', PLY='P')


class PNLogParsingException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class InvalidCardException(Exception):
    def __init__(self, message, card):
        super().__init__(message)
        self.card = card
        self.message = message
