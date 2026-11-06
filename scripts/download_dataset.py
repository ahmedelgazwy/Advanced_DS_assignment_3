"""Download the BHOSLIB/FRB graphs into data/ and verify them against data/manifest.json.

Usage (from the repository root)::

    python -m scripts.download_dataset                    # all 36 graphs, about 50 MB
    python -m scripts.download_dataset --families frb30-15 frb35-17
    python -m scripts.download_dataset --mirror URL       # e.g. the GitHub release
    python -m scripts.download_dataset --write-manifest   # recompute data/manifest.json

Files already present with the right checksum are not downloaded again. With
``--write-manifest`` every graph is loaded and its vertex and edge counts,
both forms, the FRB group structure and the checksum are recorded.

AI-assisted: generated with Claude Code; reviewed and tested by Ahmed Elgazwy
(see README, "AI usage and authorship").
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path
from typing import Optional

from graph_heuristics.datasets import (
    BASE_URL,
    DATA_DIR,
    SOURCE_PAGE,
    FrbInstance,
    frb_instances,
    groups_are_independent,
    load_frb,
    load_manifest,
    sha256_of,
)

USER_AGENT = "Mozilla/5.0 (compatible; frb-dataset-downloader)"


def download(url: str, destination: Path) -> None:
    """Download a URL to a file, via a temporary file so a failure leaves nothing behind.

    Args:
        url: The address to fetch.
        destination: Where to save the file.

    Raises:
        urllib.error.URLError: If the download fails.
    """
    partial = destination.with_suffix(destination.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, open(partial, "wb") as out:
        while block := response.read(1 << 20):
            out.write(block)
    partial.replace(destination)


def fetch(instance: FrbInstance, base_url: str, data_dir: Path, expected: Optional[str]) -> str:
    """Make sure one zip file is present and matches its checksum.

    Args:
        instance: The instance to fetch.
        base_url: Folder URL holding ``<name>.zip``.
        data_dir: Destination folder.
        expected: SHA-256 from the manifest, or None if unknown.

    Returns:
        A one-word status: ``present``, ``downloaded`` or ``MISMATCH``.
    """
    path = instance.zip_path(data_dir)
    if path.exists() and (expected is None or sha256_of(path) == expected):
        return "present"
    download(f"{base_url}{instance.name}.zip", path)
    if expected is not None and sha256_of(path) != expected:
        return "MISMATCH"
    return "downloaded"


def describe(instance: FrbInstance, data_dir: Path) -> dict:
    """Load one graph and collect its manifest entry.

    Args:
        instance: A downloaded instance.
        data_dir: The data folder.

    Returns:
        Its file size and checksum, vertex and edge counts of both forms, the
        exact optima and whether the groups are independent sets.
    """
    path = instance.zip_path(data_dir)
    graph = load_frb(instance, "clq", data_dir)
    return {
        "file": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256_of(path),
        "groups": instance.groups,
        "group_size": instance.group_size,
        "n": graph.n,
        "m_clq": graph.m,
        "m_mis": graph.n * (graph.n - 1) // 2 - graph.m,
        "max_degree_clq": graph.max_degree(),
        "groups_independent": groups_are_independent(graph, instance.group_size),
        "chromatic_number_clq": instance.chromatic_number,
        "min_vertex_cover_mis": instance.min_vertex_cover,
    }


def main(argv: Optional[list[str]] = None) -> int:
    """Command-line entry point.

    Args:
        argv: Arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit status: 0 on success, 1 if a file failed its checksum.
    """
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--families", nargs="+", help="only these families, e.g. frb30-15")
    parser.add_argument("--mirror", default=BASE_URL, help="base URL holding <name>.zip")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    parser.add_argument("--write-manifest", action="store_true",
                        help="load every graph and rewrite manifest.json")
    args = parser.parse_args(argv)

    args.data_dir.mkdir(parents=True, exist_ok=True)
    base_url = args.mirror if args.mirror.endswith("/") else args.mirror + "/"
    instances = frb_instances(args.families)
    manifest = load_manifest(args.data_dir)
    known = manifest.get("instances", {})
    failures = 0
    for instance in instances:
        expected = None if args.write_manifest else known.get(instance.name, {}).get("sha256")
        status = fetch(instance, base_url, args.data_dir, expected)
        failures += status == "MISMATCH"
        print(f"{instance.name:12} {status}", flush=True)

    if args.write_manifest:
        entries = {}
        for instance in instances:
            start = time.perf_counter()
            entries[instance.name] = describe(instance, args.data_dir)
            print(f"{instance.name:12} described in {time.perf_counter() - start:.1f} s",
                  flush=True)
        manifest = {
            "source": SOURCE_PAGE,
            "download_url": BASE_URL + "<name>.zip",
            "retrieved": date.today().isoformat(),
            "format": "zip holding <name>.mtx: Matrix Market coordinate pattern symmetric, "
                      "1-based vertex numbers",
            "instances": {**known, **entries},
        }
        path = args.data_dir / "manifest.json"
        path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path}")
    if failures:
        print(f"{failures} file(s) failed the checksum", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
