# TODO:
# 1. tokenization NO GENERATORS (R)
#    1. stopwords problem - callback
# 2. indexer (sep, stop words), inverted index (K)
# 3. search (K)
import os
from collections import defaultdict, deque
from typing import Callable, TextIO, Dict, Set, Generator

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


def inverted_index(index_: Dict[str, Set]):
    stop_words = {"to", "be", "a", "and", "the", ""}
    sep = {" ", ",", "!", ".", "\n"}
    while True:
        text, name = yield
        for token in tokenization(text, sep, lambda token: token not in stop_words):
            index_[token].add(name)


def search(query: str, index_: Dict[str, Set]) -> Set:
    "keyword AND keyword"
    prev_keyword = ""
    docset = []
    for keyword in tokenization(query, {" "}, lambda x: True):
        if keyword == "AND" and prev_keyword == "":
            raise RuntimeError
        docset.append(index_.get(keyword, []))
    resultset = docset[0].intersection(*docset[1:])
    return resultset


def read(fd: TextIO):
    for chunk in iter(lambda: fd.readline(), ""):
        yield chunk, fd.name


def partial_indexer(files_: deque, inv_ind: Generator):
    while files_:
        try:
            file_ = files_.popleft()
            chunk, name = next(file_)
            if name == "socket":
                if chunk:
                    print(search(chunk, index))
            else:
                inv_ind.send((chunk, name))
        except StopIteration:
            print(f"File indexed")
        else:
            files_.append(file_)


def socket_read(sock):
    while True:
        if sock.ready():
            yield sock.read(), "socket"
        else:
            yield "", "socket"


if __name__ == "__main__":
    inv_index = inverted_index(index)
    inv_index.__next__()
    files_deq = deque()
    for *_, files in os.walk("files"):
        for file in files:
            files_deq.append(read(open(f"files/{file}")))
    files_deq.append(socket_read(sock))
    partial_indexer(files_deq, inv_index)
    inv_index.close()
    print(index)
    res = search("Lorem Ipsum", index)
    print(res)
