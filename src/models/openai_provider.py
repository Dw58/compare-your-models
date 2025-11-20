"""
OpenAI model provider implementation.
"""
import os
import time
from typing import Any

from openai import AsyncOpenAI

from .base import ModelProvider, ModelResponse, PricingInfo


class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models (GPT-4, GPT-3.5, etc.)"""

    # Pricing per 1M tokens (USD)
    PRICING = {
        "gpt-4-turbo-preview": PricingInfo(10.00, 30.00),
        "gpt-4-turbo": PricingInfo(10.00, 30.00),
        "gpt-4": PricingInfo(30.00, 60.00),
        "gpt-3.5-turbo": PricingInfo(0.50, 1.50),
        "gpt-3.5-turbo-16k": PricingInfo(3.00, 4.00),
    }

    def __init__(
        self,
        name: str,
        model_id: str,
        api_key: str | None = None,
        **kwargs: Any
    ):
        """
        Initialize OpenAI provider.

        Args:
            name: Display name for the model
            model_id: OpenAI model identifier
            api_key: API key (defaults to OPENAI_API_KEY env var)
            **kwargs: Additional configuration
        """
        super().__init__(name, model_id, **kwargs)

        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY env var.")

        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs: Any
    ) -> ModelResponse:
        """
        Generate code from OpenAI model.

        Args:
            prompt: The task description
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional OpenAI parameters

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
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            completion_time = time.time() - start_time

            # Extract code from response
            code = response.choices[0].message.content or ""
            code = self._extract_code(code)

            # Calculate tokens and cost
            input_tokens = response.usage.prompt_tokens if response.usage else 0
            output_tokens = response.usage.completion_tokens if response.usage else 0
            cost = self.calculate_cost(input_tokens, output_tokens)

            return ModelResponse(
                code=code,
                completion_time=completion_time,
                tokens_used=input_tokens + output_tokens,
                cost=cost,
                raw_response=response.choices[0].message.content,
                metadata={
                    "model": response.model,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            )

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}") from e

    def get_pricing(self) -> PricingInfo:
        """Get pricing info for this model."""
        # Try to find exact match or base model
        for model_key in [self.model_id, self.model_id.split('-')[0:2]]:
            if isinstance(model_key, list):
                model_key = '-'.join(model_key)
            if model_key in self.PRICING:
                return self.PRICING[model_key]

        # Default to GPT-4 pricing if unknown
        return self.PRICING["gpt-4"]

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
