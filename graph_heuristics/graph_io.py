"""Read graphs from Matrix Market (.mtx) and DIMACS (.clq/.col/.mis) files.

* **Matrix Market** is the format of the Network Repository BHOSLIB files:
  a ``%%MatrixMarket matrix coordinate pattern symmetric`` header, comment
  lines starting with ``%``, a size line ``rows cols entries``, then one
  ``i j`` pair per edge, numbered from 1.
* **DIMACS** is the format of the original BHOSLIB files: ``c`` comment
  lines, a ``p edge n m`` line, then one ``e u v`` line per edge, numbered
  from 1.

Files can be plain, gzip-compressed (``.gz``) or inside a ``.zip`` archive.
Vertices are renumbered from 0. Lines are streamed, so a 7.4-million-edge file
never needs its whole text in memory.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import gzip
import io
import zipfile
from contextlib import contextmanager
from pathlib import Path
from typing import IO, Iterator, Union

from graph_heuristics.graph import Graph

PathLike = Union[str, Path]


def load_graph(path: PathLike) -> Graph:
    """Read a graph, choosing the reader from the file name.

    ``.mtx`` (also ``.mtx.gz`` and ``.zip`` archives holding a ``.mtx``) is
    read as Matrix Market; ``.clq``, ``.col``, ``.mis`` and ``.dimacs``
    (optionally ``.gz``) as DIMACS.

    Args:
        path: The graph file.

    Returns:
        The graph.

    Raises:
        ValueError: If the file type is unknown or the file is malformed.
    """
    name = Path(path).name.lower().removesuffix(".gz")
    if name.endswith((".mtx", ".zip")):
        return read_mtx(path)
    if name.endswith((".clq", ".col", ".mis", ".dimacs")):
        return read_dimacs(path)
    raise ValueError(f"unknown graph file type: {path}")


def read_mtx(path: PathLike) -> Graph:
    """Read a Matrix Market ``coordinate pattern symmetric`` file as a graph.

    Args:
        path: A ``.mtx`` file, a ``.mtx.gz`` file, or a ``.zip`` archive that
            contains exactly one ``.mtx`` file.

    Returns:
        The graph, with vertex i of the file renumbered i - 1 and the edges in
        file order.

    Raises:
        ValueError: If the header is not a symmetric coordinate pattern of a
            square matrix, or the number of entries differs from the size line.
    """
    with _open_text(path, ".mtx") as lines:
        header = next(lines, "")
        if not header.lower().startswith("%%matrixmarket matrix coordinate"):
            raise ValueError(f"{path}: not a Matrix Market coordinate file")
        if "symmetric" not in header.lower():
            raise ValueError(f"{path}: expected a symmetric matrix (an undirected graph)")
        size = next(line for line in lines if not line.startswith("%"))
        rows, cols, entries = (int(x) for x in size.split()[:3])
        if rows != cols:
            raise ValueError(f"{path}: the matrix is {rows} x {cols}, not square")
        edges = _pairs(lines, comment="%", tag=None)
        graph = Graph.from_edges(rows, edges)
    if edges.count != entries:
        raise ValueError(f"{path}: the size line says {entries} entries, found {edges.count}")
    return graph


def read_dimacs(path: PathLike) -> Graph:
    """Read a DIMACS graph file (``p edge n m`` and ``e u v`` lines).

    Args:
        path: A ``.clq``, ``.col``, ``.mis`` or ``.dimacs`` file, optionally
            gzip-compressed.

    Returns:
        The graph, with vertex i of the file renumbered i - 1.

    Raises:
        ValueError: If the ``p`` line is missing or the number of ``e`` lines
            differs from it.
    """
    with _open_text(path, None) as lines:
        problem = next((line for line in lines if line.startswith("p")), None)
        if problem is None:
            raise ValueError(f"{path}: no 'p edge n m' line")
        _, _, n, m = problem.split()[:4]
        edges = _pairs(lines, comment="c", tag="e")
        graph = Graph.from_edges(int(n), edges)
    if edges.count != int(m):
        raise ValueError(f"{path}: the p line says {m} edges, found {edges.count}")
    return graph


class _pairs:
    """Iterator over the 0-based ``(u, v)`` pairs of the remaining lines; counts them.

    Attributes:
        count: Number of pairs produced so far.
    """

    def __init__(self, lines: Iterator[str], comment: str, tag: str | None) -> None:
        """Wrap a line iterator.

        Args:
            lines: The remaining lines of the file.
            comment: Lines starting with this prefix are skipped.
            tag: If set, each edge line starts with this word (``e``).
        """
        self._lines = lines
        self._comment = comment
        self._tag = tag
        self.count = 0

    def __iter__(self) -> Iterator[tuple[int, int]]:
        """Yield each edge as a 0-based pair."""
        skip_tag = self._tag is not None
        for line in self._lines:
            parts = line.split()
            if not parts or parts[0].startswith(self._comment):
                continue
            if skip_tag:
                parts = parts[1:]
            self.count += 1
            yield int(parts[0]) - 1, int(parts[1]) - 1


@contextmanager
def _open_text(path: PathLike, member_suffix: str | None) -> Iterator[Iterator[str]]:
    """Open a plain, gzip or zip file and yield an iterator over its text lines.

    Args:
        path: The file.
        member_suffix: For a ``.zip``, the suffix of the member to read.

    Returns:
        Context manager yielding the lines.

    Raises:
        ValueError: If a ``.zip`` does not contain exactly one matching member.
    """
    path = Path(path)
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as archive:
            members = [n for n in archive.namelist() if n.lower().endswith(member_suffix or "")]
            if len(members) != 1:
                raise ValueError(f"{path}: expected one {member_suffix} file, found {members}")
            with archive.open(members[0]) as raw:
                yield iter(io.TextIOWrapper(raw, encoding="ascii"))
        return
    handle: IO[str]
    if path.suffix.lower() == ".gz":
        handle = gzip.open(path, "rt", encoding="ascii")
    else:
        handle = open(path, encoding="ascii")
    with handle:
        yield iter(handle)
