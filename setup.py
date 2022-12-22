from setuptools import setup, find_packages

VERSION = "0.0.10"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="poker_now_log_converter",
    version=VERSION,
    author="Charles Tudor",
    author_email="mail@ctudor.net",
    description="A simple command line utility for converting logs from Poker Now games to other formats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/charlestudor/PokerNowLogConverter",
    classifiers=["Programming Language :: Python :: 3.8",
                 "Programming Language :: Python :: 3.9",
                 "Programming Language :: Python :: 3.10",
                 "Programming Language :: Python :: 3.11",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
)
