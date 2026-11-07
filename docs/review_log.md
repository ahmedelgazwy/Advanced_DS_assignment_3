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
