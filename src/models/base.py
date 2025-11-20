"""
Base classes for model providers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ModelResponse:
    """Response from a model."""
    code: str
    completion_time: float  # seconds
    tokens_used: int
    cost: float  # USD
    raw_response: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PricingInfo:
    """Pricing information for a model."""
    input_price_per_million: float  # USD per 1M input tokens
    output_price_per_million: float  # USD per 1M output tokens


class ModelProvider(ABC):
    """Abstract base class for model providers."""

    def __init__(self, name: str, model_id: str, **kwargs: Any):
        """
        Initialize model provider.

        Args:
            name: Display name for the model
            model_id: Specific model identifier
            **kwargs: Additional provider-specific configuration
        """
        self.name = name
        self.model_id = model_id
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000,
        **kwargs: Any
    ) -> ModelResponse:
        """
        Generate code from a prompt.

        Args:
            prompt: The task description
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters

        Returns:
            ModelResponse with generated code and metadata
        """
        pass

    @abstractmethod
    def get_pricing(self) -> PricingInfo:
        """
        Get pricing information for this model.

        Returns:
            PricingInfo with costs per million tokens
        """
        pass

    def calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Calculate cost for a request.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Total cost in USD
        """
        pricing = self.get_pricing()
        input_cost = (input_tokens / 1_000_000) * pricing.input_price_per_million
        output_cost = (output_tokens / 1_000_000) * pricing.output_price_per_million
        return input_cost + output_cost

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, model_id={self.model_id})"
