import os
from collections import defaultdict
from typing import Callable, TextIO

SEPARATORS = {" ", ",", "!", ".", "\n"}
STOPWORDS = {"to", "be", "a", "and", "the", ""}

index = defaultdict(set)

# split text by separators, remove stopwords, and return a list of words
def tokenize(text: str, sep: set, predicate: Callable[[str], bool]) -> list:
    acc = []
    result = []
    for char in text:
        if char in sep:
            if acc:
                token = "".join(acc).lower()
                if predicate(token):
                    result.append(token)
                acc = []
        else:
            acc.append(char)
    if acc:
        token = "".join(acc).lower()
        if predicate(token):
            result.append(token)
    return result


# build inverted index by tokenizing text from file descriptor
def inverted_index(fd: TextIO) -> None:
    for token in tokenize(fd.read(), SEPARATORS, lambda x: x not in STOPWORDS):
        index[token].add(fd.name)


# boolean keyword search with support for and, not, or
def search(query: str) -> set:
    result = set()
    is_first = True
    prev_keyword = ""
    for keyword in tokenize(query, SEPARATORS, lambda x: True):
        prev_keyword = keyword
        if is_first:
            is_first = False
            result = index.get(keyword, set())
        else:
            if keyword in {"and", "or", "not"}:
                match keyword:
                    case "and":
                        result = result & index.get(prev_keyword, set())
                    case "or":
                        result = result | index.get(prev_keyword, set())
                    case "not":
                        result = result - index.get(prev_keyword, set())
    return result


if __name__ == "__main__":
    for *_, files in os.walk("talk/files"):
        for file in files:
            with open(os.path.join("talk/files", file), "r") as fd:
                inverted_index(fd)
    # print(index)
    print(search("petersburg"))