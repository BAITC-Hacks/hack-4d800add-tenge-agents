"""Acceptance checks for the organizer's fixed Finance dataset."""

import subprocess
import sys
import tempfile
import unittest
import json
import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ROLES = {"coordinator", "consolidator", "distributor", "transit", "terminal", "peripheral"}


class PipelineAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.first = Path(cls.temp.name) / "first"
        cls.second = Path(cls.temp.name) / "second"
        for output in (cls.first, cls.second):
            subprocess.run(
                [sys.executable, str(ROOT / "run.py"), "--data", str(ROOT / "data"),
                 "--out", str(output)], check=True, capture_output=True, text=True
            )
        cls.nodes = pd.read_csv(cls.first / "nodes_roles.csv")
        cls.clusters = pd.read_csv(cls.first / "clusters.csv")
        cls.top = pd.read_csv(cls.first / "top_nodes.csv")

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_required_outputs_are_complete_and_repeatable(self):
        for name in ("nodes_roles.csv", "clusters.csv", "top_nodes.csv", "viewer.html"):
            self.assertEqual((self.first / name).read_bytes(), (self.second / name).read_bytes())
        self.assertEqual(len(self.nodes), 2248)
        self.assertEqual(self.nodes.gid.nunique(), 2248)
        self.assertEqual(set(self.nodes.gid), set(pd.read_parquet(ROOT / "data/nodes.parquet").gid))
        self.assertTrue({"gid", "role", "role_score", "cluster_id", "priority_score", "evidence"} <= set(self.nodes))
        self.assertTrue(set(self.nodes.role) <= ROLES)
        self.assertTrue(self.nodes[["role", "role_score", "cluster_id", "priority_score", "evidence"]].notna().all().all())
        self.assertTrue(self.nodes.role_score.between(0, 1).all())
        self.assertTrue(self.nodes.priority_score.between(0, 1).all())
        self.assertTrue(self.nodes.evidence.str.contains(r"\d").all())
        self.assertTrue(self.nodes.evidence.str.len().le(200).all())
        self.assertFalse(self.nodes.evidence.str.contains(r"\b1 (?:payers|recipients)\b").any())

    def test_visibility_boundary_and_isolated_seeds(self):
        depth_four = self.nodes[(self.nodes.depth == 4) & (self.nodes.out_deg == 0)]
        self.assertEqual(len(depth_four), 444)
        self.assertTrue((depth_four.role == "peripheral").all())
        self.assertTrue(depth_four.evidence.str.contains("boundary").all())
        isolated = self.nodes[(self.nodes.in_deg == 0) & (self.nodes.out_deg == 0) & self.nodes.is_seed]
        self.assertEqual(len(isolated), 19)
        self.assertFalse((self.nodes[self.nodes.is_seed].role == "terminal").any())

    def test_clusters_and_queue_reconcile(self):
        self.assertEqual(int(self.clusters.n_nodes.sum()), 2248)
        self.assertEqual(int(self.clusters.n_seed.sum()), 81)
        self.assertEqual(set(self.nodes.cluster_id), set(self.clusters.cluster_id))
        self.assertTrue((self.clusters.n_nodes > 0).all())
        self.assertTrue(self.clusters.hypothesis.str.contains(r"\d").all())
        self.assertFalse(self.clusters.hypothesis.str.contains(r"\b1 (?:nodes|seeds)\b").any())
        membership = dict(zip(self.nodes.gid, self.nodes.cluster_id))
        internal = {cluster_id: 0.0 for cluster_id in self.clusters.cluster_id}
        for edge in pd.read_parquet(ROOT / "data/edges.parquet").itertuples(index=False):
            if membership[edge.src] == membership[edge.dst]:
                internal[membership[edge.src]] += edge.sum_kzt
        for cluster in self.clusters.itertuples(index=False):
            self.assertAlmostEqual(cluster.sum_kzt_internal, internal[cluster.cluster_id], delta=0.01)
        singletons = self.clusters[self.clusters.n_nodes == 1]
        self.assertEqual(len(singletons), 19)
        self.assertTrue(singletons.hypothesis.str.contains("no collective role").all())
        self.assertGreaterEqual(len(self.top), 20)
        self.assertEqual(self.top["rank"].tolist(), list(range(1, len(self.top) + 1)))
        self.assertTrue(self.top.why.str.contains(r"\d").all())
        self.assertFalse(self.top.why.str.contains(r"\b1 (?:payers|recipients)\b").any())
        self.assertEqual(
            self.top.gid.tolist(),
            self.nodes.sort_values(["priority_score", "gid"], ascending=[False, True]).gid.head(len(self.top)).tolist(),
        )

    def test_viewer_embeds_exact_gids_and_links(self):
        html = (self.first / "viewer.html").read_text(encoding="utf-8")
        payload = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1))
        self.assertEqual(len(payload["nodes"]), 2248)
        self.assertEqual(len(payload["edges"]), 3119)
        self.assertEqual(len(payload["clusters"]), len(self.clusters))
        self.assertEqual({node["gid"] for node in payload["nodes"]}, set(self.nodes.gid.astype(str)))
        self.assertTrue(all(isinstance(edge["src"], str) and isinstance(edge["dst"], str) for edge in payload["edges"]))
        self.assertEqual(payload["top"][0]["gid"], str(self.top.gid.iloc[0]))
        self.assertIn('aria-label="Search client gid"', html)


if __name__ == "__main__":
    unittest.main()
