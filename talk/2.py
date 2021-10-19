import os
from collections import Set, defaultdict
from typing import Callable, Generator, TextIO

index = defaultdict(set)

SEPARATORS = {" ", ",", "!", ".", "\n"}
STOPWORDS = {"to", "be", "a", "and", "the", ""}


def tokenization(text: str, sep: set) -> Generator:
    acc = []
    for char in text:
        if char not in sep:
            acc.append(char)
        else:
            token = "".join(acc)
            yield token
            acc = []
    if acc:
        token = "".join(acc)
        yield token


def inverted_index(fd: TextIO) -> None:
    for token in tokenization(fd.read(), SEPARATORS):
        if token not in STOPWORDS:
            index[token].add(fd.name)


# support for AND OR NOT
def search(query: str) -> set:
    resultset = set()
    first = True
    prev_keyword = ""
    grammar = {"and", "or", "not"}
    for keyword in tokenization(query, {" "}, lambda x: True):
        if keyword in grammar:
            prev_keyword = keyword
        else:
            if first:
                resultset = index.get(keyword, set())
                first = False
            else:
                if prev_keyword == "and":
                    resultset = resultset.intersection(index.get(keyword, set()))
                elif prev_keyword == "or":
                    resultset = resultset.union(index.get(keyword, set()))
                elif prev_keyword == "not":
                    resultset = resultset.difference(index.get(keyword, set()))

    return resultset


if __name__ == "__main__":
    for *_, files in os.walk("files"):
        for file in files:
            inverted_index(open(f"files/{file}"))
    print(search("Frodo OR Baggins"))
