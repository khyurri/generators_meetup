# TODO:
# add partial_indexer
import os
import selectors
import socket
import time
from collections import defaultdict, deque
from typing import Callable, TextIO, Dict, Set, Generator


index = defaultdict(set)
sel = selectors.DefaultSelector()


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
        docset.append(index_.get(keyword, set()))
    resultset = docset[0].intersection(*docset[1:])
    return resultset


def read(fd: TextIO):
    for chunk in iter(lambda: fd.readline(), ""):
        yield chunk, fd.name


def read_selector():
    while True:
        events = sel.select(0)
        if events:
            for key, mask in events:
                key.data(key.fileobj)
        yield None, "socket"


def partial_indexer(files_: deque, inv_ind: Generator):
    while files_:
        try:
            file_ = files_.popleft()
            chunk, name = next(file_)
            if name != "socket":
                inv_ind.send((chunk, name))
                print(f"Indexed chunk for {name}")
        except StopIteration:
            print(f"File fully indexed")
        else:
            files_.append(file_)
        time.sleep(1)


def accept(sock):
    conn, addr = sock.accept()
    print(f"New connection from {addr}")
    while True:
        try:
            query = conn.recv(1024).decode('UTF-8').strip()
            print(f"Request: {query}")
            print(index)
            query_result = search(query, index)
            result = []
            if query_result:
                for f in query_result:
                    result.append(f)
            conn.send("\n".join(result).encode('UTF-8'))
            conn.close()
            break
        except BlockingIOError:
            pass
        except BaseException:
            conn.close()


if __name__ == "__main__":

    sock = socket.socket()
    sock.bind(("127.0.0.1", 5555))
    sock.setblocking(False)
    sock.listen(100)
    sel.register(sock, selectors.EVENT_READ, accept)
    sel_reader = read_selector()

    inv_index = inverted_index(index)
    inv_index.__next__()
    files_deq = deque()
    files_deq.append(sel_reader)

    try:
        for *_, files in os.walk("files"):
            for file in files:
                files_deq.append(read(open(f"files/{file}")))
        partial_indexer(files_deq, inv_index)
        inv_index.close()
        print(index)
        print("Search result:")
        res = search("following top-level", index)
        print(res)
    except BaseException:
        sock.close()
