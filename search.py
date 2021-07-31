# simple keyword based search, naive intersection
from typing import Set, Dict


def search(query: str, index: Dict[str, Set]) -> Set:
    keywords = query.split(" ")
    docsets = []
    for keyword in keywords:
        docset = index.get(keyword, [])
        docsets.append(docset)
    resultset = docsets[0].intersection(*docsets[1:])
    return resultset


def test_search():
    assert len(search("a", {"a": {1, 2, 3}})) == 3
    assert len(search("a b", {"a": {1, 2, 3}, "b": {2, 3}})) == 2