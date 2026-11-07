# Review log

Record of the author's decisions, reviews and edits, phase by phase. This file
documents which parts of the work are the author's (see README, "AI usage and
authorship").

| Phase | Author's decisions and review | Author's edits | Tests run by the author |
|---|---|---|---|
| Plan | Accepted all recommendations in `docs/plan.md`: D1 smallest-last ordering; D2 authorship split (the author writes `basic_vertex_cover`, `greedy_coloring`, the hand-worked tests and the report paragraph on the ordering); D3 both FRB forms; D4 scope; D5 repository and package names. | — | — |
| 0. Repository setup | _to fill in after review_ | | |
| 1. Theory notes | _to fill in after review_ | | |
| 2. Graph and data | _to fill in after review_ | | |
| 3. Vertex cover | _to fill in after review_ | Wrote the body of `basic_vertex_cover` (marked in the code). After the first full benchmark, approved an assistant edit inside that block: the covered-vertex `set` became a `bytearray` of flags (same logic; 3.4x faster at n = 10^6, matching the randomized version's data structure). | |
| 4. Coloring | _to fill in after review_ | Wrote the body of `greedy_coloring` (marked in the code). | |
| 3b. Author's tests | Wrote `tests/test_author_cases.py` (five hand-worked graphs); after review, corrected the star test's randomized bound from 2 to 4 (the 2-approximation of the randomized algorithm holds only in expectation). | `tests/test_author_cases.py` | Ran the author's tests. |
| 5. Demo | _to fill in after review_ | | |
| 6. Benchmarks and figures | Chose to have the assistant replace the `set` in `basic_vertex_cover` by a `bytearray` before the final run (see phase 3). | | |
| 7. Report | Wrote the paragraph explaining the choice of the smallest-last ordering (Section 2.4), in the author's own words. | Section 2.4 paragraph | _compile on Overleaf_ |
| 8. Final QA | _to fill in after review_ | | |
