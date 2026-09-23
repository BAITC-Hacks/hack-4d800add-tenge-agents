# Methodology — observed graph hypotheses

This is the implemented method for the organizer's July 2026 Finance sample.
There are no verified role labels. `role_score` is a bounded **rule-strength
index**, not a calibrated probability or a finding of guilt. All evidence
refers to qualifying transfers visible in this four-hop, outgoing-only export.

## Input and metrics

`run.py` validates all required columns, nulls, duplicate ids/pairs, positive
amounts, endpoint references, and edge totals against individual transactions.
It adds **all** nodes before adding edges, including 19 isolated seeds.

For each `gid`, the directed graph gives distinct incoming/outgoing
counterparties (`in_deg`, `out_deg`), incoming/outgoing KZT (`in_kzt`,
`out_kzt`), and transaction counts (`in_tx`, `out_tx`).
`direct_seed_payers` is the number of distinct incoming counterparties that
are known seed gids. `truncated_by_depth` means depth 4 and no observed
outflow. Amounts and counts are different signals; `in_kzt + out_kzt` in the
priority formula is node activity, not a unique-money total or balance.

Seed incoming transfers from outside the sample are missing, so no seed role
uses `out_kzt / in_kzt` or the ratio of observed recipients to observed payers.
For non-seeds, the observed pass-through ratio is `out_kzt / in_kzt` when
`in_kzt > 0`; even a near-one value does not establish that the same funds
were forwarded. Transaction dates are validated as present but not used in
the MVP; no temporal claim is made.

## Primary role rules

Rules are evaluated in this order; the first match wins. The constants are
named in `run.py`. Scores are capped to 0–1 and indicate strength within the
matching rule. These thresholds were checked against the supplied data
distribution: median incoming degree 1, 95th percentile 3, and max 24;
median outgoing degree 0, 95th percentile 5, and max 116. Among non-seeds
at depth 1–3, 1,079 have positive observed inflow and no outflow, so a
meaningful inflow threshold is needed for the terminal hypothesis.

| Order | Role | Rule | Rule strength |
|---|---|---|---|
| 1 | coordinator | Non-seed; `direct_seed_payers ≥ 2`, `in_deg ≥ 3`, `out_deg ≥ 2` | `min(.95, .60 + .05×seed_payers + .02×out_deg)` |
| 2 | distributor | `out_deg ≥ 10`; for non-seeds, `out_deg ≥ 2×max(1, in_deg)` | `min(.95, .55 + .01×out_deg)` |
| 3 | consolidator | Non-seed below depth 4; `in_deg ≥ 3`, `in_kzt ≥ 500,000`, `out_kzt ≤ .20×in_kzt` | `min(.95, .58 + .025×in_deg + .10×(1 − onward_fraction))` |
| 4 | transit | Non-seed; in/out degree positive, `in_kzt ≥ 50,000`, `0.80 ≤ out_kzt/in_kzt ≤ 1.20` | `max(.50, min(.90, .75 − abs(1 − ratio)))` |
| 5 | terminal | Non-seed at depth 1–3; `out_deg = 0`, `in_kzt ≥ 100,000` | `min(.80, .50 + .05×log10(in_kzt/100,000 + 1))` |
| 6 | peripheral | No rule above matched | `.10` at depth-four no-outflow; otherwise `.20` |

The distributor seed exception requires 10 observed recipients but ignores
incomplete seed inflows. An isolated seed is peripheral with numeric evidence.
The terminal label means **no qualifying outflow observed within this export**;
external or below-threshold outflows may exist. Every one of the 444
depth-four no-outflow nodes is peripheral with an explicit observation-boundary
caveat, never terminal solely because traversal stopped.

On the supplied data, the rule order yields 5 coordinators, 39
consolidators, 61 distributors, 38 transit nodes, 306 possible terminals,
and 1,799 peripheral nodes. These counts are descriptive, not ground truth.

## Communities

NetworkX Louvain (`seed=42`) groups an undirected KZT-weighted projection.
For a reciprocal pair, both directed edge amounts are summed into one
undirected weight. Direction is intentionally discarded only for grouping;
it remains in the role logic and viewer. Communities are sorted by smallest
`gid` for stable `cluster_id` values. All 19 isolated seeds form singleton
clusters. The checked environment produced 91 communities.

For each cluster, `sum_kzt_internal` is the sum of original **directed** edge
amounts whose two endpoints belong to that cluster. `n_seed` and `n_nodes`
count members, and `top_gids` lists up to three members by priority. The
`hypothesis` gives cluster size, seed count, internal KZT, and a cautious
function suggested by the most common non-peripheral role, or states when
the group evidence is insufficient. Community membership is a grouping aid, not evidence of
coordination or culpability by itself.

## Priority ranking

For each node, the base priority index is:

```text
0.30 × log1p(in_kzt + out_kzt) / log1p(max node activity)
+ 0.20 × log1p(max(in_deg, out_deg)) / log1p(max graph degree)
+ 0.20 × min(direct_seed_payers / 3, 1)
+ 0.20 × role_score
+ 0.10 × min(cluster_n_seed / 3, 1)
```

Known seeds get a ×0.50 factor because the analyst already has their gids;
depth-four no-outflow nodes get ×0.60 because onward visibility is missing.
Scores are clipped to 0–1, sorted descending, and tied by ascending `gid`.
These are review priorities, not calibrated risk estimates. The top 30 carry
raw KZT, payer and recipient counts, direct seed payer count, and the two
largest additive terms in `why`. Every node retains its priority in
`nodes_roles.csv`.

## One-minute explanation for any gid

Search the gid in `results/viewer.html`, then read its rule evidence and
observed in/out amounts and counterparties. State the matching rule and
threshold above, the numerical score and cluster, then the relevant
visibility caveat. If the node is in `top_nodes.csv`, cite its two largest
priority terms. Phrase the result as a hypothesis for further investigation.
