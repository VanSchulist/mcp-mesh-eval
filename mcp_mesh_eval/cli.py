"""CLI for running mcp-mesh-eval benchmarks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from .engine import BenchmarkHarness, DEFAULT_META_TOOLS
from .reporter import BenchmarkReporter
from .live_harness import LiveHarness


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
        help="Execute the full analytical simulation benchmark suite",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run live empirical API benchmark (supports OPENAI_API_KEY or --dry-run)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate live API calls locally without network transmission",
    )

    args = parser.parse_args()

    # Resolve relative paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_p = os.path.join(base_dir, args.tools) if not os.path.isabs(args.tools) else args.tools
    intents_p = os.path.join(base_dir, args.intents) if not os.path.isabs(args.intents) else args.intents

    if not os.path.exists(tools_p) or not os.path.exists(intents_p):
        sys.stderr.write(f"Error: dataset file not found at '{tools_p}' or '{intents_p}'\n")
        sys.exit(1)

    with open(tools_p, "r", encoding="utf-8") as f:
        tools_data = json.load(f)
    with open(intents_p, "r", encoding="utf-8") as f:
        intents_data = json.load(f)

    if args.live:
        print("=" * 80)
        print("  mcp-mesh-eval: Empirical Live API Evaluation Harness")
        print("=" * 80)
        live = LiveHarness(tools=tools_data, meta_tools=DEFAULT_META_TOOLS)
        api_key = os.environ.get("OPENAI_API_KEY")

        if api_key and not args.dry_run:
            print("[*] OPENAI_API_KEY detected. Executing live frontier model evaluation...")
            test_prompt = "Find a tool to inspect table columns in a postgres database"
            raw_res = live.execute_openai_turn(api_key=api_key, model="gpt-4o", mode="raw", prompt=test_prompt)
            mesh_res = live.execute_openai_turn(api_key=api_key, model="gpt-4o", mode="mesh", prompt=test_prompt)
            print(f"[+] Raw 60 Tools Prompt Tokens: {raw_res.actual_prompt_tokens:,} tokens ({raw_res.latency_ms:.1f}ms)")
            print(f"[+] mcp-mesh 4 Tools Prompt Tok: {mesh_res.actual_prompt_tokens:,} tokens ({mesh_res.latency_ms:.1f}ms)")
            savings = raw_res.actual_prompt_tokens - mesh_res.actual_prompt_tokens
            pct = (savings / raw_res.actual_prompt_tokens) * 100.0 if raw_res.actual_prompt_tokens > 0 else 0
            print(f"[+] Empirical Savings: {savings:,} tokens ({pct:.1f}% reduction)")
        else:
            print("[i] Running in empirical dry-run mode (no API key required / --dry-run specified).")
            raw_meas = live.run_mock_turn("raw", "inspect postgres database table")
            mesh_meas = live.run_mock_turn("mesh", "inspect postgres database table")
            print(f"    Raw 60 Tools Schema Size : {len(json.dumps(live.format_raw_tools_openai())):,} characters")
            print(f"    Gateway 4 Meta-Tools Size : {len(json.dumps(live.format_mesh_tools_openai())):,} characters")
            print(f"    Simulated Raw Tokens      : ~{raw_meas.actual_prompt_tokens:,} tokens")
            print(f"    Simulated Gateway Tokens  : ~{mesh_meas.actual_prompt_tokens:,} tokens")
            pct = ((raw_meas.actual_prompt_tokens - mesh_meas.actual_prompt_tokens) / raw_meas.actual_prompt_tokens) * 100.0
            print(f"    Simulated Token Reduction : {pct:.1f}%\n")
            print("[+] Live API harness ready for deployment with OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY.")
            print("=" * 80)
        return

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
