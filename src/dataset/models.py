"""
Data models for benchmark tasks.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Language(str, Enum):
    """Supported programming languages."""
    PYTHON = "python"
    RUST = "rust"
    C = "c"
    CPP = "cpp"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"


class Difficulty(str, Enum):
    """Task difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXTREME = "extreme"


@dataclass
class TestCase:
    """A single test case for a benchmark task."""
    input: Any
    expected_output: Any
    timeout: float = 1.0
    weight: float = 1.0
    description: str = ""

    def __post_init__(self) -> None:
        """Validate test case."""
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.weight <= 0:
            raise ValueError("Weight must be positive")


@dataclass
class TaskMetadata:
    """Metadata for a benchmark task."""
    python_version: str = "3.11+"
    allowed_imports: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    created_at: Optional[str] = None
    author: Optional[str] = None


@dataclass
class BenchmarkTask:
    """A benchmark task for evaluating models."""
    id: str
    language: Language
    difficulty: Difficulty
    category: str
    title: str
    prompt: str
    test_cases: List[TestCase]
    reference_solution: str
    metadata: TaskMetadata = field(default_factory=TaskMetadata)

    def __post_init__(self) -> None:
        """Validate task."""
        if not self.id:
            raise ValueError("Task ID cannot be empty")
        if not self.test_cases:
            raise ValueError("Task must have at least one test case")
        if not self.prompt:
            raise ValueError("Prompt cannot be empty")

        # Convert language to enum if string
        if isinstance(self.language, str):
            self.language = Language(self.language)

        # Convert difficulty to enum if string
        if isinstance(self.difficulty, str):
            self.difficulty = Difficulty(self.difficulty)

        # Convert test cases to TestCase objects if dicts
        self.test_cases = [
            tc if isinstance(tc, TestCase) else TestCase(**tc)
            for tc in self.test_cases
        ]

        # Convert metadata to TaskMetadata if dict
        if isinstance(self.metadata, dict):
            self.metadata = TaskMetadata(**self.metadata)

    @property
    def total_weight(self) -> float:
        """Calculate total weight of all test cases."""
        return sum(tc.weight for tc in self.test_cases)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "language": self.language.value,
            "difficulty": self.difficulty.value,
            "category": self.category,
            "title": self.title,
            "prompt": self.prompt,
            "test_cases": [
                {
                    "input": tc.input,
                    "expected_output": tc.expected_output,
                    "timeout": tc.timeout,
                    "weight": tc.weight,
                    "description": tc.description
                }
                for tc in self.test_cases
            ],
            "reference_solution": self.reference_solution,
            "metadata": {
                "python_version": self.metadata.python_version,
                "allowed_imports": self.metadata.allowed_imports,
                "tags": self.metadata.tags,
                "created_at": self.metadata.created_at,
                "author": self.metadata.author
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BenchmarkTask":
        """Create task from dictionary."""
        return cls(**data)
