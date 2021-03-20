from typing import List
from unittest import TestCase

from SignalGraph import SignalGraph, Vertex, CyclicGraphException


class TestSignalGraph(TestCase):
    def setUp(self) -> None:
        pass

    def assertOrder(self, order: List[str], a: str, b: str):
        a_pos = order.index(a)
        b_pos = order.index(b)
        self.assertTrue(
            a_pos < b_pos,
            msg=f"Position of {a} is not less than that of {b} : {order}"
        )

    def test_traverse_fork(self):
        graph = SignalGraph([
            Vertex("a", ["b", "c"]),
            Vertex("b", ["d"]),
            Vertex("c", ["d"]),
            Vertex("d", []),
        ])

        order = graph.sorted_topological()
        self.assertOrder(order, "a", "b")
        self.assertOrder(order, "a", "c")
        self.assertOrder(order, "b", "d")
        self.assertOrder(order, "c", "d")

    def test_traverse_linear(self):
        graph = SignalGraph([
            Vertex("a", ["b"]),
            Vertex("b", ["c"]),
            Vertex("c", ["d"]),
            Vertex("d", []),
        ])

        order = graph.sorted_topological()
        self.assertOrder(order, "a", "b")
        self.assertOrder(order, "b", "c")
        self.assertOrder(order, "c", "d")

    def test_traverse_cyclic(self):
        graph = SignalGraph([
            Vertex("a", ["b"]),
            Vertex("b", ["c"]),
            Vertex("c", ["d"]),
            Vertex("d", ["a"]),
        ])

        self.assertRaises(CyclicGraphException, graph.sorted_topological)
