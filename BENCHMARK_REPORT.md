# 📊 `mcp-mesh-eval` Benchmark Simulation Report

> **Analytical Simulation: Dynamic MCP Gateway Routing vs. Static Schema Injection**  
> *Conducted: September 2026 | Suite: 60 Production Tools across 6 Servers | 50 Real-World Intents*  
> *Note: Token counts estimated via JSON serialization (chars / 3.4). Latency and costs projected via analytical performance models; live LLM API calls are not performed in this simulation.*

---

## 🎯 Executive Summary

Connecting autonomous agents to multiple enterprise Model Context Protocol (MCP) servers (GitHub, PostgreSQL, Slack, AWS, Filesystem, Stripe) introduces massive prompt token overhead and attention degradation.

In this analytical simulation benchmark, we evaluate **60 real-world MCP tools** across **6 frontier AI model profiles** comparing:
1. **Baseline (Raw MCP)**: Full static injection of 60 JSON schemas into the system prompt.
2. **mcp-mesh Gateway**: Dynamic lazy tool routing exposing only 4 compact meta-tools (`mesh_search_tools`, `mesh_describe_tool`, `mesh_invoke_tool`, `mesh_status`).

### 🏆 Key Findings (Simulated & Projected)

- 📉 **Token Reduction**: Turn-0 token footprint drops from **~9,790 estimated tokens to 527 tokens** (an estimated **94.6% reduction**).
- ⚡ **First-Token Latency (TTFT)**: Projected model response pre-fill latency is reduced by **61.5%–68.3%** across simulated model profiles.
- 💰 **Financial Economy**: Projected input token costs drop by **94.6%**. On high-tier models like GPT-6 Astra, projected Turn-0 operating cost falls from **$97.90 per 1,000 turns to just $5.27**.
- 🎯 **Tool Selection Accuracy**: Eliminating distractor schemas from the system prompt yields a simulated selection accuracy of **98.0%** (via BM25 retrieval) compared to **92.0%–96.0%** in the attention degradation baseline model.

---

## 📈 Quantitative Simulation Data

| Model Profile | Provider | Input Price ($/1M) | Turn-0 Tokens (Raw Est.) | Turn-0 Tokens (Mesh Est.) | Token Reduction | Projected Raw TTFT | Projected Mesh TTFT | Latency Cut | Projected Raw Cost (1k turns) | Projected Mesh Cost (1k turns) | Net Savings |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **GPT-6 Astra** | OpenAI | $10.00 | 9,790 | 527 | **94.6%** | 1152.2ms | 364.8ms | **-68.3%** | $97.90 | $5.27 | **94.6%** |
| **GPT-6.1 Sol** | OpenAI | $2.00 | 9,790 | 527 | **94.6%** | 620.5ms | 203.7ms | **-67.2%** | $19.58 | $1.05 | **94.6%** |
| **Claude Sonnet 5.5** | Anthropic | $2.00 | 9,790 | 527 | **94.6%** | 601.2ms | 212.1ms | **-64.7%** | $19.58 | $1.05 | **94.6%** |
| **Claude Opus 5.5** | Anthropic | $12.00 | 9,790 | 527 | **94.6%** | 1310.0ms | 430.1ms | **-67.2%** | $117.48 | $6.32 | **94.6%** |
| **Gemini 3.8 Flash** | Google DeepMind | $0.75 | 9,790 | 527 | **94.6%** | 271.2ms | 104.5ms | **-61.5%** | $7.34 | $0.40 | **94.6%** |
| **DeepSeek-V4.1-Flash** | DeepSeek | $0.15 | 9,790 | 527 | **94.6%** | 453.3ms | 156.9ms | **-65.4%** | $1.47 | $0.08 | **94.6%** |

---

## 🔬 Methodology & Simulation Assumptions

### 1. Token Estimation Methodology
- **Character Heuristic**: Token counts are estimated using the standard empirical ratio for JSON schema payloads: `tokens = total_compact_json_chars / 3.4`.
- **Raw MCP Baseline**: All 60 tool schemas from `evals/tools_60.json` are serialized to compact JSON and summed (~9,790 tokens).
- **mcp-mesh Gateway**: The 4 active gateway meta-tools (`mesh_search_tools`, `mesh_describe_tool`, `mesh_invoke_tool`, `mesh_status`) are serialized to compact JSON and summed (~527 tokens).

### 2. Latency Projection Model
- Time-To-First-Token (TTFT) is projected using linear pre-fill extrapolation:
  `TTFT = ttft_base_ms + (input_tokens / 1000) * ms_per_k_input_tokens`
- Base latencies and scaling coefficients are derived from vendor technical specifications and published attention benchmarks.

### 3. Cost Calculation Formula
- Cost per 1,000 turns is computed as:
  `Cost = (input_tokens / 1,000,000) * input_price_per_m * 1000`
- Assumes 1,000 user turns where Turn-0 tool schemas are injected on each request. Does not include user prompt or tool output tokens.

### 4. Important Disclaimer
- **Simulation Notice**: This harness performs analytical modeling based on deterministic schemas, BM25 retrieval, and mathematical projection formulas. It does not issue live HTTP requests to third-party LLM APIs. Live empirical testing across frontier models is planned for future releases.

---

## 🚀 Reproducibility

To reproduce this simulation suite locally:
```bash
git clone https://github.com/VanSchulist/mcp-mesh-eval.git
cd mcp-mesh-eval
python main.py --run --report
```

---

**Published by [Van Schulist](https://github.com/VanSchulist) | [Existential Cloud AI Studio](https://www.existentialcloud.ccwu.cc)**