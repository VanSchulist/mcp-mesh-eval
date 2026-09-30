"""CLI for running mcp-mesh-eval benchmarks.
"""

from __future__ import annotations

import argparse
import os
import sys

from .engine import BenchmarkHarness
from .reporter import BenchmarkReporter


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mcp-mesh-eval",
        description="Empirical benchmark evaluating Raw MCP vs mcp-mesh gateway across 60 tools and frontier models.",
    )
    parser.add_argument(
        "--tools",
        default="evals/tools_60.json",
        help="Path to 60-tool dataset JSON (default: evals/tools_60.json)",
    )
    parser.add_argument(
        "--intents",
        default="evals/intents_50.json",
        help="Path to 50 evaluation queries JSON (default: evals/intents_50.json)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate BENCHMARK_REPORT.md file",
    )
    parser.add_argument(
        "--chart",
        action="store_true",
        help="Generate assets/benchmark_comparison.svg chart",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Execute the full benchmark suite immediately",
    )

    args = parser.parse_args()

    # Resolve relative paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_p = os.path.join(base_dir, args.tools) if not os.path.isabs(args.tools) else args.tools
    intents_p = os.path.join(base_dir, args.intents) if not os.path.isabs(args.intents) else args.intents

    if not os.path.exists(tools_p) or not os.path.exists(intents_p):
        sys.stderr.write(f"Error: dataset file not found at '{tools_p}' or '{intents_p}'\n")
        sys.exit(1)

    harness = BenchmarkHarness(tools_path=tools_p, intents_path=intents_p)
    results = harness.run_all()

    reporter = BenchmarkReporter(results)
    print(reporter.render_terminal_table())

    if args.report or "--report" in sys.argv:
        report_md = reporter.generate_markdown_report()
        out_p = os.path.join(base_dir, "BENCHMARK_REPORT.md")
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"\n[+] Generated Markdown report: {out_p}")

    if args.chart or "--chart" in sys.argv or "--run" in sys.argv:
        svg_content = reporter.generate_svg_chart()
        assets_dir = os.path.join(base_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)
        chart_p = os.path.join(assets_dir, "benchmark_comparison.svg")
        with open(chart_p, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"[+] Generated SVG chart: {chart_p}")


if __name__ == "__main__":
    main()
