"""Tests for greedy coloring and the natural and smallest-last orders.

``greedy_coloring`` is checked against the literal "lowest legal color" loop
(``reference.literal_greedy_coloring``). The smallest-last order is checked
against its definition (each vertex has minimum degree when removed), against
the brute-force degeneracy, and against the minimum largest back degree over
all n! orders.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import random

import pytest

from graph_heuristics.coloring import (
    COLORING_ALGORITHMS,
    color_count,
    greedy_coloring,
    is_proper_coloring,
    max_back_degree,
    natural_order,
    smallest_last_order,
)
from graph_heuristics.generators import (
    binomial_tree,
    complete_bipartite_graph,
    complete_graph,
    crown_graph,
    cycle_graph,
    path_graph,
    planted_graph,
    random_graph,
    random_tree,
    star_graph,
)
from graph_heuristics.graph import Graph
from reference import (
    brute_force_chromatic_number,
    brute_force_degeneracy,
    literal_greedy_coloring,
    min_max_back_degree,
)


def small_random_graphs(count: int, max_n: int, seed: int) -> list[Graph]:
    """Random graphs with 1..max_n vertices and random densities."""
    rng = random.Random(seed)
    graphs = []
    for _ in range(count):
        n = rng.randint(1, max_n)
        m = rng.randint(0, n * (n - 1) // 4)
        graphs.append(random_graph(n, m, seed=rng.randrange(10**9)))
    return graphs


# --- greedy_coloring ---------------------------------------------------------


def test_greedy_matches_the_lowest_legal_color_rule() -> None:
    rng = random.Random(1)
    for graph in small_random_graphs(150, 30, seed=1):
        order = list(range(graph.n))
        rng.shuffle(order)
        assert greedy_coloring(graph, order) == literal_greedy_coloring(graph, order)


def test_greedy_first_vertex_gets_color_zero() -> None:
    graph = complete_graph(4)
    for first in range(4):
        order = [first] + [v for v in range(4) if v != first]
        assert greedy_coloring(graph, order)[first] == 0


def test_greedy_rejects_an_order_that_is_not_a_permutation() -> None:
    graph = path_graph(3)
    for bad in ([0, 1], [0, 1, 1], [0, 1, 3], [0, 1, 2, 0]):
        with pytest.raises(ValueError):
            greedy_coloring(graph, bad)


def test_greedy_on_a_graph_without_vertices() -> None:
    assert greedy_coloring(Graph.from_edges(0, []), []) == []


# --- both coloring algorithms --------------------------------------------------


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_is_proper_with_contiguous_colors(name: str) -> None:
    for graph in small_random_graphs(150, 40, seed=2):
        colors = COLORING_ALGORITHMS[name](graph)
        assert is_proper_coloring(graph, colors)
        assert set(colors) == set(range(color_count(colors)))


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_uses_at_most_max_degree_plus_one(name: str) -> None:
    for graph in small_random_graphs(100, 40, seed=3):
        assert color_count(COLORING_ALGORITHMS[name](graph)) <= graph.max_degree() + 1


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_is_never_below_the_chromatic_number(name: str) -> None:
    for graph in small_random_graphs(60, 9, seed=4):
        chi = brute_force_chromatic_number(graph)
        assert color_count(COLORING_ALGORITHMS[name](graph)) >= chi


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_known_graphs(name: str) -> None:
    algorithm = COLORING_ALGORITHMS[name]
    assert algorithm(Graph.from_edges(5, [])) == [0] * 5
    assert color_count(algorithm(complete_graph(6))) == 6
    assert color_count(algorithm(cycle_graph(8))) == 2
    assert color_count(algorithm(cycle_graph(7))) == 3
    assert color_count(algorithm(path_graph(10))) == 2
    assert color_count(algorithm(star_graph(9))) == 2
    assert color_count(algorithm(complete_bipartite_graph(4, 6))) == 2


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_planted_graph_needs_at_least_the_groups(name: str) -> None:
    graph, _ = planted_graph(groups=8, size=5, density=0.6, seed=5)
    colors = COLORING_ALGORITHMS[name](graph)
    assert is_proper_coloring(graph, colors)
    assert 8 <= color_count(colors) <= graph.max_degree() + 1


@pytest.mark.parametrize("name", list(COLORING_ALGORITHMS))
def test_coloring_large_graph(name: str) -> None:
    graph = random_graph(20_000, 100_000, seed=6)
    assert is_proper_coloring(graph, COLORING_ALGORITHMS[name](graph))


# --- natural order -------------------------------------------------------------


def test_natural_order_is_the_vertex_numbering() -> None:
    assert natural_order(path_graph(5)) == [0, 1, 2, 3, 4]


def test_natural_on_crown_graph_uses_k_colors() -> None:
    for k in (2, 5, 10):
        assert color_count(COLORING_ALGORITHMS["natural"](crown_graph(k))) == k


def test_natural_on_binomial_tree_uses_order_plus_one_colors() -> None:
    for order in range(7):
        colors = COLORING_ALGORITHMS["natural"](binomial_tree(order))
        assert color_count(colors) == order + 1


# --- smallest-last order ---------------------------------------------------------


def test_smallest_last_order_is_a_permutation() -> None:
    for graph in small_random_graphs(100, 40, seed=7):
        order, _ = smallest_last_order(graph)
        assert sorted(order) == list(range(graph.n))


def test_smallest_last_removes_a_minimum_degree_vertex_each_time() -> None:
    # The definition [csc09, Table 1]: read from the end, each vertex has the
    # smallest degree among the vertices not yet removed.
    for graph in small_random_graphs(100, 30, seed=8):
        order, _ = smallest_last_order(graph)
        alive = set(range(graph.n))
        neighbors = [set(graph.neighbors(v)) for v in range(graph.n)]
        for v in reversed(order):
            degree = len(neighbors[v] & alive)
            assert degree == min(len(neighbors[u] & alive) for u in alive)
            alive.remove(v)


def test_smallest_last_degeneracy_matches_brute_force() -> None:
    for graph in small_random_graphs(150, 40, seed=9):
        order, degeneracy = smallest_last_order(graph)
        assert degeneracy == brute_force_degeneracy(graph)
        assert max_back_degree(graph, order) == degeneracy


def test_smallest_last_minimizes_the_largest_back_degree() -> None:
    for graph in small_random_graphs(40, 7, seed=10):
        order, _ = smallest_last_order(graph)
        assert max_back_degree(graph, order) == min_max_back_degree(graph)


def test_smallest_last_coloring_uses_at_most_degeneracy_plus_one() -> None:
    for graph in small_random_graphs(150, 40, seed=11):
        _, degeneracy = smallest_last_order(graph)
        colors = COLORING_ALGORITHMS["smallest_last"](graph)
        assert color_count(colors) <= degeneracy + 1


def test_smallest_last_degeneracy_of_known_graphs() -> None:
    assert smallest_last_order(Graph.from_edges(0, [])) == ([], 0)
    assert smallest_last_order(Graph.from_edges(4, []))[1] == 0
    assert smallest_last_order(path_graph(10))[1] == 1
    assert smallest_last_order(cycle_graph(9))[1] == 2
    assert smallest_last_order(complete_graph(7))[1] == 6
    assert smallest_last_order(complete_bipartite_graph(3, 8))[1] == 3


def test_smallest_last_colors_every_tree_with_two_colors() -> None:
    for seed in range(20):
        tree = random_tree(200, seed)
        assert color_count(COLORING_ALGORITHMS["smallest_last"](tree)) == 2
    for order in range(1, 9):  # natural order needs order + 1 colors here
        tree = binomial_tree(order)
        assert color_count(COLORING_ALGORITHMS["smallest_last"](tree)) == 2


def test_smallest_last_on_large_graph() -> None:
    graph = random_graph(50_000, 250_000, seed=12)
    order, degeneracy = smallest_last_order(graph)
    assert sorted(order) == list(range(graph.n))
    assert max_back_degree(graph, order) == degeneracy


# --- helpers ---------------------------------------------------------------------


def test_is_proper_coloring_detects_conflicts() -> None:
    graph = path_graph(3)
    assert is_proper_coloring(graph, [0, 1, 0])
    assert not is_proper_coloring(graph, [0, 0, 1])
    assert not is_proper_coloring(graph, [0, 1])  # wrong length
    assert not is_proper_coloring(graph, [0, -1, 0])  # negative color


def test_max_back_degree() -> None:
    graph = star_graph(4)  # center 0
    assert max_back_degree(graph, [0, 1, 2, 3, 4]) == 1
    assert max_back_degree(graph, [1, 2, 3, 4, 0]) == 4
    with pytest.raises(ValueError):
        max_back_degree(graph, [0, 1])


def test_color_count() -> None:
    assert color_count([]) == 0
    assert color_count([0, 1, 0, 2]) == 3
