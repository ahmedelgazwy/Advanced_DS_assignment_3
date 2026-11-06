"""Tests for the Matrix Market and DIMACS readers (plain, gzip and zip files).

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import gzip
import zipfile
from pathlib import Path

import pytest

from graph_heuristics.graph_io import load_graph, read_dimacs, read_mtx

MTX = """%%MatrixMarket matrix coordinate pattern symmetric
% a triangle plus a pendant vertex
4 4 4
2 1
3 1
3 2
4 3
"""

DIMACS = """c a triangle plus a pendant vertex
p edge 4 4
e 1 2
e 1 3
e 2 3
e 3 4
"""


def write(path: Path, text: str) -> Path:
    """Write ``text`` to ``path`` (gzip if it ends with .gz, zip if .zip)."""
    if path.suffix == ".gz":
        with gzip.open(path, "wt", encoding="ascii") as handle:
            handle.write(text)
    elif path.suffix == ".zip":
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("graph.mtx", text)
            archive.writestr("readme.html", "<html></html>")
    else:
        path.write_text(text, encoding="ascii")
    return path


@pytest.mark.parametrize("name", ["g.mtx", "g.mtx.gz", "g.zip"])
def test_read_mtx(tmp_path: Path, name: str) -> None:
    graph = read_mtx(write(tmp_path / name, MTX))
    assert (graph.n, graph.m) == (4, 4)
    assert list(graph.edges()) == [(1, 0), (2, 0), (2, 1), (3, 2)]  # renumbered from 0


@pytest.mark.parametrize("name", ["g.clq", "g.col.gz", "g.mis"])
def test_read_dimacs(tmp_path: Path, name: str) -> None:
    graph = read_dimacs(write(tmp_path / name, DIMACS))
    assert (graph.n, graph.m) == (4, 4)
    assert list(graph.edges()) == [(0, 1), (0, 2), (1, 2), (2, 3)]


def test_load_graph_chooses_the_reader(tmp_path: Path) -> None:
    assert load_graph(write(tmp_path / "a.mtx", MTX)).m == 4
    assert load_graph(write(tmp_path / "a.clq", DIMACS)).m == 4
    with pytest.raises(ValueError):
        load_graph(write(tmp_path / "a.txt", MTX))


def test_mtx_entry_count_must_match(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="entries"):
        read_mtx(write(tmp_path / "bad.mtx", MTX.replace("4 4 4", "4 4 5")))


def test_mtx_must_be_symmetric_and_square(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="symmetric"):
        read_mtx(write(tmp_path / "a.mtx", MTX.replace("symmetric", "general")))
    with pytest.raises(ValueError, match="square"):
        read_mtx(write(tmp_path / "b.mtx", MTX.replace("4 4 4", "4 5 4")))
    with pytest.raises(ValueError, match="Matrix Market"):
        read_mtx(write(tmp_path / "c.mtx", "hello\n"))


def test_dimacs_edge_count_must_match(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="edges"):
        read_dimacs(write(tmp_path / "bad.clq", DIMACS.replace("p edge 4 4", "p edge 4 3")))
    with pytest.raises(ValueError, match="p edge"):
        read_dimacs(write(tmp_path / "none.clq", "c nothing\n"))


def test_vertex_out_of_range_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        read_mtx(write(tmp_path / "a.mtx", MTX.replace("4 3\n", "5 3\n")))


def test_zip_must_hold_one_mtx(tmp_path: Path) -> None:
    path = tmp_path / "two.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("a.mtx", MTX)
        archive.writestr("b.mtx", MTX)
    with pytest.raises(ValueError, match="expected one"):
        read_mtx(path)
