# &#127137; Poker Now Log Converter &#127137;

[![pypi](https://img.shields.io/pypi/v/poker_now_log_converter.svg)](https://pypi.org/project/poker_now_log_converter/)
[![python](https://img.shields.io/pypi/pyversions/poker_now_log_converter.svg)](https://pypi.org/project/poker_now_log_converter/)
[![Build Status](https://github.com/charlestudor/PokerNowLogConverter/actions/workflows/main.yml/badge.svg?branch=master)](https://github.com/charlestudor/PokerNowLogConverter/actions)

A  command line utility for converting logs from Poker Now games to other formats.


## Introduction

[Poker Now](https://www.pokernow.club) is a free online client for playing Texas Hold'em, Omaha PL and Omaha PL Hi/Lo poker.

Currently the game logs that can be downloaded from the Poker Now client are not supported by most poker analysis programs
such as GTO Wizard, PokerTracker, Holdem Manager, UpSwingPoker etc

**Poker Now Log Converter** can be used to convert Poker Now logs into the PokerStars format for further analysis.

This project was written for my personal use, and is not affiliated, endorsed or sponsored by the Poker Now team.

## Features

- Cross platform: Windows, Mac and Linux
- Supports log files from Poker Now version 0.1.53 (06/24/2020) to present.
- Run from the command line, or include as a python library. (Supports >=Python 3.8)
- Outputs log files in PokerStars format which can then be uploaded into tools such as GTO Wizard, PokerTracker etc for analysis.
- Currently supports only Texas Hold'em cash games.
- Can adjust log output settings such as currency and timezone.
- Use **Interactive Alias Mode** from the command line to easily rename players seen during poker hands to their known aliases.
 
## Installation

Poker Now Log Converter supports Python 3.8 to 3.11.

### 1. Install via [Pip](http://www.pip-installer.org/):

    $ pip install poker-now-log-converter
    $ python -m poker_now_log_converter 

### 2. Install from Git:
    $ git clone git://github.com/charlestudor/PokerNowLogConverter
    $ python setup.py install
    $ python -m poker_now_log_converter 

    
### 3. Use as a script without installing
    $ git clone git://github.com/charlestudor/PokerNowLogConverter
    $ python ./PokerNowLogConverter

## Usage

As a command line tool:

    $ python -m poker_now_log_converter -h
    
    usage: __main__.py [-h] [-o OUTPUTDIR] [-H HERONAME] [-a ALIASES] [-c CURRENCY] [-tz TIMEZONE]
                   [-f FILENAME | -d DIRECTORY] [-q | -i]

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUTDIR, --outputDir OUTPUTDIR
                            Specify output directory to save logs to. Defaults to current folder.
      -H HERONAME, --heroName HERONAME
                            Specify the name of the hero. This should match an alias or unique 'name @ id' of the player
                            who cards are being dealt to.
      -a ALIASES, --aliases ALIASES
                            Specify a mapping of player ids to aliases. The format should
                            be:'player1=alias1,player2=alias2'
      -c CURRENCY, --currency CURRENCY
                            Set currency being used in games. Defaults to USD
      -tz TIMEZONE, --timezone TIMEZONE
                            Set timezone these games were recorded in. Defaults to ET
      -f FILENAME, --filename FILENAME
                            Specify PokerNow Log file to convert.
      -d DIRECTORY, --directory DIRECTORY
                            Specify directory containing PokerNow Log files to convert.
      -q, --quiet           Run converter tool without outputting to terminal.
      -i, --interactive     Use interactive mode to set the aliases of players seen in the log
      
    $ python -m poker_now_log_converter -H CT -f ./PNLogExample.txt -c GBP -tz GMT -i -o ./OutputDir

As a library:

    $ python
    >>> from poker_now_log_converter.main import convert_poker_now_files
    >>> convert_poker_now_files(hero_name="CT", input_filename="./PNLogExample.txt")
    
## Contributing

If you find a bug please [file an issue](https://www.github.com/charlestudor/PokerNowLogConverter/issues?q=is%3Aopen).
Please upload an example log which is broken to aid in fixing.

## License
[MIT](LICENSE.TXT)



Special thanks to Samuel Simões for creating [Poker Now](https://www.pokernow.club), which is a brilliant poker client.
