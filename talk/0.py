from typing import Callable, TextIO


def tokenize(text: str, sep: set, predicate: Callable[[str], bool]) -> list:
    pass


def inverted_index(fd: TextIO) -> None:
    pass


def search(query: str) -> set:
    pass