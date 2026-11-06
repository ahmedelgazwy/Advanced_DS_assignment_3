"""Tests for the FRB catalogue, the exact optima and, if downloaded, the real files.

Tests marked ``needs_data`` are skipped when ``data/frb30-15-1.zip`` has not
been downloaded (``python -m scripts.download_dataset``).

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

from pathlib import Path

import pytest

from graph_heuristics.datasets import (
    INSTANCE_NAMES,
    frb_instances,
    groups_are_independent,
    is_available,
    load_frb,
    load_manifest,
    parse_instance,
    sha256_of,
)
from graph_heuristics.generators import planted_graph

SMALLEST = parse_instance("frb30-15-1")
needs_data = pytest.mark.skipif(not is_available(SMALLEST), reason="FRB data not downloaded")


def test_catalogue_has_36_instances() -> None:
    assert len(INSTANCE_NAMES) == len(set(INSTANCE_NAMES)) == 36
    assert INSTANCE_NAMES[0] == "frb30-15-1" and INSTANCE_NAMES[-1] == "frb100-40"
    assert [inst.family for inst in frb_instances(["frb35-17"])] == ["frb35-17"] * 5


def test_parse_instance_and_optima() -> None:
    inst = parse_instance("frb30-15-1")
    assert (inst.groups, inst.group_size, inst.n, inst.family) == (30, 15, 450, "frb30-15")
    assert inst.chromatic_number == 30
    assert inst.min_vertex_cover == 420
    assert inst.url.endswith("/frb30-15-1.zip")
    big = parse_instance("frb100-40")
    assert (big.n, big.chromatic_number, big.min_vertex_cover) == (4000, 100, 3900)
    with pytest.raises(ValueError):
        parse_instance("brock200_1")


def test_groups_are_independent_on_planted_graph() -> None:
    graph, _ = planted_graph(groups=5, size=4, density=0.5, seed=1)
    assert groups_are_independent(graph, 4)
    assert not groups_are_independent(graph.complement(), 4)


def test_sha256(tmp_path: Path) -> None:
    path = tmp_path / "x.bin"
    path.write_bytes(b"abc")
    assert sha256_of(path) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_load_frb_missing_file_and_bad_form(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_frb(SMALLEST, "clq", data_dir=tmp_path)
    with pytest.raises(ValueError):
        load_frb(SMALLEST, "dense", data_dir=tmp_path)


@needs_data
def test_smallest_instance_in_both_forms() -> None:
    clq = load_frb(SMALLEST, "clq")
    assert (clq.n, clq.m) == (450, 83_198)
    assert groups_are_independent(clq, 15)
    mis = load_frb(SMALLEST, "mis")
    assert (mis.n, mis.m) == (450, 17_827)


@needs_data
def test_manifest_matches_the_files() -> None:
    manifest = load_manifest()
    entry = manifest["instances"]["frb30-15-1"]
    assert entry["sha256"] == sha256_of(SMALLEST.zip_path())
    assert (entry["n"], entry["m_clq"], entry["m_mis"]) == (450, 83_198, 17_827)
    assert all(e["groups_independent"] for e in manifest["instances"].values())
