"""Tests for live API benchmark harness."""

import io
import json
import unittest
from unittest.mock import MagicMock, patch

from mcp_mesh_eval.engine import DEFAULT_META_TOOLS
from mcp_mesh_eval.live_harness import LiveHarness, LiveMeasurement


class TestLiveHarness(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_tools = [
            {
                "name": "create_issue",
                "server": "github",
                "description": "Create a new issue in a GitHub repository.",
                "parameters": {"owner": "string", "repo": "string", "title": "string"},
            },
            {
                "name": "query_db",
                "server": "postgres",
                "description": "Execute a SQL query.",
                "parameters": {"sql": "string"},
            },
        ]
        self.harness = LiveHarness(tools=self.sample_tools, meta_tools=DEFAULT_META_TOOLS)

    def test_format_openai_schemas(self) -> None:
        raw_openai = self.harness.format_raw_tools_openai()
        self.assertEqual(len(raw_openai), 2)
        self.assertEqual(raw_openai[0]["type"], "function")
        self.assertEqual(raw_openai[0]["function"]["name"], "github__create_issue")

        mesh_openai = self.harness.format_mesh_tools_openai()
        self.assertEqual(len(mesh_openai), len(DEFAULT_META_TOOLS))
        self.assertEqual(mesh_openai[0]["function"]["name"], "mesh_search_tools")

    def test_format_anthropic_schemas(self) -> None:
        raw_anthropic = self.harness.format_raw_tools_anthropic()
        self.assertEqual(len(raw_anthropic), 2)
        self.assertEqual(raw_anthropic[0]["name"], "github__create_issue")
        self.assertIn("input_schema", raw_anthropic[0])

        mesh_anthropic = self.harness.format_mesh_tools_anthropic()
        self.assertEqual(len(mesh_anthropic), len(DEFAULT_META_TOOLS))
        self.assertEqual(mesh_anthropic[0]["name"], "mesh_search_tools")

    def test_mock_turn_measurements(self) -> None:
        raw_meas = self.harness.run_mock_turn("raw", "open an issue")
        mesh_meas = self.harness.run_mock_turn("mesh", "open an issue")

        self.assertTrue(raw_meas.is_mock)
        self.assertTrue(mesh_meas.is_mock)
        self.assertGreater(raw_meas.actual_prompt_tokens, 0)
        self.assertGreater(mesh_meas.actual_prompt_tokens, 0)

    @patch("urllib.request.urlopen")
    def test_execute_openai_turn_mocked_http(self, mock_urlopen: MagicMock) -> None:
        mock_response_data = {
            "id": "chatcmpl-test123",
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [
                            {
                                "id": "call_abc",
                                "type": "function",
                                "function": {
                                    "name": "mesh_search_tools",
                                    "arguments": '{"query":"github issue"}',
                                },
                            }
                        ],
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 527,
                "completion_tokens": 22,
                "total_tokens": 549,
            },
        }

        mock_context = MagicMock()
        mock_context.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_context.__enter__.return_value = mock_context
        mock_urlopen.return_value = mock_context

        meas = self.harness.execute_openai_turn(
            api_key="test-key",
            model="gpt-4o",
            mode="mesh",
            prompt="Find a tool to open a github issue",
        )

        self.assertEqual(meas.actual_prompt_tokens, 527)
        self.assertEqual(meas.invoked_tool_name, "mesh_search_tools")
        self.assertEqual(meas.provider, "OpenAI")
        self.assertFalse(meas.is_mock)
