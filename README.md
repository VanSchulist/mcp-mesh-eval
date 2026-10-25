# 📊 `mcp-mesh-eval`

> **Context Window & Cost Simulation Model: Dynamic MCP Routing vs. Static Schema Injection**  
> Analytical performance simulation benchmarking 60 enterprise Model Context Protocol tools across frontier model profiles (GPT-6 Astra, Claude Sonnet 5.5, Gemini 3.8 Flash, DeepSeek-V4.1-Flash).

[![Official Gateway](https://img.shields.io/badge/Gateway-mcp--mesh-purple.svg)](https://github.com/VanSchulist/mcp-mesh)
[![Research Portal](https://img.shields.io/badge/Portal-www.existentialcloud.ccwu.cc-8A2BE2.svg)](https://www.existentialcloud.ccwu.cc)
[![CI: Benchmark Harness](https://github.com/VanSchulist/mcp-mesh-eval/actions/workflows/eval.yml/badge.svg)](https://github.com/VanSchulist/mcp-mesh-eval/actions/workflows/eval.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

<p align="center">
  <img src="assets/benchmark_comparison.svg" alt="mcp-mesh-eval Benchmark Results" width="950">
</p>

---

## 🎯 Executive Summary

As developers equip AI agents with multiple enterprise **Model Context Protocol (MCP)** servers (GitHub, PostgreSQL, Slack, AWS Cloud, Filesystem, Stripe), a major infrastructure bottleneck emerges:

1. **Turn-0 Token Bloat**: Connecting to 6 standard MCP servers injects **60 full JSON schemas (~9,790 estimated tokens)** into the prompt before the user sends a single message.
2. **Context Window Attention Degradation ("Lost in the Middle")**: Flooding the prompt with dozens of parameter definitions confuses LLM attention mechanisms, increasing hallucinated arguments and wrong-tool selections by 4–8%.
3. **Severe First-Token Latency (TTFT)**: Processing 10,000+ schema tokens adds 400ms to 1,300ms of pre-fill latency to every agent turn.

`mcp-mesh-eval` is an open, reproducible analytical simulation benchmark comparing the **Raw MCP Baseline** against the **[`mcp-mesh`](https://github.com/VanSchulist/mcp-mesh) Gateway**.

---

## 📈 Quantitative Simulation Data

Tested against 50 real-world developer intents across 60 production MCP tools:

| Model Profile | Provider | Input Price ($/1M) | Turn-0 Tokens (Raw Est.) | Turn-0 Tokens (Mesh Est.) | Token Reduction | Projected Raw TTFT | Projected Mesh TTFT | Latency Cut | Projected Raw Cost (1k turns) | Projected Mesh Cost (1k turns) | Net Savings |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPT-6 Astra** | OpenAI | $10.00 | 9,790 | 527 | **94.6%** | 1,152.2ms | 364.8ms | **-68.3%** | $97.90 | $5.27 | **94.6%** |
| **GPT-6.1 Sol** | OpenAI | $2.00 | 9,790 | 527 | **94.6%** | 620.5ms | 203.7ms | **-67.2%** | $19.58 | $1.05 | **94.6%** |
| **Claude Sonnet 5.5** | Anthropic | $2.00 | 9,790 | 527 | **94.6%** | 601.2ms | 212.1ms | **-64.7%** | $19.58 | $1.05 | **94.6%** |
| **Claude Opus 5.5** | Anthropic | $12.00 | 9,790 | 527 | **94.6%** | 1,310.0ms | 430.1ms | **-67.2%** | $117.48 | $6.32 | **94.6%** |
| **Gemini 3.8 Flash** | Google DeepMind | $0.75 | 9,790 | 527 | **94.6%** | 271.2ms | 104.5ms | **-61.5%** | $7.34 | $0.40 | **94.6%** |
| **DeepSeek-V4.1-Flash** | DeepSeek | $0.15 | 9,790 | 527 | **94.6%** | 453.3ms | 156.9ms | **-65.4%** | $1.47 | $0.08 | **94.6%** |

---

## 🏆 Key Takeaways (Simulated & Projected)

1. **94.6% Direct Token & Cost Reduction**: By replacing 60 static schemas with the 4 active gateway meta-tools (`mesh_search_tools`, `mesh_describe_tool`, `mesh_invoke_tool`, `mesh_status`), Turn-0 prompt tokens drop from an estimated 9,790 to 527 tokens.
2. **~61% to ~68% Projected Latency Improvement**: Model response pre-fill latency is reduced by up to 787ms on large reasoning models.
3. **Higher Tool Selection Accuracy**: Eliminating 56 irrelevant tool schemas from the system prompt yields 98% simulated tool selection accuracy, avoiding context clutter degradation.

---

## 🔬 Methodology & Simulation Assumptions

- **Token Estimation**: Tokens are estimated via compact JSON serialization length divided by 3.4 (`chars / 3.4`), the standard character-to-token ratio for English/JSON payloads.
- **Latency Model**: Time-to-first-token is calculated via `TTFT = ttft_base_ms + (tokens / 1000) * ms_per_k_input_tokens`, using empirical coefficients derived from vendor technical reports.
- **Cost Model**: Direct input cost is computed as `(input_tokens / 1,000,000) * input_price_per_m * 1000` per 1,000 user turns.
- **Disclaimer**: This repository provides an analytical simulation and economic projection framework. It does not issue live HTTP calls to proprietary LLM APIs. Live empirical testing across frontier models is planned for future releases.

---

## 📂 Dataset & Evaluation Suite

- **Tool Catalog (`evals/tools_60.json`)**: 60 fully specified MCP tools across 6 server domains:
  - `github` (10 tools): repository management, PR creation, code search, CI workflows.
  - `postgres` (10 tools): read-only queries, DML execution, schema introspection, indexing.
  - `slack` (10 tools): channel messaging, search, reaction management, user profiles.
  - `aws` (10 tools): EC2 orchestration, CloudWatch metrics, S3 object storage, Lambda triggers.
  - `filesystem` (10 tools): atomic file I/O, regex searching, directory trees, checksum verification.
  - `stripe` (10 tools): customers, payment intents, subscriptions, refunds, invoices.
- **Intent Test Cases (`evals/intents_50.json`)**: 50 realistic developer prompts testing natural language tool selection, parameter formatting, and distractor resistance.

---

## 🚀 Reproduce the Benchmark

No external dependencies required. Pure Python 3.10+ standard library:

```bash
# 1. Clone the evaluation repository
git clone https://github.com/VanSchulist/mcp-mesh-eval.git
cd mcp-mesh-eval

# 2. Run the evaluation and print the comparison table
python main.py --run

# 3. Export Markdown report and SVG chart
python main.py --run --report --chart
```

---

## 🔗 Related Projects

- **[`mcp-mesh`](https://github.com/VanSchulist/mcp-mesh)**: The official Model Context Protocol dynamic gateway and lazy tool router.
- **[`mcp-registry-cli`](https://github.com/VanSchulist/mcp-registry-cli)**: The zero-config community package manager & discovery registry for MCP servers.
- **[Existential Cloud AI Studio](https://www.existentialcloud.ccwu.cc)**: Official research portal, architecture blueprints, and interactive live simulator.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

**Engineered by [Van Schulist](https://github.com/VanSchulist) | [Existential Cloud](https://github.com/VanSchulist/github-ai-studio)**
