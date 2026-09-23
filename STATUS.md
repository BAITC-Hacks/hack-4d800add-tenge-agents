# Status

Update this file at every commit. It is the hourly-checkpoint evidence trail (§6.6) and the first thing Codex reads to resume.

## Now

- **Phase:** plan approved; required pipeline and generated viewer implemented, final delivery checks in progress.
- **Selected task:** Finance — Money Graph, verified in the official portal.
- **Last verified commands:** `python3 run.py --data data --out results` ✅ (0.23 seconds); `python3 -m unittest discover -s tests -v` ✅ (4 tests).
- **Verified inputs:** 2,248 nodes, 3,119 edges, 4,840 transactions,
  81 seeds; edge aggregates reconcile with transactions.
- **Input distribution:** user approved including the small official Parquet
  package in this official repository for judging; it was committed and pushed
  in `5eaae53`.
- **Important correction:** the proposed depth-four logistic classifier is not
  approved for the MVP; it reproduced the truncation trap and cannot be called
  a calibrated terminal probability.
- **Next step:** finish the requested docs relocation, clean-clone rehearsal,
  user viewer inspection, and platform submission.

## Checkpoints

| # | Time | What changed | What is runnable | Tested | Remaining |
|---|---|---|---|---|---|
| 1 | 14:55 | official materials + audited design baseline | organizer starter → 3 schema CSVs | data integrity + starter sanity | implementation plan |
| 2 | 16:28–16:31 | approved plan; deterministic roles, clusters, ranking, generated viewer | `python3 run.py --data data --out results` | 4 acceptance tests green, 0.23 s run; `5eaae53` pushed | viewer visual inspection; clean-clone rehearsal |
| 3 | 16:33 | user requested `docs/` ignored; public documents and diagram moved to repository root | same pipeline and viewer | tests to rerun before corrective commit | clean-clone rehearsal; submission |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |
| 6 |  |  |  |  |  |

## Known issues / decisions taken during the build

- The organizer archive is hackathon-use-only. Commit it only to this official
  repository, with no extra remote, and verify the remote and submission.
- Browser automation blocked opening the local `file://` viewer; generation and
  embedded-data contract are tested, but visual inspection remains to be done.

## Metrics from the last run
- organizer starter elapsed: about 1 second
- role distribution: coordinator 5, consolidator 39, distributor 61, transit
  38, terminal 306, peripheral 1,799
- clusters: 91, including 19 isolated seeds as singletons
- top-5 gids: see `results/top_nodes.csv`; no hardcoded gid list
