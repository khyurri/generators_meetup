from typing import Set, Dict


# simple keyword based search, naive intersection
def conjunction_search(query: str, index: Dict[str, Set]) -> Set:
    docsets = __docset_extraction(index, query)
    resultset = docsets[0].intersection(*docsets[1:])
    return resultset


# simple keyword based search, naive union
def disjunction_search(query: str, index: Dict[str, Set]) -> Set:
    docsets = __docset_extraction(index, query)
    resultset = docsets[0].union(*docsets[1:])
    return resultset


# todo add top k retrieval
# add wand or something similar
def wand_search(query: str, index: Dict[str, Set], top_k: int = 5) -> Set:
    pass


def __docset_extraction(index, query):
    keywords = query.split(" ")
    return [index.get(k, set()) for k in keywords]


def test_search():
    assert len(conjunction_search("a", {"a": {1, 2, 3}})) == 3
    assert len(conjunction_search("a b", {"a": {1, 2, 3}, "b": {2, 3}})) == 2
    assert len(disjunction_search("a b", {"a": {1, 2, 3}, "b": {4, 5}})) == 5
