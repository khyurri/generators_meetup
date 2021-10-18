from typing import Callable, TextIO

SEPARATORS = {" ", ",", "!", ".", "\n"}
STOPWORDS = {"to", "be", "a", "and", "the", ""}


def tokenize(text: str, sep: set, predicate: Callable[[str], bool]) -> list:
    pass


def inverted_index(fd: TextIO) -> None:
    pass


def search(query: str) -> set:
    pass
