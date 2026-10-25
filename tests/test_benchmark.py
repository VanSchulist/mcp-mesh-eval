"""Automated unit tests for mcp-mesh-eval benchmark suite."""

from __future__ import annotations

import os
import re
import unittest
from mcp_mesh_eval.engine import BenchmarkHarness, DEFAULT_META_TOOLS
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

        self.assertEqual(raw_tokens, 9790)
        self.assertEqual(mesh_tokens, 527)
        savings_pct = (raw_tokens - mesh_tokens) / raw_tokens
        self.assertGreater(savings_pct, 0.94)  # ~94.6% savings

    def test_dynamic_meta_tools_scaling(self) -> None:
        """Verifies that adding/removing meta tools dynamically updates tokens (no hardcoded constants)."""
        base_tokens = self.harness.estimate_mesh_tool_tokens()

        # Create harness with only 1 meta tool
        single_tool_harness = BenchmarkHarness(
            tools_path=self.tools_p,
            intents_path=self.intents_p,
            meta_tools=[DEFAULT_META_TOOLS[0]],
        )
        single_tokens = single_tool_harness.estimate_mesh_tool_tokens()
        self.assertLess(single_tokens, base_tokens)
        self.assertGreater(single_tokens, 100)

        # Create harness with extra custom tool
        extended_tools = list(DEFAULT_META_TOOLS) + [
            {"name": "custom_extra", "description": "An extra tool description", "inputSchema": {}}
        ]
        extended_harness = BenchmarkHarness(
            tools_path=self.tools_p,
            intents_path=self.intents_p,
            meta_tools=extended_tools,
        )
        extended_tokens = extended_harness.estimate_mesh_tool_tokens()
        self.assertGreater(extended_tokens, base_tokens)

    def test_cost_calculation_math(self) -> None:
        """Verifies that cost calculations adhere strictly to declared price per 1M input tokens."""
        for model in FRONTIER_MODELS.values():
            res = self.harness.run_benchmark_for_model(model)
            expected_raw_cost = round((res.raw_tokens / 1_000_000.0) * model.input_price_per_m * 1000.0, 3)
            expected_mesh_cost = round((res.mesh_tokens / 1_000_000.0) * model.input_price_per_m * 1000.0, 3)
            self.assertEqual(res.raw_cost_per_1k_turns, expected_raw_cost)
            self.assertEqual(res.mesh_cost_per_1k_turns, expected_mesh_cost)

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

    def test_report_prose_and_table_consistency(self) -> None:
        """Verifies that the executive summary prose and markdown table use the exact same numbers."""
        results = self.harness.run_all()
        reporter = BenchmarkReporter(results)
        report_md = reporter.generate_markdown_report()

        r0 = results[0]
        # Check that token numbers in prose match r0
        self.assertIn(f"~{r0.raw_tokens:,} estimated tokens to {r0.mesh_tokens:,} tokens", report_md)
        self.assertIn(f"{r0.token_reduction_pct}% reduction", report_md)
        # Check that table contains exact same figures
        table_row = f"| **{r0.model.display_name}** | {r0.model.provider} | ${r0.model.input_price_per_m:.2f} | {r0.raw_tokens:,} | {r0.mesh_tokens:,} | **{r0.token_reduction_pct}%** |"
        self.assertIn(table_row, report_md)

    def test_simulation_disclaimer_present(self) -> None:
        """Verifies that generated reports explicitly declare their simulation / projection nature."""
        results = self.harness.run_all()
        reporter = BenchmarkReporter(results)
        report_md = reporter.generate_markdown_report()

        self.assertIn("Analytical Simulation", report_md)
        self.assertIn("live LLM API calls are not performed in this simulation", report_md)
        self.assertIn("Simulation Assumptions", report_md)


if __name__ == "__main__":
    unittest.main()
