import os
from collections import defaultdict
from typing import TextIO

index = defaultdict(set)


def tokenization(text: str, sep: set) -> list:
    acc = []
    result = []
    for char in text:
        if char not in sep:
            acc.append(char)
        else:
            token = "".join(acc)
            result.append(token)
            acc = []
    if acc:
        result.append("".join(acc))
    return result


def inverted_index(fd: TextIO):
    stop_words = {"to", "be", "a", "and", "the", ""}
    sep = {" ", ",", "!", ".", "\n"}
    for token in tokenization(fd.read(), sep):
        index[token].add(fd.name)


# support for AND OR NOT
def search(query: str) -> set:
    resultset = set()
    first = True
    prev_keyword = ""
    grammar = {"AND", "OR", "NOT"}
    for keyword in tokenization(query, {" "}):
        if keyword in grammar:
            prev_keyword = keyword
        else:
            if first:
                resultset = index.get(keyword, set())
                first = False
            else:
                if prev_keyword == "AND":
                    resultset = resultset.intersection(index.get(keyword, set()))
                elif prev_keyword == "OR":
                    resultset = resultset.union(index.get(keyword, set()))
                elif prev_keyword == "NOT":
                    resultset = resultset.difference(index.get(keyword, set()))

    return resultset


if __name__ == "__main__":
    for *_, files in os.walk("../files"):
        for file in files:
            inverted_index(open(f"../files/{file}"))
    print(index)
    res = search("hello OR power NOT absolute")
    print(res)
