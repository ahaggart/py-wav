from __future__ import annotations

from typing import List, Dict, Set, Generator, Iterable


class Vertex:
    def __init__(self, uuid: str, edges: Iterable[str]):
        self.uuid = uuid
        self.edges = list(edges)


class CyclicGraphException(Exception):
    pass


class SignalGraph:
    def __init__(self, vertices: Iterable[Vertex] = None):
        self.vertices: Dict[str, Vertex] = {}
        if vertices is not None:
            for v in vertices:
                self.vertices[v.uuid] = v

    def put_vertex(self, uuid: str, edges: Iterable[str]):
        self.vertices[uuid] = Vertex(uuid, edges)

    def traverse(self) -> Generator[str]:
        """Topological traversal of the signal DAG"""
        for v in self.sorted_topological():
            yield v

    def sorted_topological(self) -> List[str]:
        perm: Set[str] = set()
        temp: Set[str] = set()
        unmarked = set(self.vertices.values())
        result: List[str] = []

        def visit(v: Vertex):
            if v.uuid in perm:
                return
            if v.uuid in temp:
                raise CyclicGraphException("Not a DAG")
            temp.add(v.uuid)

            for edge in v.edges:
                visit(self.vertices[edge])

            temp.remove(v.uuid)
            perm.add(v.uuid)
            result.append(v.uuid)

        while len(unmarked) > 0:
            vertex = unmarked.pop()
            visit(vertex)

        return result
