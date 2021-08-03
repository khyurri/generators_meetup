import os
from collections import defaultdict, Set
from typing import TextIO, Callable, Generator

index = defaultdict(set)


def tokenize(text: str, sep: set) -> Generator:
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
    sep = {" ", ",", ".", "!", "?"}
    stop_words = {"the", "a", "at", "to", "be", ""}
    for token in tokenize(fd.read(), sep):
        if token not in stop_words:
            index[token].add(fd.name)


# AND
def search(query: str) -> set:
    last_token = ""
    docsets = []
    for keyword in tokenize(query, {" "}):
        if keyword in {"OR", "AND"}:
            if not last_token:
                raise RuntimeError
        else:
            last_token = keyword
            docsets.append(index.get(keyword, set()))
    resultset = docsets[0].intersection(*docsets[1:])
    return resultset


if __name__ == '__main__':
    for *_, files in os.walk("files"):
        for file in files:
            inverted_index(open(f"files/{file}"))
    print(search("Frodo OR Baggins"))