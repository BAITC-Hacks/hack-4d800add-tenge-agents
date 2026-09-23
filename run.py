#!/usr/bin/env python3
"""Build an explainable investigation queue from the organizer's Money Graph data."""

import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path

import networkx as nx
import pandas as pd


ROLES = {"coordinator", "consolidator", "distributor", "transit", "terminal", "peripheral"}
SEED = 42
TOP_N = 30

# These are observed-graph rule thresholds, not learned probabilities.
COORDINATOR_SEED_PAYERS = 2
COORDINATOR_IN_DEG = 3
COORDINATOR_OUT_DEG = 2
DISTRIBUTOR_OUT_DEG = 10
CONSOLIDATOR_IN_DEG = 3
CONSOLIDATOR_IN_KZT = 500_000
CONSOLIDATOR_MAX_ONWARD = 0.20
TRANSIT_MIN_IN_KZT = 50_000
TRANSIT_RATIO_MIN = 0.80
TRANSIT_RATIO_MAX = 1.20
TERMINAL_MIN_IN_KZT = 100_000
SEED_PRIORITY_FACTOR = 0.50
TRUNCATED_PRIORITY_FACTOR = 0.60


def load_inputs(data_dir):
    required = {
        "nodes": {"gid", "depth", "is_seed"},
        "edges": {"src", "dst", "sum_kzt", "n_tx", "depth"},
        "transactions": {"src", "dst", "date", "sum_kzt"},
    }
    tables = {name: pd.read_parquet(data_dir / f"{name}.parquet") for name in required}
    for name, columns in required.items():
        if not columns <= set(tables[name].columns):
            raise ValueError(f"{name}.parquet missing {sorted(columns - set(tables[name].columns))}")
        if tables[name][list(columns)].isna().any().any():
            raise ValueError(f"{name}.parquet contains missing required values")
    nodes, edges, tx = (tables[name] for name in ("nodes", "edges", "transactions"))
    if nodes.gid.duplicated().any() or edges.duplicated(["src", "dst"]).any():
        raise ValueError("Duplicate node gid or directed edge")
    gids = set(nodes.gid)
    if not (set(edges.src) | set(edges.dst)) <= gids:
        raise ValueError("Edge endpoint missing from nodes.parquet")
    if (edges.sum_kzt <= 0).any() or (tx.sum_kzt <= 0).any() or (edges.n_tx < 1).any():
        raise ValueError("Amounts and transaction counts must be positive")
    agg = tx.groupby(["src", "dst"], sort=True).agg(amount=("sum_kzt", "sum"), count=("sum_kzt", "size"))
    pairs = edges.set_index(["src", "dst"])[["sum_kzt", "n_tx"]].sort_index()
    if not pairs.index.equals(agg.index) or not (pairs.n_tx.to_numpy() == agg["count"].to_numpy()).all():
        raise ValueError("Edge pairs or transaction counts do not reconcile")
    if not pd.Series(pairs.sum_kzt.to_numpy() - agg.amount.to_numpy()).abs().le(0.01).all():
        raise ValueError("Edge sums do not reconcile with transactions")
    return nodes.sort_values("gid").reset_index(drop=True), edges.sort_values(["src", "dst"]).reset_index(drop=True)


def graph_and_features(nodes, edges):
    graph = nx.DiGraph()
    graph.add_nodes_from(int(gid) for gid in nodes.gid)
    for edge in edges.itertuples(index=False):
        graph.add_edge(int(edge.src), int(edge.dst), sum_kzt=float(edge.sum_kzt), n_tx=int(edge.n_tx))
    features = nodes[["gid", "depth", "is_seed"]].copy()
    for name, values in (
        ("in_deg", graph.in_degree()), ("out_deg", graph.out_degree()),
        ("in_kzt", graph.in_degree(weight="sum_kzt")),
        ("out_kzt", graph.out_degree(weight="sum_kzt")),
        ("in_tx", graph.in_degree(weight="n_tx")),
        ("out_tx", graph.out_degree(weight="n_tx")),
    ):
        features[name] = features.gid.map(dict(values))
    seeds = set(features.loc[features.is_seed, "gid"])
    features["direct_seed_payers"] = features.gid.map(
        {gid: sum(parent in seeds for parent in graph.predecessors(gid)) for gid in graph}
    )
    features["truncated_by_depth"] = (features.depth == 4) & (features.out_deg == 0)
    return graph, features


def assign_clusters(graph, features):
    # Louvain needs an undirected graph. Sum both directions of each pair so
    # reciprocal transfers contribute their full observed amount.
    undirected = nx.Graph()
    undirected.add_nodes_from(sorted(graph.nodes))
    weights = defaultdict(float)
    for src, dst, attrs in graph.edges(data=True):
        weights[tuple(sorted((src, dst)))] += attrs["sum_kzt"]
    for (src, dst), amount in sorted(weights.items()):
        undirected.add_edge(src, dst, weight=amount)
    communities = nx.community.louvain_communities(undirected, weight="weight", seed=SEED)
    communities.sort(key=min)
    membership = {gid: cluster_id for cluster_id, group in enumerate(communities) for gid in group}
    features["cluster_id"] = features.gid.map(membership).astype(int)
    seed_counts = features.groupby("cluster_id").is_seed.sum().astype(int).to_dict()
    features["cluster_n_seed"] = features.cluster_id.map(seed_counts)
    return features


def role_for(row):
    incoming = float(row.in_kzt)
    outgoing = float(row.out_kzt)
    ratio = outgoing / incoming if incoming else None
    if (not row.is_seed and row.direct_seed_payers >= COORDINATOR_SEED_PAYERS
            and row.in_deg >= COORDINATOR_IN_DEG and row.out_deg >= COORDINATOR_OUT_DEG):
        score = min(0.95, 0.60 + 0.05 * row.direct_seed_payers + 0.02 * row.out_deg)
        evidence = (f"Observed {row.direct_seed_payers} seed payers, {row.in_deg} payers, "
                    f"{row.out_deg} recipients; coordination hypothesis.")
        return "coordinator", score, evidence
    if row.out_deg >= DISTRIBUTOR_OUT_DEG and (row.is_seed or row.out_deg >= 2 * max(1, row.in_deg)):
        score = min(0.95, 0.55 + 0.01 * row.out_deg)
        if row.is_seed:
            evidence = (f"Observed {row.out_deg} recipients, {outgoing:,.0f} KZT sent; "
                        "distribution hypothesis. Seed inflows incomplete.")
        else:
            evidence = (f"Observed {row.out_deg} recipients vs {row.in_deg} payers; "
                        f"{outgoing:,.0f} KZT sent; distribution hypothesis.")
        return "distributor", score, evidence
    if (not row.is_seed and row.depth < 4 and row.in_deg >= CONSOLIDATOR_IN_DEG
            and incoming >= CONSOLIDATOR_IN_KZT and outgoing <= CONSOLIDATOR_MAX_ONWARD * incoming):
        score = min(0.95, 0.58 + 0.025 * row.in_deg + 0.10 * (1 - outgoing / incoming))
        evidence = (f"Observed {row.in_deg} payers, {incoming:,.0f} KZT in, "
                    f"{100 * outgoing / incoming:.0f}% onward; consolidation hypothesis.")
        return "consolidator", score, evidence
    if (not row.is_seed and row.in_deg > 0 and row.out_deg > 0
            and incoming >= TRANSIT_MIN_IN_KZT
            and TRANSIT_RATIO_MIN <= ratio <= TRANSIT_RATIO_MAX):
        score = max(0.50, min(0.90, 0.75 - abs(1 - ratio)))
        evidence = (f"Observed {incoming:,.0f} KZT in, {outgoing:,.0f} KZT out, "
                    f"ratio {ratio:.2f}; transit hypothesis, timing untested.")
        return "transit", score, evidence
    if (not row.is_seed and row.depth in (1, 2, 3) and row.out_deg == 0
            and incoming >= TERMINAL_MIN_IN_KZT):
        score = min(0.80, 0.50 + 0.05 * math.log10(incoming / TERMINAL_MIN_IN_KZT + 1))
        evidence = (f"Observed {incoming:,.0f} KZT from {row.in_deg} payers, "
                    "0 qualifying outflows; possible terminal, external flows unknown.")
        return "terminal", score, evidence
    if row.truncated_by_depth:
        evidence = (f"Depth 4 boundary: {incoming:,.0f} KZT observed in, "
                    f"{row.in_deg} payers; onward transfers unobserved.")
        return "peripheral", 0.10, evidence
    evidence = (f"Observed {row.in_deg} payers, {row.out_deg} recipients, "
                f"{incoming:,.0f} KZT in; insufficient role evidence.")
    if row.is_seed:
        evidence += " Seed inflows incomplete."
    return "peripheral", 0.20, evidence


def assign_roles(features):
    assigned = [role_for(row) for row in features.itertuples(index=False)]
    features[["role", "role_score", "evidence"]] = pd.DataFrame(assigned, index=features.index)
    if (not set(features.role) <= ROLES or features.evidence.str.len().gt(200).any()
            or not features.evidence.str.contains(r"\d").all()):
        raise ValueError("Role output violates the required contract")
    return features


def assign_priority(features):
    total = features.in_kzt + features.out_kzt
    max_total = max(float(total.max()), 1)
    max_degree = max(int(features[["in_deg", "out_deg"]].to_numpy().max()), 1)
    features["volume_signal"] = total.map(lambda x: math.log1p(x) / math.log1p(max_total))
    features["degree_signal"] = features[["in_deg", "out_deg"]].max(axis=1).map(
        lambda x: math.log1p(x) / math.log1p(max_degree)
    )
    features["seed_signal"] = (features.direct_seed_payers / 3).clip(upper=1)
    features["cluster_signal"] = (features.cluster_n_seed / 3).clip(upper=1)
    score = (0.30 * features.volume_signal + 0.20 * features.degree_signal
             + 0.20 * features.seed_signal + 0.20 * features.role_score
             + 0.10 * features.cluster_signal)
    score = score.where(~features.is_seed, score * SEED_PRIORITY_FACTOR)
    score = score.where(~features.truncated_by_depth, score * TRUNCATED_PRIORITY_FACTOR)
    features["priority_score"] = score.clip(0, 1)
    return features


def write_outputs(graph, features, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    roles = features[["gid", "role", "role_score", "cluster_id", "priority_score", "evidence",
                      "depth", "is_seed", "in_deg", "out_deg", "in_kzt", "out_kzt",
                      "in_tx", "out_tx", "direct_seed_payers", "truncated_by_depth"]]
    roles.to_csv(out_dir / "nodes_roles.csv", index=False, float_format="%.6f")

    ranked = features.sort_values(["priority_score", "gid"], ascending=[False, True])
    top = ranked.head(TOP_N).copy()
    top["rank"] = range(1, len(top) + 1)
    def why(row):
        terms = {
            "activity": 0.30 * row.volume_signal,
            "degree": 0.20 * row.degree_signal,
            "seed links": 0.20 * row.seed_signal,
            "role": 0.20 * row.role_score,
            "cluster seeds": 0.10 * row.cluster_signal,
        }
        drivers = sorted(terms, key=lambda name: (-terms[name], name))[:2]
        reason = (f"Observed {row.in_kzt + row.out_kzt:,.0f} KZT in+out activity; "
                  f"{row.in_deg} payers, {row.out_deg} recipients, "
                  f"{row.direct_seed_payers} direct seed payers; "
                  f"main score terms: {drivers[0]} {terms[drivers[0]]:.2f}, "
                  f"{drivers[1]} {terms[drivers[1]]:.2f}.")
        if row.is_seed:
            reason += " Known seed: score x0.50."
        if row.truncated_by_depth:
            reason += " Depth 4 boundary: score x0.60."
        return reason

    top["why"] = top.apply(why, axis=1)
    top[["rank", "gid", "role", "priority_score", "why"]].to_csv(
        out_dir / "top_nodes.csv", index=False, float_format="%.6f"
    )

    internal = defaultdict(float)
    cluster_by_gid = dict(zip(features.gid, features.cluster_id))
    for src, dst, attrs in graph.edges(data=True):
        if cluster_by_gid[src] == cluster_by_gid[dst]:
            internal[cluster_by_gid[src]] += attrs["sum_kzt"]
    cluster_rows = []
    for cluster_id, group in features.groupby("cluster_id", sort=True):
        leaders = ranked.loc[ranked.cluster_id == cluster_id, "gid"].head(3).tolist()
        n_seed = int(group.is_seed.sum())
        turnover = internal[cluster_id]
        cluster_rows.append({
            "cluster_id": int(cluster_id), "n_nodes": len(group), "n_seed": n_seed,
            "sum_kzt_internal": round(turnover, 2),
            "top_gids": "|".join(map(str, leaders)),
            "hypothesis": (f"Observed group of {len(group)} nodes and {n_seed} seeds, "
                           f"{turnover:,.0f} KZT internal; review shared flows."),
        })
    pd.DataFrame(cluster_rows).to_csv(out_dir / "clusters.csv", index=False)
    return roles, top, cluster_rows


def write_viewer(graph, features, top, clusters, out_dir):
    fields = ("role", "evidence", "depth", "cluster_id", "in_deg", "out_deg",
              "in_kzt", "out_kzt", "direct_seed_payers")
    nodes = []
    for row in features.itertuples(index=False):
        node = {"gid": str(row.gid), "is_seed": bool(row.is_seed),
                "truncated": bool(row.truncated_by_depth),
                "role_score": round(float(row.role_score), 6),
                "priority_score": round(float(row.priority_score), 6)}
        for field in fields:
            value = getattr(row, field)
            node[field] = str(value) if field in ("role", "evidence") else float(value) if field.endswith("_kzt") else int(value)
        nodes.append(node)
    edges = [
        {"src": str(src), "dst": str(dst), "sum_kzt": attrs["sum_kzt"], "n_tx": attrs["n_tx"]}
        for src, dst, attrs in sorted(graph.edges(data=True))
    ]
    top_rows = [{"gid": str(row.gid), "rank": int(row.rank), "role": row.role,
                 "priority_score": round(float(row.priority_score), 6)}
                for row in top.itertuples(index=False)]
    payload = json.dumps({"nodes": nodes, "edges": edges, "top": top_rows,
                          "clusters": clusters}, ensure_ascii=False, separators=(",", ":"))
    template = (Path(__file__).parent / "viewer" / "index.html").read_text(encoding="utf-8")
    (out_dir / "viewer.html").write_text(template.replace("__DATA__", payload.replace("</", "<\\/")), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("data"))
    parser.add_argument("--out", type=Path, default=Path("results"))
    args = parser.parse_args()
    start = time.perf_counter()
    nodes, edges = load_inputs(args.data)
    graph, features = graph_and_features(nodes, edges)
    features = assign_clusters(graph, features)
    features = assign_roles(features)
    features = assign_priority(features)
    _, top, clusters = write_outputs(graph, features, args.out)
    write_viewer(graph, features, top, clusters, args.out)
    print(f"{len(features)} nodes, {len(edges)} edges, {len(clusters)} clusters, "
          f"{len(top)} ranked; {time.perf_counter() - start:.2f} s; output: {args.out}")


if __name__ == "__main__":
    main()
