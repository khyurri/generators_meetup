import os
import selectors
import socket
import time
from collections import defaultdict, Set, deque
from typing import TextIO, Callable, Generator

index = defaultdict(set)

sel = selectors.DefaultSelector()


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


def inverted_index() -> Generator:
    sep = {" "}
    stop_words = {}
    while True:
        name, chunk = yield
        for token in tokenize(chunk, sep):
            if token not in stop_words:
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


if __name__ == '__main__':

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