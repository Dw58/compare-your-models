"""
Anthropic model provider implementation.
"""
import os
import time
from typing import Any

from anthropic import AsyncAnthropic

from .base import ModelProvider, ModelResponse, PricingInfo


class AnthropicProvider(ModelProvider):
    """Provider for Anthropic models (Claude)"""

    # Pricing per 1M tokens (USD)
    PRICING = {
        "claude-3-opus-20240229": PricingInfo(15.00, 75.00),
        "claude-3-sonnet-20240229": PricingInfo(3.00, 15.00),
        "claude-3-5-sonnet-20240620": PricingInfo(3.00, 15.00),
        "claude-3-5-sonnet-20241022": PricingInfo(3.00, 15.00),
        "claude-3-haiku-20240307": PricingInfo(0.25, 1.25),
        "claude-2.1": PricingInfo(8.00, 24.00),
        "claude-2.0": PricingInfo(8.00, 24.00),
    }

    def __init__(
        self,
        name: str,
        model_id: str,
        api_key: str | None = None,
        **kwargs: Any
    ):
        """
        Initialize Anthropic provider.

        Args:
            name: Display name for the model
            model_id: Anthropic model identifier
            api_key: API key (defaults to ANTHROPIC_API_KEY env var)
            **kwargs: Additional configuration
        """
        super().__init__(name, model_id, **kwargs)

        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY env var.")

        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs: Any
    ) -> ModelResponse:
        """
        Generate code from Anthropic model.

        Args:
            prompt: The task description
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional Anthropic parameters

        Returns:
            ModelResponse with generated code and metadata
        """
        # Build the system prompt
        system_prompt = """You are an expert Python programmer. Generate clean, efficient, and well-documented Python code.

IMPORTANT:
- Only output the Python function code requested
- Do NOT include explanations, markdown formatting, or code blocks
- Do NOT include example usage or test cases
- Just write the pure Python function implementation
"""

        start_time = time.time()

        try:
            response = await self.client.messages.create(
                model=self.model_id,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )

            completion_time = time.time() - start_time

            # Extract code from response
            code = ""
            if response.content:
                # Anthropic returns list of content blocks
                for block in response.content:
                    if hasattr(block, 'text'):
                        code += block.text

            code = self._extract_code(code)

            # Calculate tokens and cost
            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0
            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                code=code,
                completion_time=completion_time,
                tokens_used=input_tokens + output_tokens,
                cost=cost,
                raw_response=code,
                metadata={
                    "model": response.model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "stop_reason": response.stop_reason
                }
            )

        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}") from e

    def get_pricing(self) -> PricingInfo:
        """Get pricing info for this model."""
        return self.PRICING.get(
            self.model_id,
            self.PRICING["claude-3-sonnet-20240229"]  # Default
        )

    @staticmethod
    def _extract_code(response: str) -> str:
        """
        Extract Python code from response, removing markdown formatting.

        Args:
            response: Raw response from model

        Returns:
            Clean Python code
        """
        code = response.strip()

        # Remove markdown code blocks
        if code.startswith("```python"):
            code = code[9:]  # Remove ```python
        elif code.startswith("```"):
            code = code[3:]  # Remove ```

        if code.endswith("```"):
            code = code[:-3]  # Remove trailing ```

        return code.strip()
