"""Frontier model specifications, pricing, and latency profiles (September 2026).

Note: Performance metrics (ttft_base_ms, ms_per_k_input_tokens, raw_attention_decay)
are analytical simulation parameters calibrated from published vendor model cards and
empirical LLM attention decay literature, NOT real-time live API execution measurements.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ModelProfile:
    """Represents a frontier model's performance and cost parameters for simulation."""
    model_id: str
    display_name: str
    provider: str
    input_price_per_m: float   # USD per 1M input tokens
    output_price_per_m: float  # USD per 1M output tokens
    ttft_base_ms: float        # Base Time-To-First-Token overhead (ms)
    ms_per_k_input_tokens: float  # Latency scaling per 1,000 input tokens
    context_window: int        # Maximum context window in tokens
    raw_attention_decay: float  # Simulated accuracy degradation factor under 60-tool raw schema overload


# September 2026 Frontier Models Evaluation Suite (Analytical Profiles)
FRONTIER_MODELS: Dict[str, ModelProfile] = {
    "gpt-6-astra": ModelProfile(
        model_id="gpt-6-astra",
        display_name="GPT-6 Astra",
        provider="OpenAI",
        input_price_per_m=10.00,
        output_price_per_m=50.00,
        ttft_base_ms=320.0,
        ms_per_k_input_tokens=85.0,
        context_window=1_000_000,
        raw_attention_decay=0.04,  # Drops ~4% accuracy under schema flood
    ),
    "gpt-6.1-sol": ModelProfile(
        model_id="gpt-6.1-sol",
        display_name="GPT-6.1 Sol",
        provider="OpenAI",
        input_price_per_m=2.00,
        output_price_per_m=10.00,
        ttft_base_ms=180.0,
        ms_per_k_input_tokens=45.0,
        context_window=500_000,
        raw_attention_decay=0.05,
    ),
    "claude-5.5-sonnet": ModelProfile(
        model_id="claude-5.5-sonnet",
        display_name="Claude Sonnet 5.5",
        provider="Anthropic",
        input_price_per_m=2.00,
        output_price_per_m=10.00,
        ttft_base_ms=190.0,
        ms_per_k_input_tokens=42.0,
        context_window=500_000,
        raw_attention_decay=0.03,
    ),
    "claude-5.5-opus": ModelProfile(
        model_id="claude-5.5-opus",
        display_name="Claude Opus 5.5",
        provider="Anthropic",
        input_price_per_m=12.00,
        output_price_per_m=60.00,
        ttft_base_ms=380.0,
        ms_per_k_input_tokens=95.0,
        context_window=1_000_000,
        raw_attention_decay=0.035,
    ),
    "gemini-3.8-flash": ModelProfile(
        model_id="gemini-3.8-flash",
        display_name="Gemini 3.8 Flash",
        provider="Google DeepMind",
        input_price_per_m=0.75,
        output_price_per_m=3.75,
        ttft_base_ms=95.0,
        ms_per_k_input_tokens=18.0,
        context_window=2_000_000,
        raw_attention_decay=0.05,
    ),
    "deepseek-v4.1-flash": ModelProfile(
        model_id="deepseek-v4.1-flash",
        display_name="DeepSeek-V4.1-Flash",
        provider="DeepSeek",
        input_price_per_m=0.15,
        output_price_per_m=0.75,
        ttft_base_ms=140.0,
        ms_per_k_input_tokens=32.0,
        context_window=256_000,
        raw_attention_decay=0.07,
    ),
}
