"""Hand-worked test cases: expected results computed on paper by the author.

Written by Ahmed Elgazwy (see docs/author_tasks.md, task 3). Each test builds
a small graph, and asserts the results of the four algorithms worked out by
hand.
"""

from __future__ import annotations

from graph_heuristics.coloring import (
    color_count,
    greedy_coloring,
    natural_order,
    smallest_last_coloring,
)
from graph_heuristics.graph import Graph
from graph_heuristics.vertex_cover import (
    basic_vertex_cover,
    is_vertex_cover,
    randomized_vertex_cover,
)
import pytest
# ---- Written by Ahmed Elgazwy: begin ----




def is_valid_vertex_cover(graph, cover):
    """Check that every edge has at least one endpoint in the cover."""
    cover = set(cover)
    return all(
        u in cover or v in cover
        for u, v in graph.edges()
    )


def is_valid_coloring(graph, colors):
    """Check that adjacent vertices have different colors."""
    if len(colors) != graph.n:
        return False

    if any(c < 0 for c in colors):
        return False

    return all(
        colors[u] != colors[v]
        for u, v in graph.edges()
    )


def test_triangle():
    # Triangle: K3
    graph = Graph(
    3,
    [0, 1, 0],
    [1, 2, 2]
    )   
    order = [0,1,2]

    # Minimum vertex cover size = 2
    assert basic_vertex_cover(graph) == [0, 1]

    cover = randomized_vertex_cover(graph, seed=42)
    assert is_valid_vertex_cover(graph, cover)
    assert len(cover) <= 2 * 2

    # Natural-order greedy coloring
    assert greedy_coloring(graph,order) == [0, 1, 2]

    # Smallest-last coloring requires 3 colors
    colors = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, colors)
    assert len(set(colors)) == 3


def test_path_p4():
    # Path P4, with edges deliberately given in a different order
  
    graph = Graph(
    4,
    [1, 2, 0],
    [2, 3, 1]
    )   
    order = [0,1,2,3]
    # Greedy vertex cover:
    # (1,2) -> add 1,2
    # (2,3) -> already covered
    # (0,1) -> already covered
    assert basic_vertex_cover(graph) == [1, 2]

    # Minimum vertex cover size = 2
    cover = randomized_vertex_cover(graph, seed=42)
    assert is_valid_vertex_cover(graph, cover)
    assert len(cover) <= 2 * 2

    # Natural-order coloring
    assert greedy_coloring(graph,order) == [0, 1, 0, 1]

    # Smallest-last coloring needs 2 colors
    colors = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, colors)
    assert len(set(colors)) == 2


def test_star_k14():
    # Star K1,4: vertex 0 is the center

    graph = Graph(
    5,
    [1, 2, 3,4],
    [0, 0, 0,0]
    )   
    order = [0,1,2,3,4]
    # Every edge is initially uncovered only for the first edge.
    assert basic_vertex_cover(graph) == [1, 0]

    # Minimum vertex cover size = 1 (the center)
    cover = randomized_vertex_cover(graph, seed=42)
    assert is_valid_vertex_cover(graph, cover)
    assert len(cover) <= 4 * 1

    # Natural-order coloring
    assert greedy_coloring(graph,order) == [0, 1, 1, 1, 1]

    # Smallest-last coloring needs 2 colors
    colors = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, colors)
    assert len(set(colors)) == 2


def test_complete_bipartite_k33():
    # K3,3: partitions {0,1,2} and {3,4,5}

    graph = Graph(
    6,
    [0, 0, 0,1,1,1,2,2,2],
    [3, 4, 5,3,4,5,3,4,5]
    )   
    order = [0,1,2,3,4,5]
    # Greedy vertex cover follows edge input order.
    assert basic_vertex_cover(graph) == [0, 3, 1, 4, 2, 5]

    # Minimum vertex cover size = 3
    cover = randomized_vertex_cover(graph, seed=42)
    assert is_valid_vertex_cover(graph, cover)
    assert len(cover) <= 2 * 3

    # Natural-order coloring
    assert greedy_coloring(graph,order) == [0, 0, 0, 1, 1, 1]

    # Smallest-last coloring needs 2 colors
    colors = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, colors)
    assert len(set(colors)) == 2


def test_cycle_c5():
    # Cycle C5

    graph = Graph(
    5,
    [0, 1, 2,3,4],
    [1, 2, 3,4,0]
    )   
    order = [0,1,2,3,4]
    # Greedy vertex cover:
    # (0,1) -> add 0,1
    # (1,2) -> already covered
    # (2,3) -> add 2,3
    # (3,4) -> already covered
    # (4,0) -> add 4
    assert basic_vertex_cover(graph) == [0, 1, 2, 3]

    # Minimum vertex cover size = 3
    cover = randomized_vertex_cover(graph, seed=42)
    assert is_valid_vertex_cover(graph, cover)
    assert len(cover) <= 2 * 3

    # Natural-order coloring
    assert greedy_coloring(graph,order) == [0, 1, 0, 1, 2]

    # Smallest-last coloring needs 3 colors
    colors = smallest_last_coloring(graph)
    assert is_valid_coloring(graph, colors)
    assert len(set(colors)) == 3

# ---- Written by Ahmed Elgazwy: end ----
