"""Tests for the graph generators and the brute-force oracles they rely on.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import pytest

from graph_heuristics.generators import (
    binomial_tree,
    complete_bipartite_graph,
    complete_graph,
    crown_graph,
    cycle_graph,
    path_graph,
    perfect_matching_graph,
    planted_graph,
    random_graph,
    random_tree,
    star_graph,
)
from reference import (
    brute_force_chromatic_number,
    brute_force_degeneracy,
    brute_force_min_cover_size,
    literal_vertex_cover,
    min_max_back_degree,
)


def test_random_graph_size_and_determinism() -> None:
    graph = random_graph(100, 1_000, seed=1)
    assert (graph.n, graph.m) == (100, 1_000)
    assert list(graph.edges()) == list(random_graph(100, 1_000, seed=1).edges())
    assert list(graph.edges()) != list(random_graph(100, 1_000, seed=2).edges())


def test_random_graph_rejects_too_many_edges() -> None:
    with pytest.raises(ValueError):
        random_graph(10, 23, seed=0)  # more than n(n-1)/4 = 22
    with pytest.raises(ValueError):
        random_graph(10, -1, seed=0)


def test_planted_graph_structure() -> None:
    groups, size = 7, 5
    graph, hidden = planted_graph(groups, size, density=0.5, seed=3)
    assert graph.n == groups * size
    for u, v in graph.edges():
        assert u // size != v // size, "an edge inside a group"
    assert [v // size for v in hidden] == list(range(groups))
    edges = {frozenset(e) for e in graph.edges()}
    for i, u in enumerate(hidden):
        for v in hidden[i + 1:]:
            assert frozenset((u, v)) in edges, "the hidden vertices must form a clique"


def test_planted_graph_optima_by_brute_force() -> None:
    graph, _ = planted_graph(groups=3, size=3, density=0.5, seed=4)
    assert brute_force_chromatic_number(graph) == 3
    assert brute_force_min_cover_size(graph.complement()) == 3 * (3 - 1)


def test_small_families() -> None:
    assert (path_graph(5).n, path_graph(5).m) == (5, 4)
    assert path_graph(1).m == 0
    assert (cycle_graph(6).n, cycle_graph(6).m) == (6, 6)
    with pytest.raises(ValueError):
        cycle_graph(2)
    assert (star_graph(4).n, star_graph(4).m, star_graph(4).degree(0)) == (5, 4, 4)
    assert complete_graph(5).m == 10
    assert (complete_bipartite_graph(2, 3).n, complete_bipartite_graph(2, 3).m) == (5, 6)
    assert (perfect_matching_graph(4).n, perfect_matching_graph(4).m) == (8, 4)


def test_crown_graph() -> None:
    graph = crown_graph(4)
    assert (graph.n, graph.m) == (8, 12)
    assert all((u + v) % 2 == 1 for u, v in graph.edges())  # a_i even, b_j odd
    assert all(v != u + 1 for u, v in graph.edges())  # a_i and b_i not adjacent
    assert brute_force_chromatic_number(graph) == 2


def test_binomial_tree() -> None:
    for order in range(6):
        tree = binomial_tree(order)
        assert (tree.n, tree.m) == (2**order, 2**order - 1)
        assert tree.degree(tree.n - 1) == order  # the root has `order` children


def test_random_tree() -> None:
    tree = random_tree(50, seed=5)
    assert (tree.n, tree.m) == (50, 49)
    assert brute_force_degeneracy(tree) == 1


# --- the oracles themselves ----------------------------------------------------


def test_oracles_on_known_graphs() -> None:
    assert brute_force_min_cover_size(star_graph(5)) == 1
    assert brute_force_min_cover_size(complete_graph(5)) == 4
    assert brute_force_min_cover_size(perfect_matching_graph(3)) == 3
    assert brute_force_chromatic_number(cycle_graph(5)) == 3
    assert brute_force_chromatic_number(cycle_graph(6)) == 2
    assert brute_force_chromatic_number(complete_graph(5)) == 5
    assert brute_force_degeneracy(complete_graph(5)) == 4
    assert brute_force_degeneracy(cycle_graph(5)) == 2
    assert min_max_back_degree(cycle_graph(5)) == 2
    assert min_max_back_degree(star_graph(4)) == 1
    assert literal_vertex_cover(path_graph(4)) == [0, 1, 2, 3]
