"""Automated unit tests for mcp-mesh-eval benchmark suite."""

from __future__ import annotations

import os
import unittest
from mcp_mesh_eval.engine import BenchmarkHarness
from mcp_mesh_eval.models import FRONTIER_MODELS
from mcp_mesh_eval.reporter import BenchmarkReporter


class TestBenchmarkEvaluation(unittest.TestCase):
    """Test suite for benchmark dataset, calculation engine, and reporting."""

    @classmethod
    def setUpClass(cls) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.tools_p = os.path.join(base_dir, "evals", "tools_60.json")
        cls.intents_p = os.path.join(base_dir, "evals", "intents_50.json")
        cls.harness = BenchmarkHarness(tools_path=cls.tools_p, intents_path=cls.intents_p)

    def test_dataset_integrity(self) -> None:
        self.assertEqual(len(self.harness.tools), 60)
        self.assertEqual(len(self.harness.intents), 50)

        # Verify all tools have required schema keys
        servers = set()
        for t in self.harness.tools:
            self.assertIn("server", t)
            self.assertIn("name", t)
            self.assertIn("description", t)
            self.assertIn("parameters", t)
            servers.add(t["server"])

        self.assertEqual(len(servers), 6)
        self.assertIn("github", servers)
        self.assertIn("postgres", servers)
        self.assertIn("slack", servers)
        self.assertIn("aws", servers)
        self.assertIn("filesystem", servers)
        self.assertIn("stripe", servers)

    def test_token_estimates(self) -> None:
        raw_tokens = self.harness.estimate_raw_tool_tokens()
        mesh_tokens = self.harness.estimate_mesh_tool_tokens()

        self.assertGreater(raw_tokens, 8000)
        self.assertLess(mesh_tokens, 500)
        savings_pct = (raw_tokens - mesh_tokens) / raw_tokens
        self.assertGreater(savings_pct, 0.90)  # >90% savings

    def test_simulated_mesh_search(self) -> None:
        matches = self.harness.simulate_mesh_search("open pull request on git", limit=3)
        self.assertTrue(len(matches) > 0)
        tool_names = [m["name"] for m in matches]
        self.assertIn("create_pull_request", tool_names)

    def test_run_benchmark_model(self) -> None:
        model = FRONTIER_MODELS["gpt-6-astra"]
        res = self.harness.run_benchmark_for_model(model)
        self.assertGreater(res.mesh_accuracy, 95.0)
        self.assertGreater(res.token_reduction_pct, 90.0)
        self.assertGreater(res.cost_reduction_pct, 90.0)
        self.assertGreater(res.raw_ttft_ms, res.mesh_ttft_ms)

    def test_reporter_outputs(self) -> None:
        results = self.harness.run_all()
        self.assertEqual(len(results), len(FRONTIER_MODELS))
        reporter = BenchmarkReporter(results)

        table = reporter.render_terminal_table()
        self.assertIn("mcp-mesh-eval", table)
        self.assertIn("GPT-6 Astra", table)

        md = reporter.generate_markdown_report()
        self.assertIn("Quantitative Benchmark Data", md)
        self.assertIn("Key Findings", md)

        svg = reporter.generate_svg_chart()
        self.assertIn("<svg", svg)
        self.assertIn("GPT-6 Astra", svg)


if __name__ == "__main__":
    unittest.main()
