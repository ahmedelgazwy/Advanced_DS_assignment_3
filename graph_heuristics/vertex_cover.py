"""Vertex cover heuristics: the basic 2-approximation and its randomized version.

A vertex cover is a set C of vertices that touches every edge. Finding a
smallest one is NP-hard [Karp 1972]. Both algorithms below follow the lecture
loop "while an edge (u, v) remains: add vertices of it to C, then delete the
edges incident to them":

* **basic**: add both u and v. The selected edges form a maximal matching M,
  and any cover needs a distinct vertex for each edge of M, so
  |C| = 2|M| <= 2 OPT. The bound is tight (e.g. on a perfect matching).
* **randomized** [Pitt 1985]: add one of u and v, chosen with probability 1/2.
  Each choice lands in a fixed optimal cover with probability >= 1/2, so
  E|C| <= 2 OPT.

Both scan the edge list once, in input order. An edge has been "deleted" by
the lecture loop exactly when one given the assignment 2 pdf create a detailed plan for me to review for solving this assignment. create a git repo that you will use for commiting each part and make the plan comprehensiveof its endpoints is already in C, so the
next uncovered edge of the scan is the next edge the loop would select. Both
run in O(n + m) time with O(n) extra space: a bytearray of membership flags.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship"). Exception: the body of
``basic_vertex_cover`` was written by Ahmed Elgazwy (marked below).
"""

from __future__ import annotations

import random
from typing import Callable, Iterable, Optional

from graph_heuristics.graph import Graph


def basic_vertex_cover(graph: Graph) -> list[int]:
    """Basic vertex cover: take both endpoints of every edge that is still uncovered.

    Scans the edges once, in input order (``graph.edges()``). When an edge
    (u, v) has neither endpoint in the cover yet, both u and v are added.

    Args:
        graph: The input graph.

    Returns:
        The cover: a list of distinct vertices in the order they were added.
        For each selected edge (u, v), u is added before v.

    Complexity: O(n + m) time, O(n) extra space.
    """
    # ---- Written by Ahmed Elgazwy: begin ----
    res = []
    selected = set()

    for u, v in graph.edges():
        if u not in selected and v not in selected:
            res.append(u)
            res.append(v)

            selected.add(u)
            selected.add(v)

    return res
    # ---- Written by Ahmed Elgazwy: end ----


def randomized_vertex_cover(graph: Graph, seed: Optional[int] = None) -> list[int]:
    """Randomized vertex cover [Pitt 1985]: take one random endpoint of each uncovered edge.

    Scans the edges in the same order as :func:`basic_vertex_cover`, so the
    random choice of endpoint is the only difference between the two.

    Args:
        graph: The input graph.
        seed: Seed of the private random number generator; the same seed
            gives the same cover. None seeds from the operating system.

    Returns:
        The cover: a list of distinct vertices in the order they were added.

    Complexity: O(n + m) time (one random bit per selected edge), O(n) extra
    space.
    """
    coin = random.Random(seed).getrandbits
    in_cover = bytearray(graph.n)
    cover: list[int] = []
    for u, v in zip(graph.edge_u, graph.edge_v):
        if in_cover[u] or in_cover[v]:
            continue  # already covered: the lecture loop deleted this edge
        chosen = v if coin(1) else u
        in_cover[chosen] = 1
        cover.append(chosen)
    return cover


def is_vertex_cover(graph: Graph, cover: Iterable[int]) -> bool:
    """Check that a set of vertices touches every edge.

    Args:
        graph: The graph.
        cover: Vertices of the candidate cover (repeats are allowed).

    Returns:
        True if every edge has at least one endpoint in ``cover``.

    Raises:
        ValueError: If a vertex is outside 0..n-1.

    Complexity: O(n + m) time, O(n) extra space.
    """
    in_cover = bytearray(graph.n)
    for v in cover:
        if not 0 <= v < graph.n:
            raise ValueError(f"vertex {v} is outside 0..{graph.n - 1}")
        in_cover[v] = 1
    return all(in_cover[u] or in_cover[v] for u, v in zip(graph.edge_u, graph.edge_v))


#: Every vertex cover algorithm, keyed by display name. Each one is called as
#: ``algorithm(graph, seed)``; the basic algorithm ignores the seed.
VERTEX_COVER_ALGORITHMS: dict[str, Callable[[Graph, Optional[int]], list[int]]] = {
    "basic": lambda graph, seed=None: basic_vertex_cover(graph),
    "randomized": randomized_vertex_cover,
}
