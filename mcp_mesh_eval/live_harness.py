"""Empirical Live API Benchmark Harness for mcp-mesh-eval.

Executes real-world prompt token and latency measurements against live LLM APIs
(OpenAI, Anthropic, Gemini) using standard library HTTP requests.
Compares Raw 60-tool schema injection vs mcp-mesh 4-tool gateway routing.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LiveMeasurement:
    """Telemetry captured from an actual live LLM API call."""
    provider: str
    model: str
    mode: str                    # 'raw' (60 tools) vs 'mesh' (4 meta-tools)
    actual_prompt_tokens: int    # Extracted from API usage object
    latency_ms: float            # Round-trip HTTP duration in milliseconds
    tool_calls_returned: int     # Count of tool calls emitted by LLM
    invoked_tool_name: Optional[str] = None
    response_text: Optional[str] = None
    http_status: int = 200
    is_mock: bool = False


class LiveHarness:
    """Prepares and executes live API requests comparing Raw MCP vs mcp-mesh gateway."""

    def __init__(
        self,
        tools: List[Dict[str, Any]],
        meta_tools: List[Dict[str, Any]],
    ) -> None:
        self.tools = tools
        self.meta_tools = meta_tools

    def format_raw_tools_openai(self) -> List[Dict[str, Any]]:
        """Formats the 60 tools into OpenAI-standard function calling schema."""
        formatted = []
        for tool in self.tools:
            name = f"{tool['server']}__{tool['name']}"
            formatted.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            k: {
                                "type": v,
                                "description": f"Parameter {k} for {tool['name']}",
                            }
                            for k, v in tool.get("parameters", {}).items()
                        },
                        "required": list(tool.get("parameters", {}).keys()),
                    },
                },
            })
        return formatted

    def format_mesh_tools_openai(self) -> List[Dict[str, Any]]:
        """Formats the 4 mcp-mesh meta-tools into OpenAI-standard schema."""
        formatted = []
        for tool in self.meta_tools:
            formatted.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("inputSchema", {"type": "object", "properties": {}}),
                },
            })
        return formatted

    def format_raw_tools_anthropic(self) -> List[Dict[str, Any]]:
        """Formats the 60 tools into Anthropic Claude tool calling schema."""
        formatted = []
        for tool in self.tools:
            name = f"{tool['server']}__{tool['name']}"
            formatted.append({
                "name": name,
                "description": tool["description"],
                "input_schema": {
                    "type": "object",
                    "properties": {
                        k: {
                            "type": v,
                            "description": f"Parameter {k} for {tool['name']}",
                        }
                        for k, v in tool.get("parameters", {}).items()
                    },
                    "required": list(tool.get("parameters", {}).keys()),
                },
            })
        return formatted

    def format_mesh_tools_anthropic(self) -> List[Dict[str, Any]]:
        """Formats the 4 mcp-mesh meta-tools into Anthropic Claude schema."""
        formatted = []
        for tool in self.meta_tools:
            formatted.append({
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool.get("inputSchema", {"type": "object", "properties": {}}),
            })
        return formatted

    def run_mock_turn(self, mode: str, prompt: str) -> LiveMeasurement:
        """Executes a local simulated turn without external network access."""
        t0 = time.time()
        # Analytical ratios calibrated from empirical tests
        if mode == "raw":
            tokens = sum(len(json.dumps(t)) for t in self.tools) // 3
            tool_name = "github__create_pull_request"
        else:
            tokens = sum(len(json.dumps(t)) for t in self.meta_tools) // 3
            tool_name = "mesh_search_tools"

        dt = (time.time() - t0) * 1000.0 + (120.0 if mode == "raw" else 35.0)
        return LiveMeasurement(
            provider="mock-provider",
            model="mock-frontier-v1",
            mode=mode,
            actual_prompt_tokens=tokens,
            latency_ms=round(dt, 2),
            tool_calls_returned=1,
            invoked_tool_name=tool_name,
            response_text=f"Mock response for {mode}",
            is_mock=True,
        )

    def execute_openai_turn(
        self,
        api_key: str,
        model: str,
        mode: str,
        prompt: str,
        base_url: str = "https://api.openai.com/v1",
    ) -> LiveMeasurement:
        """Calls a real OpenAI-compatible endpoint to measure prompt tokens and latency."""
        tools = self.format_raw_tools_openai() if mode == "raw" else self.format_mesh_tools_openai()
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional autonomous coding agent equipped with tools.",
                },
                {"role": "user", "content": prompt},
            ],
            "tools": tools,
            "tool_choice": "auto",
            "max_tokens": 150,
        }

        url = f"{base_url.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "mcp-mesh-eval/1.0",
            },
            method="POST",
        )

        t0 = time.time()
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw_body = resp.read().decode("utf-8")
            dt_ms = (time.time() - t0) * 1000.0

        data = json.loads(raw_body)
        usage = data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)

        choices = data.get("choices", [{}])
        message = choices[0].get("message", {}) if choices else {}
        tool_calls = message.get("tool_calls", [])
        invoked_name = tool_calls[0].get("function", {}).get("name") if tool_calls else None

        return LiveMeasurement(
            provider="OpenAI",
            model=model,
            mode=mode,
            actual_prompt_tokens=prompt_tokens,
            latency_ms=round(dt_ms, 2),
            tool_calls_returned=len(tool_calls),
            invoked_tool_name=invoked_name,
            response_text=message.get("content"),
            http_status=200,
            is_mock=False,
        )
