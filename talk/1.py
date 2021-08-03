# TODO:
# 1. tokenization NO GENERATORS (R)
#    1. stopwords problem - callback
# 2. indexer (sep, stop words), inverted index (K)
# 3. search (K)
import os
from collections import defaultdict, Set
from typing import TextIO, Callable

index = defaultdict(set)


def tokenize(text: str, sep: set, predicate: Callable[[str], bool]) -> list:
    acc = []
    result = []
    for char in text:
        if char not in sep:
            acc.append(char)
        else:
            token = "".join(acc)
            if predicate(token):
                result.append(token)
            acc = []
    if acc:
        token = "".join(acc)
        if predicate(token):
            result.append(token)
    return result


def inverted_index(fd: TextIO) -> None:
    sep = {" ", ",", ".", "!", "?"}
    stop_words = {"the", "a", "at", "to", "be", ""}
    for token in tokenize(fd.read(), sep, lambda x: x not in stop_words):
        index[token].add(fd.name)


# AND
def search(query: str) -> set:
    last_token = ""
    def check_grammar(token: str) -> bool:
        nonlocal last_token
        if token in {"OR", "AND"}:
            if not last_token:
                raise RuntimeError
            return False
        else:
            last_token = token
        return True

    keywords = tokenize(query, {" "}, check_grammar)
    docsets = []
    for keyword in keywords:
        docsets.append(index.get(keyword, set()))
    resultset = docsets[0].intersection(*docsets[1:])
    return resultset


if __name__ == '__main__':
    for *_, files in os.walk("files"):
        for file in files:
            inverted_index(open(f"files/{file}"))
    print(search("Frodo OR Baggins"))
