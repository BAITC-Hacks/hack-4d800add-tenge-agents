# Requirements — Finance: Money Graph

**Case:** «Граф денег: восстановление финансовой структуры организованной группы по транзакционной сети» — Finance track, HackAlem AI 2026.
**Authoritative source:** [organizer Google Doc (RU/KZ/EN)](https://docs.google.com/document/d/1JPLU-G6R25Ge2hVaY2J9cqvrx7FGExj87XKwJPaMz3o/edit).
Verified against the live HackAlem portal on 23 September 2026. This file is a
working condensation; where it differs from the source, the organizer document
wins. A private verbatim DOCX/text snapshot is kept in `docs/private/`.

## The question the tool must answer
> «Кого из этих 2 248 клиентов смотреть первым и почему?»

An AML analyst knows 81 seed clients (drug-trafficking recipients). The tool reconstructs who sits above them: who collects, who moves, who distributes, who ends up with the money.

## Input (provided, `data/`)
| File | Rows | Columns |
|---|---|---|
| `edges.parquet` | 3 119 | `src, dst, sum_kzt, n_tx, depth` (aggregated per payer→recipient pair) |
| `nodes.parquet` | 2 248 | `gid, depth (min hop, 0=seed), is_seed` |
| `transactions.parquet` | 4 840 | `src, dst, date, sum_kzt` (individual transfers) |

Collection: from 81 seeds, **outgoing transfers only**, 4 hops, threshold ≥ 5 000 KZT, intra-bank, July 2026. Turnover 365 890 012 KZT. Depth distribution: 81 / 472 / 462 / 789 / 444.

This is a one-off batch export; no streaming system is required. The dataset is
anonymized and licensed only for hackathon use. It contains no names, ages,
balances, operation types, or other customer attributes.

## Output (fixed schemas — checked mechanically)

**`out/nodes_roles.csv`** — exactly 2 248 rows
| col | type | meaning |
|---|---|---|
| gid | int64 | client id |
| role | str | one of: consolidator, transit, distributor, terminal, coordinator, peripheral |
| role_score | float 0–1 | confidence |
| cluster_id | int | cluster number |
| priority_score | float 0–1 | analyst priority |
| evidence | str ≤200 | human-readable, **must contain numbers** |

**`out/clusters.csv`** — one row per cluster: `cluster_id, n_nodes, n_seed, sum_kzt_internal, top_gids, hypothesis`

**`out/top_nodes.csv`** — ≥ 20 rows sorted by priority: `rank, gid, role, priority_score, why`

Extra columns allowed; required ones may not be removed.

**Viewer:** network map with flow direction, role/cluster highlighting, search by gid. Web page is fine.

**Performance:** raw parquet → all three CSVs in **< 5 minutes**, locally, on a normal laptop.

## Must-have (all five, each with the jury's check)
1. **Reproducible pipeline** — one command from README on a clean machine, < 5 min, creates 3 files.
2. **Role + score for every node** — 2 248 rows, all columns filled, evidence non-empty.
3. **Documented, explainable role criteria** — jury names 3 random gids; you explain each role in one minute from your metrics.
4. **Clustering** — every node has `cluster_id`; each cluster has size, seed count, turnover, hypothesis.
5. **Top list + visualization** — ≥ 20 ranked nodes with rationale; jury names a gid, you find it on the map and show its links.

## Optional (extra points)
Truncation-artifact handling (separate true terminals from depth-4 cut-offs, with justified method) · temporal patterns (pass-through in 1–2 days, bursts, synchronized inflows) · recurring routes and cycles · anomaly detection (structuring, atypical profiles per hop) · resilience (remove top-N, does it fragment) · **AI analyst assistant** (NL question → graph answer with node refs) · auto node cards · completeness assessment (what data is missing, what to request next).

## Constraints
**Forbidden:** hardcoded gid lists; black-box roles; enrichment with external sources or invented attributes; requiring cloud/GPU/paid services.
**Required:** explainability for non-ML analysts; anonymized data only; findings
phrased as hypotheses for verification, never statements of guilt; ≤ 5 min;
local execution; README section on scaling to ~1M nodes (text only). Internet
may be needed only for an optional external LLM.

## Data traps (announced — handling them is graded)
| Trap | Implication |
|---|---|
| 444 nodes at depth 4 with out_deg = 0 | traversal artifact, NOT "money settled" — naive `out_deg==0 ⇒ terminal` yields 444 false sinks |
| Outgoing-only collection | inbound flows from outside the sample are invisible; full balance unknowable |
| Seed inflows understated | `pass_through` for seeds can be 20+; do not derive seed roles from "how much received" |
| 354 nodes visibly send more than they visibly received | outside-sample inflows are missing; full balances cannot be inferred |
| 5 000 KZT threshold | structuring below threshold is invisible |
| 19 seeds absent from edges, 12 seeds only as recipients | 31 seeds have no outgoing transfers — must still appear in output |
| 16 weakly connected components (1 877 / 270 / rest 2–17 nodes) | 352 nodes outside the giant component |
| Sums vs counts are different signals | 1×4M ≠ 40×100k — use both |
| Directed, weighted graph | undirected centralities erase the meaning; if used (Louvain), say so |
| No ground truth | graded on how well-founded the criteria are |

## Scoring (per case)
| Criterion | Pts |
|---|---|
| Compliance & functionality | 25 |
| Technical implementation (approach, architecture, AI/agentic use, matches stated logic) | 25 |
| README & reproducibility | 25 |
| Value & applicability | 15 |
| Development potential & originality | 10 |

## Deliverables
Repository · README (one-command run, role criteria + thresholds, outputs, limitations, scaling section) · three CSVs · one solution diagram (data → metrics → roles → interface) · 5-minute demo (live run + substantive walkthrough of 2–3 nodes).

Starter code (`starter/starter.py`) already loads data, validates, builds the DiGraph, computes `in_deg, out_deg, in_kzt, out_kzt, in_tx, out_tx, pagerank, pass_through, truncated_by_depth`, and writes the three CSVs with empty roles. It runs in < 1 s.

The organizer notes that the must-haves were validated for a team of 3–4 in
five hours. A solo build must therefore prioritize the five mandatory checks
before optional ML, LLM, or interface polish.
