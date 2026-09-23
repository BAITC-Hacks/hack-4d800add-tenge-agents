# Tenge Agents — Explainable Money Graph

HackAlem AI 2026 submission for the Finance track.

## Status

The task requirements and supplied dataset have been reviewed. The project is
currently in the design and implementation phase.

Completed so far:

- selected the Finance / Money Graph task;
- inspected the supplied nodes, edges, and transaction schemas;
- identified graph-traversal and isolated-node edge cases;
- defined the minimum reproducible solution and evaluation checklist.

## Problem

The project analyzes a directed graph of bank transfers and assigns an
explainable behavioral role to every participant. It also groups related nodes,
prioritizes suspicious structures, and provides evidence that an analyst can
inspect for any selected `gid`.

## Planned solution

The first working version will use a deterministic pipeline:

1. Load and validate the supplied graph data.
2. Calculate directed, weighted, and temporal graph features.
3. Detect communities with a fixed random seed.
4. Assign interpretable roles using documented evidence and confidence scores.
5. Rank high-priority nodes and clusters.
6. Export the required CSV files and provide a searchable graph view.

The core analysis will remain reproducible without an external API. An optional
LLM analyst assistant may be added only after the deterministic pipeline and
required outputs are complete.

## Important data constraints

- Depth-four nodes may have no recorded outgoing edges because graph traversal
  stopped at that depth; they must not automatically be classified as terminal.
- Seed nodes with no outgoing edges must still appear in the output.
- Role decisions must be explainable from calculated graph evidence.
- Community detection and exported results must be deterministic.

## Required deliverables

- [ ] Role assignment for every node
- [ ] Cluster summaries
- [ ] Prioritized list of suspicious nodes or structures
- [ ] Required CSV exports
- [ ] Searchable cluster and ego-network visualization
- [ ] One-command local launch
- [ ] Reproducible installation and verification instructions

## Reproducibility

Exact installation, execution, and verification commands will be added with the
first runnable implementation. No deployment or personal account will be
required for the primary evaluation scenario.
