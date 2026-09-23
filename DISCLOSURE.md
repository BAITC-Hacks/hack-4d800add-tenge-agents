# Disclosure of organizer materials, third-party software, and AI assistance

This file must be updated during the build so that the final submission describes
what was actually used. The selected task specification and current hackathon
regulations are authoritative.

## Organizer-provided materials

- `data/` — anonymized Finance case data supplied for hackathon use. The three
  Parquet files are included in this official submission repository so judges
  can reproduce the result; they must not be reused outside the hackathon.
- `starter/` — organizer starter code for loading and validating the data,
  constructing a directed graph, calculating basic metrics, and writing output
  templates.

`starter/` remains local and ignored because it is not a runtime dependency.
The pipeline reuses the organizer's input validation, directed graph, and
basic degree/amount ideas, while adding all isolated nodes, role rules,
communities, ranking, and the viewer.

## Pre-existing participant code

None identified at the start of implementation. Update this section if any
pre-existing utility or template is used.

## AI assistance used so far

- Claude Fable produced initial product, architecture, UI, and build-plan drafts.
- OpenAI Codex checked the live Finance track, validated the organizer package,
  audited and simplified the drafts, and reorganized the repository documentation.

- OpenAI Codex implemented the Python pipeline, rule criteria, clustering,
  ranking, static viewer, acceptance checks, and documentation during the
  competition window. The human participant approved the scope, data
  distribution, and seed-priority policy.

## Third-party software

`requirements.txt` pins pandas (BSD-3-Clause), pyarrow (Apache-2.0), NetworkX
(BSD-3-Clause), and NumPy (BSD-3-Clause). They load Parquet, build/analyze the
graph, and export CSVs. The viewer uses browser-native HTML, CSS, SVG, and
JavaScript with no vendored library, CDN, or second build toolchain.

## Optional runtime services

No runtime service or LLM is used. `.env` and any user API key are ignored and
are not read by the pipeline or viewer.

## Data handling

The organizer describes the dataset as anonymized and restricted to hackathon
use. Do not infer that identifiers are synthetic, and do not upload the data to
an external service without confirming that the rules allow it.
