"""Greedy graph coloring along the natural order and along the smallest-last order.

Greedy coloring visits the vertices in a given order and gives each one the
smallest color (0, 1, 2, ...) not used by its already-colored neighbors. With
an order pi it uses at most B_pi + 1 colors, where the *back degree* of a
vertex is its number of neighbors placed before it in pi and B_pi is the
largest back degree [Gebremedhin et al. 2009]. Since B_pi <= Delta, every
order gives at most Delta + 1 colors.

* **natural order**: vertices 0, 1, ..., n-1, as numbered in the input.
* **smallest-last order** [Matula & Beck 1983]: built from the end. The
  vertex placed last has the smallest degree; it is removed, and the vertex
  placed second-to-last has the smallest degree in what remains, and so on.
  This order has the smallest B_pi over all n! orders. That minimum is the
  *degeneracy* d of the graph, so greedy coloring along it uses at most
  d + 1 colors (2 for any tree, at most 6 for any planar graph).

The order is computed in O(n + m) time with a bucket queue: the vertices sit
in one array sorted by current degree, and removing a vertex moves each of its
remaining neighbors one bucket down by a swap [Batagelj & Zaversnik 2003].
Greedy coloring is O(n + m) for any order, so both algorithms are linear.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship"). Exception: the body of
``greedy_coloring`` was written by Ahmed Elgazwy (marked below).
"""

from __future__ import annotations

from typing import Callable, Sequence

from graph_heuristics.graph import Graph


def greedy_coloring(graph: Graph, order: Sequence[int]) -> list[int]:
    """Greedy coloring: give each vertex, in order, the lowest color its neighbors do not use.

    Colors are the integers 0, 1, 2, ... When vertex v is colored, only its
    neighbors that come before it in ``order`` have colors; v gets the
    smallest color none of them uses.

    Args:
        graph: The input graph.
        order: Every vertex 0..n-1 exactly once: the order in which to color.

    Returns:
        ``colors``, a list of length n: ``colors[v]`` is the color of vertex v.
        The colors used are exactly 0..k-1 for some k.

    Raises:
        ValueError: If ``order`` is not a permutation of 0..n-1.

    Complexity: O(n + m) time, O(n) extra space.
    """
    _check_permutation(order, graph.n)
    # ---- Written by Ahmed Elgazwy: begin ----


    n = graph.n

    colors = [-1] * n
    forbidden = [-1] * (n + 1)

    for v in order:

        # Mark colors used by already-colored neighbors
        for u in graph.neighbors(v):
            c = colors[u]

            if c != -1:
                forbidden[c] = v

        # Find the first available color
        c = 0
        while forbidden[c] == v:
            c += 1

        # Assign the color
        colors[v] = c

    return colors
    # ---- Written by Ahmed Elgazwy: end ----


def natural_order(graph: Graph) -> list[int]:
    """The natural vertex order 0, 1, ..., n-1 (the numbering of the input).

    Args:
        graph: The input graph.

    Returns:
        ``list(range(n))``.
    """
    return list(range(graph.n))


def smallest_last_order(graph: Graph) -> tuple[list[int], int]:
    """Smallest-last vertex order [Matula & Beck 1983] and the degeneracy of the graph.

    Repeatedly removes a vertex of minimum degree in the remaining graph; the
    coloring order is the reverse of the removal order, so the vertex removed
    first is colored last. Ties are broken deterministically (by position in
    the bucket array, initially by vertex number).

    Implementation: ``vert`` holds the vertices not yet removed, sorted by
    current degree, at positions i+1..n-1; ``start[d]`` is the first position
    of the vertices of degree >= d. Removing vertex ``vert[i]`` lowers each
    remaining neighbor u by one bucket: swap u with the first vertex of its
    bucket, then advance that bucket's start. A bucket start left behind the
    removed prefix is clamped to i + 1 when read.

    Args:
        graph: The input graph.

    Returns:
        ``(order, degeneracy)``: the coloring order (a permutation of 0..n-1)
        and the degeneracy d, the largest degree a vertex has when removed.
        Every vertex has at most d neighbors before it in ``order``.

    Complexity: O(n + m) time; O(n) extra space (deg, pos and vert of n
    entries each, start of Delta + 1 <= n entries).
    """
    n = graph.n
    offsets, adjacency = graph.offsets, graph.adjacency
    deg = [offsets[v + 1] - offsets[v] for v in range(n)]
    max_deg = max(deg, default=0)

    # Bin-sort the vertices by degree: start[d] = first position of degree d.
    count = [0] * (max_deg + 2)
    for d in deg:
        count[d] += 1
    start = [0] * (max_deg + 2)
    for d in range(1, max_deg + 2):
        start[d] = start[d - 1] + count[d - 1]
    pos = [0] * n
    vert = [0] * n
    fill = start[:]
    for v in range(n):
        pos[v] = fill[deg[v]]
        vert[pos[v]] = v
        fill[deg[v]] += 1

    degeneracy = 0
    for i in range(n):
        v = vert[i]  # a vertex of minimum degree among those not yet removed
        if deg[v] > degeneracy:
            degeneracy = deg[v]
        for u in adjacency[offsets[v]:offsets[v + 1]]:  # a slice copy iterates fastest
            pu = pos[u]
            if pu <= i:
                continue  # u was removed before v
            du = deg[u]
            first = start[du]
            if first <= i:
                first = i + 1  # the bucket's stored start is stale: clamp it
            w = vert[first]
            if w != u:  # swap u to the front of its bucket
                vert[pu] = w
                pos[w] = pu
                vert[first] = u
                pos[u] = first
            start[du] = first + 1  # u now ends bucket du - 1
            deg[u] = du - 1
    vert.reverse()
    return vert, degeneracy


def max_back_degree(graph: Graph, order: Sequence[int]) -> int:
    """The largest back degree of an order: max over v of #neighbors before v.

    Greedy coloring along ``order`` uses at most this value + 1 colors.

    Args:
        graph: The graph.
        order: A permutation of 0..n-1.

    Returns:
        The maximum back degree (0 for a graph without edges).

    Raises:
        ValueError: If ``order`` is not a permutation of 0..n-1.

    Complexity: O(n + m) time, O(n) extra space.
    """
    _check_permutation(order, graph.n)
    position = [0] * graph.n
    for i, v in enumerate(order):
        position[v] = i
    back = [0] * graph.n
    for u, v in zip(graph.edge_u, graph.edge_v):
        if position[u] < position[v]:
            back[v] += 1
        else:
            back[u] += 1
    return max(back, default=0)


def is_proper_coloring(graph: Graph, colors: Sequence[int]) -> bool:
    """Check that adjacent vertices have different colors.

    Args:
        graph: The graph.
        colors: ``colors[v]`` is the color of vertex v.

    Returns:
        True if there is one non-negative color per vertex and no edge joins
        two vertices of the same color.
    """
    if len(colors) != graph.n or any(c < 0 for c in colors):
        return False
    return all(colors[u] != colors[v] for u, v in zip(graph.edge_u, graph.edge_v))


def color_count(colors: Sequence[int]) -> int:
    """The number of distinct colors used.

    Args:
        colors: ``colors[v]`` is the color of vertex v.

    Returns:
        The number of distinct values in ``colors``.
    """
    return len(set(colors))


def natural_coloring(graph: Graph) -> list[int]:
    """Greedy coloring along the natural order 0, 1, ..., n-1.

    Args:
        graph: The input graph.

    Returns:
        ``colors[v]`` for every vertex; at most Delta + 1 colors.

    Complexity: O(n + m) time, O(n) extra space.
    """
    return greedy_coloring(graph, natural_order(graph))


def smallest_last_coloring(graph: Graph) -> list[int]:
    """Greedy coloring along the smallest-last order.

    Args:
        graph: The input graph.

    Returns:
        ``colors[v]`` for every vertex; at most degeneracy + 1 colors.

    Complexity: O(n + m) time, O(n) extra space.
    """
    order, _ = smallest_last_order(graph)
    return greedy_coloring(graph, order)


def _check_permutation(order: Sequence[int], n: int) -> None:
    """Raise ValueError unless ``order`` lists every vertex 0..n-1 exactly once.

    Args:
        order: The candidate order.
        n: Number of vertices.

    Raises:
        ValueError: If ``order`` has the wrong length, a vertex outside
            0..n-1, or a repeated vertex.
    """
    if len(order) != n:
        raise ValueError(f"the order has {len(order)} vertices, expected {n}")
    seen = bytearray(n)
    for v in order:
        if not 0 <= v < n:
            raise ValueError(f"vertex {v} is outside 0..{n - 1}")
        if seen[v]:
            raise ValueError(f"vertex {v} appears twice in the order")
        seen[v] = 1


#: Every coloring algorithm, keyed by display name; each maps a graph to colors.
COLORING_ALGORITHMS: dict[str, Callable[[Graph], list[int]]] = {
    "natural": natural_coloring,
    "smallest_last": smallest_last_coloring,
}
