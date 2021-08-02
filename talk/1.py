# TODO:
# 1. tokenization NO GENERATORS (R)
#    1. stopwords problem - callback
# 2. indexer (sep, stop words), inverted index (K)
# 3. search (K)
import os
from collections import defaultdict
from typing import Callable, TextIO, Dict, Set

index = defaultdict(set)


def tokenization(text: str, sep: set, callback: Callable[[str], bool]) -> list:
    acc = []
    for char in text:
        if char not in sep:
            acc.append(char)
        else:
            token = "".join(acc)
            if callback(token):
                yield token
            acc = []
    if acc:
        yield "".join(acc)


def inverted_index(fd: TextIO, index_: Dict[str, Set]):
    stop_words = {"to", "be", "a", "and", "the", ""}
    sep = {" ", ",", "!", ".", "\n"}
    for token in tokenization(fd.read(), sep, lambda token: token not in stop_words):
        index_[token].add(fd.name)


def search(query: str, index_: Dict[str, Set]) -> Set:
    "keyword AND keyword"
    prev_keyword = ""
    docset = []
    for keyword in tokenization(query, {" "}, lambda x: True):
        if keyword == "AND" and prev_keyword == "":
            raise RuntimeError
        docset.append(index_.get(keyword, set()))
    resultset = docset[0].intersection(*docset[1:])
    return resultset


if __name__ == "__main__":
    for *_, files in os.walk("files"):
        for file in files:
            inverted_index(open(f"files/{file}"), index)
    print(index)
    res = search("Lorem Ipsum", index)
    print(res)
