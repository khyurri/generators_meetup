import os
import selectors
import socket
import time
from collections import Set, defaultdict, deque
from typing import Callable, Generator, TextIO

index = defaultdict(set)

SEPARATORS = {" ", ",", "!", ".", "\n"}
STOPWORDS = {"to", "be", "a", "and", "the", ""}

sel = selectors.DefaultSelector()


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


def inverted_index() -> Generator:
    while True:
        name, chunk = yield
        for token in tokenization(chunk, SEPARATORS):
            if token not in STOPWORDS:
                index[token].add(name)


def read_file(fd: TextIO) -> Generator:
    for chunk in iter(lambda: fd.readline(), ""):
        yield fd.name, chunk


def read_socket() -> Generator:
    while True:
        events = sel.select(0)
        if events:
            for key, addr in events:
                key.data(key.fileobj)
        yield "socket", ""


def reader(files: deque, inv_coro: Generator) -> None:
    while files:
        try:
            file = files.popleft()
            name, chunk = next(file)
            if name != "socket":
                inv_coro.send((name, chunk))
        except StopIteration:
            print("File indexed")
        else:
            files.append(file)
        print(index)
        time.sleep(0.5)


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


def accept(sock: socket.socket) -> None:
    conn, addr = sock.accept()
    print(f"{addr} connected")
    while True:
        try:
            query = conn.recv(1024).decode("utf-8").strip()
            result = search(query)
            for doc in result:
                conn.send(doc.encode("utf-8"))
                conn.send("\n".encode("utf-8"))
            conn.close()
            break
        except BlockingIOError:
            pass
        except BaseException:
            conn.close()


if __name__ == "__main__":

    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", 5555))
        sock.setblocking(False)
        sock.listen()

        sel.register(sock, selectors.EVENT_READ, accept)

        inv_coro = inverted_index()
        next(inv_coro)
        job_queue = deque()
        job_queue.append(read_socket())

        for *_, files in os.walk("files"):
            for file in files:
                job_queue.append(read_file(open(f"files/{file}")))
        reader(job_queue, inv_coro)
        inv_coro.close()
        print(search("Frodo OR Baggins"))
    except BaseException:
        sock.close()
