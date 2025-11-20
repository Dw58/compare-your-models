"""
Scoring system for evaluating model performance.
"""
from dataclasses import dataclass
from typing import Optional

from src.dataset.models import BenchmarkTask
from src.execution.executor import ExecutionResult
from src.models.base import ModelResponse


@dataclass
class Score:
    """Composite score for a model's performance on a task."""
    correctness: float  # 0-100: percentage of tests passed
    speed: float  # 0-100: response generation speed score
    quality: float  # 0-100: code quality score (basic for now)
    efficiency: float  # 0-100: runtime efficiency score
    overall: float  # 0-100: weighted composite score

    # Metadata
    tests_passed: int = 0
    tests_total: int = 0
    response_time: float = 0.0
    execution_time: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0


class Scorer:
    """Evaluates model performance across multiple dimensions."""

    def __init__(
        self,
        correctness_weight: float = 0.40,
        speed_weight: float = 0.20,
        quality_weight: float = 0.25,
        efficiency_weight: float = 0.15
    ):
        """
        Initialize scorer with custom weights.

        Args:
            correctness_weight: Weight for correctness score (0-1)
            speed_weight: Weight for speed score (0-1)
            quality_weight: Weight for quality score (0-1)
            efficiency_weight: Weight for efficiency score (0-1)
        """
        total = correctness_weight + speed_weight + quality_weight + efficiency_weight
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        self.correctness_weight = correctness_weight
        self.speed_weight = speed_weight
        self.quality_weight = quality_weight
        self.efficiency_weight = efficiency_weight

    def evaluate(
        self,
        task: BenchmarkTask,
        model_response: ModelResponse,
        execution_result: ExecutionResult,
        reference_time: Optional[float] = None
    ) -> Score:
        """
        Evaluate a model's performance on a task.

        Args:
            task: The benchmark task
            model_response: Model's response with generated code
            execution_result: Result of executing the code
            reference_time: Optional reference execution time for comparison

        Returns:
            Composite score across all dimensions
        """
        # Calculate individual scores
        correctness = self._score_correctness(task, execution_result)
        speed = self._score_speed(model_response, task)
        quality = self._score_quality(model_response)
        efficiency = self._score_efficiency(execution_result, reference_time)

        # Calculate weighted overall score
        overall = (
            correctness * self.correctness_weight +
            speed * self.speed_weight +
            quality * self.quality_weight +
            efficiency * self.efficiency_weight
        )

        return Score(
            correctness=correctness,
            speed=speed,
            quality=quality,
            efficiency=efficiency,
            overall=overall,
            tests_passed=execution_result.passed_tests,
            tests_total=execution_result.total_tests,
            response_time=model_response.completion_time,
            execution_time=execution_result.total_execution_time,
            tokens_used=model_response.tokens_used,
            cost=model_response.cost
        )

    def _score_correctness(
        self,
        task: BenchmarkTask,
        execution_result: ExecutionResult
    ) -> float:
        """
        Score based on test case pass rate (weighted).

        Args:
            task: The benchmark task
            execution_result: Execution results

        Returns:
            Score from 0-100
        """
        if execution_result.total_tests == 0:
            return 0.0

        # Calculate weighted pass rate
        total_weight = task.total_weight
        passed_weight = 0.0

        for i, test_result in enumerate(execution_result.test_results):
            if test_result.passed and i < len(task.test_cases):
                passed_weight += task.test_cases[i].weight

        return (passed_weight / total_weight) * 100.0 if total_weight > 0 else 0.0

    def _score_speed(
        self,
        model_response: ModelResponse,
        task: BenchmarkTask
    ) -> float:
        """
        Score based on response generation time.

        Args:
            model_response: Model's response
            task: The benchmark task

        Returns:
            Score from 0-100 (lower time = higher score)
        """
        # Define baseline times for different difficulties
        baselines = {
            "easy": 5.0,
            "medium": 15.0,
            "hard": 45.0,
            "extreme": 90.0
        }

        baseline = baselines.get(task.difficulty.value, 15.0)
        response_time = model_response.completion_time

        # Score: 100 at 0s, 50 at baseline, asymptotic to 0
        if response_time <= 0:
            return 100.0

        score = 100.0 * (baseline / (baseline + response_time))
        return max(0.0, min(100.0, score))

    def _score_quality(self, model_response: ModelResponse) -> float:
        """
        Score code quality (basic heuristics for now).

        Args:
            model_response: Model's response

        Returns:
            Score from 0-100
        """
        code = model_response.code
        score = 0.0

        # Basic quality checks (can be expanded with pylint later)

        # Has docstring
        if '"""' in code or "'''" in code:
            score += 20.0

        # Has type hints
        if '->' in code and ':' in code:
            score += 20.0

        # Not too short (likely incomplete)
        if len(code) > 50:
            score += 20.0

        # Not too long (likely over-engineered)
        if len(code) < 1000:
            score += 20.0

        # Has proper indentation
        lines = code.split('\n')
        if any(line.startswith('    ') for line in lines):
            score += 20.0

        return min(100.0, score)

    def _score_efficiency(
        self,
        execution_result: ExecutionResult,
        reference_time: Optional[float] = None
    ) -> float:
        """
        Score runtime efficiency.

        Args:
            execution_result: Execution results
            reference_time: Reference execution time

        Returns:
            Score from 0-100
        """
        if not execution_result.passed:
            return 0.0

        # If no reference time, give neutral score
        if reference_time is None or reference_time <= 0:
            return 50.0

        actual_time = execution_result.total_execution_time

        if actual_time <= 0:
            return 100.0

        # Score: 100 if same as reference, scales down if slower
        ratio = reference_time / actual_time

        if ratio >= 1.0:
            # Faster or equal to reference
            score = 100.0
        else:
            # Slower than reference
            score = 100.0 * ratio

        return max(0.0, min(100.0, score))
