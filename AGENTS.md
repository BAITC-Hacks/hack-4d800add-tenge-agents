# AGENTS.md — Money Graph

This is a solo HackAlem AI Finance-track project. The official specification is
authoritative; planning documents are proposals and must be challenged when
they conflict with the task, evidence, or remaining time.

## Read first

1. `STATUS.md`
2. `REQUIREMENTS.md`
3. `VERIFICATION.md`
4. `METHODOLOGY.md`
5. `ARCHITECTURE.md`
6. relevant files in `docs/private/`, especially current event rules and the
   internal build plan

## Current gate

The design was audited and the user approved the implementation plan on
23 September. The required pipeline is implemented; finish verification,
documentation, clean-clone rehearsal, and the final push before 18:00. Do not
treat an older Fable decision as fixed merely because it is written down.

## Non-negotiables

- Work only in this official repository; do not add mirrors or extra remotes.
- Preserve a truthful, understandable history and push visible checkpoints.
- Never commit secrets, credentials, private event material, or personal data.
- Use only attributes present in the organizer data; never invent customer
  identity or demographic fields.
- Phrase roles as investigation hypotheses, never findings of guilt.
- Every role and priority position needs concrete numeric evidence.
- Add all 2,248 nodes, including isolated seeds.
- Do not call depth-four no-outflow nodes terminal solely because traversal
  stopped there.
- Core pipeline and viewer must work without an LLM, paid service, or personal
  account.
- Use deterministic seeds and `gid` tie-breaking.

## Scope order

1. One-command pipeline and exact CSV schemas.
2. Explainable role and score for every node.
3. Clusters and summaries.
4. Top-20-or-more priority list with reasons.
5. Minimal searchable directed viewer.
6. README, diagram, disclosure, clean-run rehearsal.
7. Optional temporal/ML/LLM work only after 1–6 pass.

Choose the simplest viable Python and local-viewer stack during planning. Do not
introduce a second build toolchain or framework without a concrete scoring need.
Run commands belong in README once they actually work; thresholds belong in
`METHODOLOGY.md` and implementation configuration.

## Local organizer inputs

`data/` is complete, verified, and committed to this official repository for
hackathon judging. `starter/` is complete locally but remains ignored because
the finished pipeline does not depend on it. Do not delete or modify either.
