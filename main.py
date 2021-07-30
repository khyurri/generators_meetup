import os
from collections import deque, defaultdict
from typing import Generator, DefaultDict, TextIO


def tokenizer(text: str, splitters: set) -> Generator[str, None, None]:
    acc = []
    for c in text:
        if c in splitters:
            yield "".join(acc)
            acc = []
        else:
            acc.append(c)
    yield "".join(acc)


def tokenize_job(fd: TextIO,
                 splitters: set,
                 stop_words: set,
                 index: DefaultDict[str, set]) -> Generator[None, None, None]:
    for next_token in tokenizer(fd.read(), splitters):
        if next_token not in stop_words:
            index[next_token].add(fd.name)
        yield  # <-- allow other jobs to feel the index


class Scheduler:

    def __init__(self) -> None:
        self.sched = deque()

    def add_to_sched(self,
                     job_name: str,
                     job: Generator[None, None, None]) -> None:
        self.sched.append((job_name, job))

    def run(self) -> None:
        while self.sched:
            job_name, job = self.sched.popleft()
            try:
                next(job)
            except StopIteration:
                print(f"{job_name} completed")
            else:
                self.add_to_sched(job_name, job)


def read_files(src: str) -> Generator[str, None, None]:
    for root, dirs, files in os.walk(src):
        for file in files:
            yield f"{root}/{file}"


if __name__ == "__main__":
    splitters = {" ", ","}
    stop_words = {"i", "am"}
    index = defaultdict(set)
    scheduler = Scheduler()
    for file in read_files("files"):
        job = tokenize_job(open(file), splitters, stop_words, index)
        scheduler.add_to_sched(file, job)

    scheduler.run()

