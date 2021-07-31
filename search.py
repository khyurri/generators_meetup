# simple keyword based search, naive intersection
from typing import Set, Dict


def conjunction_search(query: str, index: Dict[str, Set]) -> Set:
    docsets = docset_extraction(index, query)
    resultset = docsets[0].intersection(*docsets[1:])
    return resultset


def docset_extraction(index, query):
    keywords = query.split(" ")
    docsets = []
    for keyword in keywords:
        docset = index.get(keyword, [])
        docsets.append(docset)
    return docsets


def disjunction_search(query: str, index: Dict[str, Set]) -> Set:
    docsets = docset_extraction(index, query)
    resultset = docsets[0].union(*docsets[1:])
    return resultset


def test_search():
    assert len(conjunction_search("a", {"a": {1, 2, 3}})) == 3
    assert len(conjunction_search("a b", {"a": {1, 2, 3}, "b": {2, 3}})) == 2
    assert len(disjunction_search("a b", {"a": {1, 2, 3}, "b": {4, 5}})) == 5
