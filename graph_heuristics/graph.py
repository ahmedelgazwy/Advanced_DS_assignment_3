"""Undirected simple graph stored as an edge list plus CSR adjacency arrays.

Vertices are the integers 0..n-1. The graph keeps two views of its edges:

* the **edge list** ``edge_u``/``edge_v`` in input order. The vertex cover
  algorithms scan it, so "select an arbitrary edge" means "the next edge in
  input order";
* the **CSR adjacency** (compressed sparse row): the neighbors of ``v`` are
  ``adjacency[offsets[v]:offsets[v + 1]]``. The coloring algorithms use it.

Both views are flat ``array`` objects, 4 or 8 bytes per entry, so even the
largest FRB graph (4,000 vertices, 7.4 million edges) fits in about 120 MB.
No per-vertex or per-edge Python objects are created. A ``Graph`` is
immutable after construction.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

from array import array
from typing import Iterable, Iterator


class Graph:
    """An undirected simple graph (no self-loops, no parallel edges) on 0..n-1.

    Build one with :meth:`from_edges`; the constructor is internal.

    Attributes:
        n: Number of vertices.
        m: Number of edges.
        edge_u, edge_v: The edges in input order: edge ``i`` joins
            ``edge_u[i]`` and ``edge_v[i]``.
        offsets: CSR row offsets, ``n + 1`` entries.
        adjacency: CSR neighbor lists, ``2m`` entries. The neighbors of each
            vertex appear in the order of the edges that introduced them.
    """

    __slots__ = ("n", "m", "edge_u", "edge_v", "offsets", "adjacency")

    def __init__(self, n: int, edge_u: array, edge_v: array) -> None:
        """Store a validated, duplicate-free edge list and build the CSR arrays.

        Internal: use :meth:`from_edges`, which validates the input.

        Args:
            n: Number of vertices.
            edge_u: First endpoints (``array('i')``), already validated.
            edge_v: Second endpoints, same length as ``edge_u``.
        """
        self.n = n
        self.m = len(edge_u)
        self.edge_u = edge_u
        self.edge_v = edge_v
        self.offsets = _row_offsets(n, edge_u, edge_v)
        self.adjacency = _fill_adjacency(n, edge_u, edge_v, self.offsets)

    @classmethod
    def from_edges(cls, n: int, edges: Iterable[tuple[int, int]]) -> Graph:
        """Build a graph from an edge list.

        A repeated edge, in either orientation (``(u, v)`` then ``(v, u)``),
        is kept once, at its first position.

        Args:
            n: Number of vertices (vertices are 0..n-1).
            edges: Pairs ``(u, v)`` of vertices.

        Returns:
            The graph, with its edges in input order.

        Raises:
            ValueError: If ``n`` is negative, an endpoint is outside 0..n-1, or
                an edge is a self-loop.

        Complexity: O(n + m) time and space.
        """
        if n < 0:
            raise ValueError(f"the number of vertices must be >= 0, got {n}")
        edge_u = array("i")
        edge_v = array("i")
        for u, v in edges:
            if not (0 <= u < n and 0 <= v < n):
                raise ValueError(f"edge ({u}, {v}) has an endpoint outside 0..{n - 1}")
            if u == v:
                raise ValueError(f"self-loop at vertex {u}")
            edge_u.append(u)
            edge_v.append(v)
        keep = _first_occurrences(n, edge_u, edge_v)
        if keep is not None:
            edge_u = array("i", (u for u, k in zip(edge_u, keep) if k))
            edge_v = array("i", (v for v, k in zip(edge_v, keep) if k))
        return cls(n, edge_u, edge_v)

    def edges(self) -> Iterator[tuple[int, int]]:
        """Iterate over the edges in input order.

        Returns:
            Iterator of ``(u, v)`` pairs, each edge exactly once.
        """
        return zip(self.edge_u, self.edge_v)

    def neighbors(self, v: int) -> memoryview:
        """The neighbors of a vertex (a zero-copy view of the CSR array).

        Args:
            v: A vertex in 0..n-1.

        Returns:
            Read-only sequence of the neighbors of ``v``; iterate over it or
            index it like a list.
        """
        return memoryview(self.adjacency)[self.offsets[v]:self.offsets[v + 1]].toreadonly()

    def degree(self, v: int) -> int:
        """The number of neighbors of a vertex.

        Args:
            v: A vertex in 0..n-1.

        Returns:
            The degree of ``v``.
        """
        return self.offsets[v + 1] - self.offsets[v]

    def max_degree(self) -> int:
        """The largest degree, Delta.

        Returns:
            Delta, or 0 for a graph without vertices.
        """
        offsets = self.offsets
        return max((offsets[v + 1] - offsets[v] for v in range(self.n)), default=0)

    def complement(self) -> Graph:
        """The complement graph: u and v are adjacent iff they are not adjacent here.

        Edges are listed in lexicographic order ``(u, v)`` with ``u < v``.

        Returns:
            A new graph with ``n(n - 1)/2 - m`` edges.

        Complexity: O(n^2) time, O(n + n^2/2 - m) space.
        """
        n = self.n
        offsets, adjacency = self.offsets, self.adjacency
        stamp = [-1] * n  # stamp[w] == u  <=>  w is a neighbor of u
        edge_u = array("i")
        edge_v = array("i")
        for u in range(n):
            for i in range(offsets[u], offsets[u + 1]):
                stamp[adjacency[i]] = u
            missing = [w for w in range(u + 1, n) if stamp[w] != u]
            edge_u.extend([u] * len(missing))
            edge_v.extend(missing)
        return Graph(n, edge_u, edge_v)

    def __repr__(self) -> str:
        """Short description, e.g. ``Graph(n=450, m=83198)``."""
        return f"Graph(n={self.n}, m={self.m})"


def _row_offsets(n: int, edge_u: array, edge_v: array) -> array:
    """Prefix sums of the vertex degrees: the CSR row offsets.

    Args:
        n: Number of vertices.
        edge_u, edge_v: The edge list.

    Returns:
        ``array('q')`` of n + 1 offsets; ``offsets[v + 1] - offsets[v]`` is
        the degree of v.
    """
    degree = [0] * n
    for u in edge_u:
        degree[u] += 1
    for v in edge_v:
        degree[v] += 1
    offsets = array("q", bytes(8 * (n + 1)))
    total = 0
    for v in range(n):
        total += degree[v]
        offsets[v + 1] = total
    return offsets


def _fill_adjacency(n: int, edge_u: array, edge_v: array, offsets: array) -> array:
    """Fill the CSR neighbor array; each vertex's neighbors follow edge order.

    Args:
        n: Number of vertices.
        edge_u, edge_v: The edge list.
        offsets: The CSR row offsets from :func:`_row_offsets`.

    Returns:
        ``array('i')`` of 2m neighbor ids.
    """
    adjacency = array("i", bytes(4 * offsets[n]))
    slot = offsets.tolist()  # next free position in each row
    for u, v in zip(edge_u, edge_v):
        adjacency[slot[u]] = v
        slot[u] += 1
        adjacency[slot[v]] = u
        slot[v] += 1
    return adjacency


def _first_occurrences(n: int, edge_u: array, edge_v: array) -> bytearray | None:
    """Find repeated edges, without building a set of edges.

    Each vertex's incident edges are listed in edge order, and a stamp array
    marks the neighbors already seen. An edge whose other endpoint was already
    seen from this vertex repeats an earlier edge.

    Args:
        n: Number of vertices.
        edge_u, edge_v: The edge list, possibly with repeats.

    Returns:
        None if there are no repeats; otherwise a bytearray with 1 for each
        edge to keep (the first occurrence) and 0 for each repeat.

    Complexity: O(n + m) time and space.
    """
    m = len(edge_u)
    offsets = _row_offsets(n, edge_u, edge_v)
    incident = array("i", bytes(4 * offsets[n]))  # edge ids, grouped by vertex
    slot = offsets.tolist()
    for e in range(m):
        u, v = edge_u[e], edge_v[e]
        incident[slot[u]] = e
        slot[u] += 1
        incident[slot[v]] = e
        slot[v] += 1
    seen = [-1] * n  # seen[w] == u  <=>  some earlier edge joins u and w
    keep = None
    for u in range(n):
        for i in range(offsets[u], offsets[u + 1]):
            e = incident[i]
            w = edge_v[e] if edge_u[e] == u else edge_u[e]
            if seen[w] == u:
                if keep is None:
                    keep = bytearray(b"\x01") * m
                keep[e] = 0
            else:
                seen[w] = u
    return keep
