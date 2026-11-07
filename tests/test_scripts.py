"""End-to-end tests of the benchmark, plot and download scripts on tiny inputs.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import csv
import shutil
from pathlib import Path

import pytest

from graph_heuristics.datasets import is_available, parse_instance
from scripts import download_dataset, plot_results, run_benchmarks

SMALLEST = parse_instance("frb30-15-1")


def rows(path: Path) -> list[dict]:
    """Read a CSV file into row dicts."""
    with open(path, newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_scaling_sizes_ladder() -> None:
    assert run_benchmarks.scaling_sizes(20_000) == [1_000, 2_000, 5_000, 10_000, 20_000]
    assert run_benchmarks.scaling_sizes(999) == []


def test_benchmark_and_plots_without_frb_data(tmp_path: Path) -> None:
    out = tmp_path / "results"
    args = ["--quick", "--results", str(out), "--skip", "frb", "memory", "--max-n", "2000",
            "--repeats", "1", "--seeds", "3"]
    assert run_benchmarks.main(args) == 0
    scaling = rows(out / "scaling.csv")
    assert {r["algorithm"] for r in scaling} == set(run_benchmarks.TIMED)
    assert {int(r["n"]) for r in scaling} == {1_000, 2_000}
    worst = rows(out / "worst_cases.csv")
    matching = next(r for r in worst if r["graph"].startswith("perfect matching"))
    assert int(matching["first"]) == 2 * int(matching["optimum"])
    assert (out / "environment.json").exists() and (out / "benchmark_log.txt").exists()

    assert plot_results.main(["--results", str(out)]) == 0
    assert (out / "figures" / "scaling.png").exists()
    assert (out / "figures" / "scaling_per_element.pdf").exists()
    assert "Log-log slopes" in (out / "summary.md").read_text(encoding="utf-8")


@pytest.mark.skipif(not is_available(SMALLEST), reason="FRB data not downloaded")
def test_benchmark_on_one_frb_graph(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    shutil.copy(SMALLEST.zip_path(), data)
    out = tmp_path / "results"
    args = ["--quick", "--results", str(out), "--data-dir", str(data), "--skip", "scaling",
            "memory", "worst", "--repeats", "1", "--seeds", "2", "--copies", "1"]
    assert run_benchmarks.main(args) == 0
    runtime = rows(out / "frb_runtime.csv")
    assert {(r["form"], r["algorithm"]) for r in runtime} == {
        (form, name) for form in ("clq", "mis") for name in run_benchmarks.TIMED}
    (quality,) = rows(out / "frb_quality.csv")
    assert int(quality["opt_cover"]) == 420 and int(quality["chi"]) == 30
    assert 420 <= int(quality["basic_file"]) <= 450
    assert int(quality["natural_file"]) >= 30 and int(quality["sl_file"]) >= 30

    assert plot_results.main(["--results", str(out)]) == 0
    for name in ("frb_runtime", "vc_quality", "coloring_quality", "sl_split"):
        assert (out / "figures" / f"{name}.png").exists()


def test_download_skips_files_already_present(tmp_path: Path, monkeypatch) -> None:
    calls = []
    monkeypatch.setattr(download_dataset, "download", lambda url, dest: calls.append(url))
    (tmp_path / "frb30-15-1.zip").write_bytes(b"x")
    status = download_dataset.fetch(SMALLEST, "https://example.org/", tmp_path, None)
    assert status == "present" and calls == []
    status = download_dataset.fetch(SMALLEST, "https://example.org/", tmp_path, "0" * 64)
    assert status == "MISMATCH" and calls == ["https://example.org/frb30-15-1.zip"]
