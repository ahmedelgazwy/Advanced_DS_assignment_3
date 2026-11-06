"""Tests for the Graph class: construction, validation, CSR views and complement.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import pytest

from graph_heuristics.generators import complete_graph, path_graph, random_graph
from graph_heuristics.graph import Graph


def test_counts_degrees_and_neighbors() -> None:
    graph = Graph.from_edges(4, [(0, 1), (0, 2), (2, 3)])
    assert (graph.n, graph.m) == (4, 3)
    assert [graph.degree(v) for v in range(4)] == [2, 1, 2, 1]
    assert list(graph.neighbors(0)) == [1, 2]
    assert list(graph.neighbors(2)) == [0, 3]
    assert graph.max_degree() == 2
    assert repr(graph) == "Graph(n=4, m=3)"


def test_edges_keep_input_order_and_orientation() -> None:
    edges = [(3, 1), (0, 2), (1, 0)]
    assert list(Graph.from_edges(4, edges).edges()) == edges


def test_neighbors_follow_edge_order() -> None:
    graph = Graph.from_edges(4, [(0, 3), (1, 0), (0, 2)])
    assert list(graph.neighbors(0)) == [3, 1, 2]


def test_neighbors_is_read_only() -> None:
    graph = path_graph(3)
    with pytest.raises(TypeError):
        graph.neighbors(1)[0] = 2  # type: ignore[index]


def test_repeated_edges_are_kept_once_at_first_position() -> None:
    graph = Graph.from_edges(3, [(0, 1), (1, 2), (1, 0), (0, 1), (2, 1), (0, 2)])
    assert list(graph.edges()) == [(0, 1), (1, 2), (0, 2)]
    assert [graph.degree(v) for v in range(3)] == [2, 2, 2]


def test_invalid_input_is_rejected() -> None:
    with pytest.raises(ValueError):
        Graph.from_edges(-1, [])
    with pytest.raises(ValueError):
        Graph.from_edges(3, [(0, 3)])
    with pytest.raises(ValueError):
        Graph.from_edges(3, [(-1, 0)])
    with pytest.raises(ValueError):
        Graph.from_edges(3, [(1, 1)])


def test_empty_graphs() -> None:
    for n in (0, 1, 5):
        graph = Graph.from_edges(n, [])
        assert (graph.n, graph.m, graph.max_degree()) == (n, 0, 0)
        assert list(graph.edges()) == []


def test_csr_matches_edge_list() -> None:
    graph = random_graph(300, 2_000, seed=1)
    adjacency = {v: set() for v in range(graph.n)}
    for u, v in graph.edges():
        adjacency[u].add(v)
        adjacency[v].add(u)
    for v in range(graph.n):
        assert sorted(graph.neighbors(v)) == sorted(adjacency[v])
        assert graph.degree(v) == len(adjacency[v])
    assert graph.offsets[graph.n] == 2 * graph.m


def test_complement() -> None:
    graph = random_graph(60, 400, seed=2)
    complement = graph.complement()
    assert complement.m == 60 * 59 // 2 - 400
    edges = {frozenset(e) for e in graph.edges()}
    for u, v in complement.edges():
        assert u < v and frozenset((u, v)) not in edges
    back = {frozenset(e) for e in complement.complement().edges()}
    assert back == edges


def test_complement_of_complete_graph_is_empty() -> None:
    assert complete_graph(6).complement().m == 0
    assert Graph.from_edges(5, []).complement().m == 10
