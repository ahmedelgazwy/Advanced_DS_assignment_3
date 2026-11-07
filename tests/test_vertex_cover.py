"""Tests for the basic and randomized vertex cover algorithms.

The basic algorithm is checked against the lecture pseudo-code run literally
(``reference.literal_vertex_cover``) and against brute-force optima; the
randomized one for validity, reproducibility, a fair coin and its expected
2-approximation.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import random

import pytest

from graph_heuristics.generators import (
    complete_bipartite_graph,
    complete_graph,
    path_graph,
    perfect_matching_graph,
    planted_graph,
    random_graph,
    star_graph,
)
from graph_heuristics.graph import Graph
from graph_heuristics.vertex_cover import (
    VERTEX_COVER_ALGORITHMS,
    basic_vertex_cover,
    is_vertex_cover,
    randomized_vertex_cover,
)
from reference import brute_force_min_cover_size, literal_vertex_cover


def small_random_graphs(count: int, max_n: int, seed: int) -> list[Graph]:
    """Random graphs with 1..max_n vertices and random densities."""
    rng = random.Random(seed)
    graphs = []
    for _ in range(count):
        n = rng.randint(1, max_n)
        m = rng.randint(0, n * (n - 1) // 4)
        graphs.append(random_graph(n, m, seed=rng.randrange(10**9)))
    return graphs


# --- both algorithms ---------------------------------------------------------


@pytest.mark.parametrize("name", list(VERTEX_COVER_ALGORITHMS))
def test_cover_is_valid_on_random_graphs(name: str) -> None:
    algorithm = VERTEX_COVER_ALGORITHMS[name]
    for i, graph in enumerate(small_random_graphs(150, 40, seed=1)):
        cover = algorithm(graph, i)
        assert is_vertex_cover(graph, cover), graph
        assert len(set(cover)) == len(cover), "a vertex was added twice"


@pytest.mark.parametrize("name", list(VERTEX_COVER_ALGORITHMS))
def test_graphs_without_edges_need_no_vertices(name: str) -> None:
    algorithm = VERTEX_COVER_ALGORITHMS[name]
    assert algorithm(Graph.from_edges(0, []), 0) == []
    assert algorithm(Graph.from_edges(5, []), 0) == []


@pytest.mark.parametrize("name", list(VERTEX_COVER_ALGORITHMS))
def test_within_twice_the_optimum_on_small_graphs(name: str) -> None:
    algorithm = VERTEX_COVER_ALGORITHMS[name]
    for i, graph in enumerate(small_random_graphs(120, 11, seed=2)):
        opt = brute_force_min_cover_size(graph)
        cover = algorithm(graph, i)
        assert opt <= len(cover)
        if name == "basic":  # the randomized bound holds only in expectation
            assert len(cover) <= 2 * opt


@pytest.mark.parametrize("name", list(VERTEX_COVER_ALGORITHMS))
def test_large_graph(name: str) -> None:
    graph = random_graph(20_000, 100_000, seed=3)
    cover = VERTEX_COVER_ALGORITHMS[name](graph, 3)
    assert is_vertex_cover(graph, cover)


@pytest.mark.parametrize("name", list(VERTEX_COVER_ALGORITHMS))
def test_planted_complement_needs_n_minus_groups(name: str) -> None:
    graph, _ = planted_graph(groups=6, size=4, density=0.7, seed=4)
    complement = graph.complement()
    opt = 6 * (4 - 1)  # the groups are cliques of 4: all but one vertex of each
    cover = VERTEX_COVER_ALGORITHMS[name](complement, 4)
    assert is_vertex_cover(complement, cover)
    assert opt <= len(cover) <= complement.n


# --- basic algorithm ---------------------------------------------------------


def test_basic_single_edge_takes_both_endpoints() -> None:
    assert basic_vertex_cover(Graph.from_edges(2, [(0, 1)])) == [0, 1]
    assert basic_vertex_cover(Graph.from_edges(2, [(1, 0)])) == [1, 0]


def test_basic_matches_the_lecture_pseudo_code() -> None:
    for graph in small_random_graphs(150, 30, seed=5):
        assert basic_vertex_cover(graph) == literal_vertex_cover(graph)


def test_basic_cover_is_the_endpoints_of_a_maximal_matching() -> None:
    for graph in small_random_graphs(100, 30, seed=6):
        cover = basic_vertex_cover(graph)
        assert len(cover) % 2 == 0
        edges = {frozenset(e) for e in graph.edges()}
        matching = [(cover[i], cover[i + 1]) for i in range(0, len(cover), 2)]
        assert all(frozenset(e) in edges for e in matching)  # pairs are edges
        matched = set(cover)
        assert len(matched) == len(cover)  # the edges are disjoint
        assert all(u in matched or v in matched for u, v in graph.edges())  # maximal


def test_basic_follows_the_edge_order() -> None:
    # Path 0-1-2-3: the first edge (0, 1) is taken, (1, 2) is then covered,
    # and (2, 3) is taken: cover [0, 1, 2, 3].
    assert basic_vertex_cover(path_graph(4)) == [0, 1, 2, 3]
    # The same path listed middle edge first: (1, 2) covers everything.
    middle_first = Graph.from_edges(4, [(1, 2), (0, 1), (2, 3)])
    assert basic_vertex_cover(middle_first) == [1, 2]


def test_basic_is_exactly_twice_the_optimum_on_a_perfect_matching() -> None:
    graph = perfect_matching_graph(50)
    assert len(basic_vertex_cover(graph)) == 100  # OPT = 50


def test_basic_on_complete_bipartite_takes_every_vertex() -> None:
    graph = complete_bipartite_graph(5, 5)
    assert len(basic_vertex_cover(graph)) == 10  # OPT = 5


def test_basic_on_complete_graph() -> None:
    assert len(basic_vertex_cover(complete_graph(7))) == 6  # OPT = 6
    assert len(basic_vertex_cover(complete_graph(8))) == 8  # OPT = 7


def test_basic_on_a_star_takes_two_vertices() -> None:
    assert sorted(basic_vertex_cover(star_graph(10))) == [0, 1]  # OPT = 1


# --- randomized algorithm ----------------------------------------------------


def test_randomized_single_edge_takes_one_endpoint() -> None:
    assert randomized_vertex_cover(Graph.from_edges(2, [(0, 1)]), seed=0) in ([0], [1])


def test_randomized_is_optimal_on_a_perfect_matching() -> None:
    graph = perfect_matching_graph(50)
    for seed in range(5):
        assert len(randomized_vertex_cover(graph, seed)) == 50


def test_randomized_same_seed_same_cover() -> None:
    graph = random_graph(500, 2_000, seed=7)
    assert randomized_vertex_cover(graph, seed=42) == randomized_vertex_cover(graph, seed=42)


def test_randomized_different_seeds_differ() -> None:
    graph = random_graph(500, 2_000, seed=8)
    covers = {tuple(randomized_vertex_cover(graph, seed)) for seed in range(10)}
    assert len(covers) > 1


def test_randomized_coin_is_fair() -> None:
    graph = Graph.from_edges(2, [(0, 1)])
    trials = 4_000
    first = sum(randomized_vertex_cover(graph, seed) == [0] for seed in range(trials))
    sigma = (trials * 0.25) ** 0.5
    assert abs(first - trials / 2) < 5 * sigma


def test_randomized_mean_within_twice_the_optimum() -> None:
    for graph in small_random_graphs(40, 11, seed=9):
        opt = brute_force_min_cover_size(graph)
        sizes = [len(randomized_vertex_cover(graph, seed)) for seed in range(60)]
        assert sum(sizes) / len(sizes) <= 2 * opt + 1e-9


def test_randomized_only_scans_uncovered_edges() -> None:
    # Star with the center first: once the center is chosen nothing else is added.
    graph = star_graph(30)
    for seed in range(20):
        cover = randomized_vertex_cover(graph, seed)
        assert 0 not in cover[:-1]  # the center, if chosen, ends the cover
        assert is_vertex_cover(graph, cover)


# --- is_vertex_cover ---------------------------------------------------------


def test_is_vertex_cover_detects_an_uncovered_edge() -> None:
    graph = path_graph(4)
    assert is_vertex_cover(graph, [1, 2])
    assert not is_vertex_cover(graph, [1])
    assert is_vertex_cover(Graph.from_edges(3, []), [])


def test_is_vertex_cover_rejects_unknown_vertices() -> None:
    with pytest.raises(ValueError):
        is_vertex_cover(path_graph(3), [5])
