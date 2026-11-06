"""Slow, obviously-correct reference implementations used as test oracles.

* :func:`literal_vertex_cover` follows the lecture pseudo-code word for word,
  with an explicit edge set and explicit deletions.
* :func:`literal_greedy_coloring` follows "assign the lowest legal color"
  with Python sets.
* The brute-force functions compute exact optima of tiny graphs.

None of them is efficient; they exist to check the real implementations.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

from itertools import combinations, permutations
from typing import Sequence

from graph_heuristics.graph import Graph


def literal_vertex_cover(graph: Graph) -> list[int]:
    """The lecture's VertexCover(G), literally: select an edge, add both ends, delete.

    "Select an arbitrary edge" takes the first remaining edge in input order.

    Args:
        graph: The input graph.

    Returns:
        The cover, in the order the vertices were added.

    Complexity: O(m * |M|) time, where M is the selected matching.
    """
    remaining = list(graph.edges())
    cover: list[int] = []
    while remaining:
        u, v = remaining[0]
        cover += [u, v]
        remaining = [(a, b) for a, b in remaining if a not in (u, v) and b not in (u, v)]
    return cover


def literal_greedy_coloring(graph: Graph, order: Sequence[int]) -> list[int]:
    """GreedyBasicGraphColoring, literally: each vertex gets the lowest legal color.

    Args:
        graph: The input graph.
        order: A permutation of 0..n-1.

    Returns:
        ``colors[v]`` for every vertex.
    """
    color: dict[int, int] = {}
    for v in order:
        used = {color[u] for u in graph.neighbors(v) if u in color}
        c = 0
        while c in used:
            c += 1
        color[v] = c
    return [color[v] for v in range(graph.n)]


def brute_force_min_cover_size(graph: Graph) -> int:
    """The size of a minimum vertex cover, by trying every subset (n <= 16).

    Args:
        graph: A small graph.

    Returns:
        OPT, the minimum number of vertices touching every edge.
    """
    edges = list(graph.edges())
    for k in range(graph.n + 1):
        for subset in combinations(range(graph.n), k):
            chosen = set(subset)
            if all(u in chosen or v in chosen for u, v in edges):
                return k
    return graph.n


def brute_force_chromatic_number(graph: Graph) -> int:
    """The chromatic number, by backtracking over k = 1, 2, ... colors (n <= 10).

    Args:
        graph: A small graph.

    Returns:
        chi, the fewest colors of a proper coloring (0 for no vertices).
    """
    n = graph.n
    if n == 0:
        return 0
    # Vertices are colored in order 0..n-1, so only earlier neighbors matter.
    earlier = [[u for u in graph.neighbors(v) if u < v] for v in range(n)]

    def colorable(k: int) -> bool:
        color = [-1] * n
        stack = [(0, 0)]  # (vertex, next color to try)
        while stack:
            v, c = stack.pop()
            if v == n:
                return True
            while c < k and any(color[u] == c for u in earlier[v]):
                c += 1
            if c < k:
                color[v] = c
                stack.append((v, c + 1))  # resume here on backtrack
                stack.append((v + 1, 0))
        return False

    return next(k for k in range(1, n + 1) if colorable(k))


def brute_force_degeneracy(graph: Graph) -> int:
    """The degeneracy: repeatedly delete a vertex of minimum degree (O(n^2)).

    Args:
        graph: The graph.

    Returns:
        The largest minimum degree seen during the deletions.
    """
    alive = set(range(graph.n))
    neighbors = [set(graph.neighbors(v)) for v in range(graph.n)]
    best = 0
    while alive:
        v = min(alive, key=lambda x: len(neighbors[x] & alive))
        best = max(best, len(neighbors[v] & alive))
        alive.remove(v)
    return best


def min_max_back_degree(graph: Graph) -> int:
    """The minimum, over all n! orders, of the largest back degree (n <= 7).

    Args:
        graph: A tiny graph.

    Returns:
        min over orders pi of max over v of #neighbors of v before v in pi.
    """
    edges = list(graph.edges())
    best = graph.n
    for order in permutations(range(graph.n)):
        position = {v: i for i, v in enumerate(order)}
        back = [0] * graph.n
        for u, v in edges:
            back[v if position[u] < position[v] else u] += 1
        best = min(best, max(back, default=0))
    return best if graph.n else 0
