"""LLM client for Claude Sonnet API calls."""

import json
import logging
import time
from typing import Optional

import anthropic

logger = logging.getLogger(__name__)


class CostTracker:
    """Tracks API costs across the pipeline run."""

    # Claude Sonnet 4 pricing (per 1M tokens)
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
        "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    }
    DEFAULT_PRICING = {"input": 3.0, "output": 15.0}

    def __init__(self):
        self.calls = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0

    def record(self, caller: str, input_tokens: int, output_tokens: int,
               model: str = "", duration: float = 0.0):
        pricing = self.PRICING.get(model, self.DEFAULT_PRICING)
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

        self.calls.append({
            "caller": caller,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "duration": duration,
            "timestamp": time.time(),
        })
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost

    def get_report(self) -> dict:
        return {
            "total_calls": len(self.calls),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 4),
            "calls": self.calls,
        }


class LLMClient:
    """Client for Claude Sonnet API with cost tracking."""

    def __init__(self, config: dict, cost_tracker: Optional[CostTracker] = None):
        self.config = config.get("llm", {})
        self.api_key = self.config.get("api_key", "")
        self.model = self.config.get("model", "claude-sonnet-4-20250514")
        self.timeout = self.config.get("timeout", 300)
        self.cost_tracker = cost_tracker or CostTracker()

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required. Set it in providers.yaml or as an environment variable.")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    async def analyze(self, system_prompt: str, user_prompt: str,
                      caller: str = "unknown", max_tokens: int = 4096,
                      response_format: str = "json") -> dict | str:
        """Send a prompt to Claude and return the response."""
        start = time.time()

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )

            duration = time.time() - start
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens

            self.cost_tracker.record(
                caller=caller,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model=self.model,
                duration=duration,
            )

            response_text = message.content[0].text

            if response_format == "json":
                # Try to extract JSON from the response
                return self._parse_json(response_text)

            return response_text

        except anthropic.APIError as e:
            logger.error(f"API error in {caller}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in {caller}: {e}")
            raise

    def _parse_json(self, text: str) -> dict | list:
        """Extract JSON from LLM response text."""
        # Try direct parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        import re
        json_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try finding JSON array or object
        for start_char, end_char in [('[', ']'), ('{', '}')]:
            start_idx = text.find(start_char)
            end_idx = text.rfind(end_char)
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx + 1])
                except json.JSONDecodeError:
                    continue

        logger.warning(f"Could not parse JSON from response, returning raw text")
        return {"raw_response": text}
