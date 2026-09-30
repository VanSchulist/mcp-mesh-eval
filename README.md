# 📊 `mcp-mesh-eval`

> **Empirical Frontier Model Evaluation: Dynamic MCP Routing vs. Static Schema Injection**  
> Benchmarking 60 enterprise Model Context Protocol tools across September 2026 frontier models (GPT-6 Astra, Claude Sonnet 5.5, Gemini 3.8 Flash, DeepSeek-V4.1-Flash).

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

1. **Turn-0 Token Bloat**: Connecting to 6 standard MCP servers injects **60 full JSON schemas (~9,800 to 14,000 tokens)** into the prompt before the user sends a single message.
2. **Context Window Attention Degradation ("Lost in the Middle")**: Flooding the prompt with dozens of parameter definitions confuses LLM attention mechanisms, increasing hallucinated arguments and wrong-tool selections by 4–8%.
3. **Severe First-Token Latency (TTFT)**: Processing 10,000+ schema tokens adds 400ms to 1,300ms of pre-fill latency to every agent turn.

`mcp-mesh-eval` is an open, reproducible benchmark comparing the **Raw MCP Baseline** against the **[`mcp-mesh`](https://github.com/VanSchulist/mcp-mesh) Gateway**.

---

## 📈 Quantitative Results

Tested against 50 real-world developer intents across 60 production MCP tools:

| Model | Provider | Turn-0 Tokens (Raw) | Turn-0 Tokens (Mesh) | Token Reduction | Raw TTFT | Mesh TTFT | Latency Cut | Raw Cost (1k turns) | Mesh Cost (1k turns) | Net Savings |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPT-6 Astra** | OpenAI | 9,790 | 384 | **96.1%** | 1,152.2ms | 352.6ms | **-69.4%** | $97.90 | $3.84 | **96.1%** |
| **GPT-6.1 Sol** | OpenAI | 9,790 | 384 | **96.1%** | 620.5ms | 197.3ms | **-68.2%** | $19.58 | $0.77 | **96.1%** |
| **Claude Sonnet 5.5** | Anthropic | 9,790 | 384 | **96.1%** | 601.2ms | 206.1ms | **-65.7%** | $19.58 | $0.77 | **96.1%** |
| **Claude Opus 5.5** | Anthropic | 9,790 | 384 | **96.1%** | 1,310.0ms | 416.5ms | **-68.2%** | $117.48 | $4.61 | **96.1%** |
| **Gemini 3.8 Flash** | Google DeepMind | 9,790 | 384 | **96.1%** | 271.2ms | 101.9ms | **-62.4%** | $7.34 | $0.29 | **96.1%** |
| **DeepSeek-V4.1-Flash** | DeepSeek | 9,790 | 384 | **96.1%** | 453.3ms | 152.3ms | **-66.4%** | $1.47 | $0.06 | **96.1%** |

---

## 🏆 Key Takeaways

1. **96.1% Direct Cost Reduction**: By replacing 60 static schemas with 3 lazy meta-tools (`mesh_search_tools`, `mesh_describe_tool`, `mesh_invoke_tool`), Turn-0 context shrinks from 9,790 tokens to 384 tokens.
2. **~65% to ~70% Latency Improvement**: Agents respond over half a second faster on every turn, dramatically enhancing human-in-the-loop developer velocity.
3. **Higher Tool Selection Accuracy**: Eliminating 57 irrelevant tool schemas from the system prompt increases selection accuracy from **92–96% up to 98%**, completely mitigating context clutter.

---

## 🔬 Dataset & Evaluation Suite

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
- **[Existential Cloud AI Studio](https://www.existentialcloud.ccwu.cc)**: Official research portal, architecture blueprints, and interactive live simulator.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

**Engineered by [Van Schulist](https://github.com/VanSchulist) | [Existential Cloud](https://github.com/VanSchulist/github-ai-studio)**
