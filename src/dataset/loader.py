"""
Dataset loader for benchmark tasks.
"""
import json
import random
from pathlib import Path
from typing import List, Optional

from .models import BenchmarkTask, Difficulty, Language


class DatasetLoader:
    """Loads and manages benchmark tasks."""

    def __init__(self, tasks_dir: str = "benchmarks/tasks"):
        """
        Initialize dataset loader.

        Args:
            tasks_dir: Path to directory containing task JSON files
        """
        self.tasks_dir = Path(tasks_dir)
        self._tasks_cache: Optional[List[BenchmarkTask]] = None

    def load_all_tasks(self, force_reload: bool = False) -> List[BenchmarkTask]:
        """
        Load all benchmark tasks from disk.

        Args:
            force_reload: If True, reload from disk even if cached

        Returns:
            List of all benchmark tasks
        """
        if self._tasks_cache and not force_reload:
            return self._tasks_cache

        tasks = []

        # Load tasks from all difficulty directories
        for difficulty in Difficulty:
            difficulty_dir = self.tasks_dir / difficulty.value
            if not difficulty_dir.exists():
                continue

            for task_file in difficulty_dir.glob("*.json"):
                try:
                    task = self._load_task_file(task_file)
                    tasks.append(task)
                except Exception as e:
                    print(f"Warning: Failed to load {task_file}: {e}")

        self._tasks_cache = tasks
        return tasks

    def load_tasks_by_difficulty(
        self,
        difficulty: Difficulty | str,
        num_tasks: Optional[int] = None,
        shuffle: bool = False,
        language: Optional[Language | str] = None
    ) -> List[BenchmarkTask]:
        """
        Load tasks filtered by difficulty and optionally language.

        Args:
            difficulty: Difficulty level to filter by
            num_tasks: Maximum number of tasks to return
            shuffle: If True, randomize task order
            language: Optional language filter

        Returns:
            List of tasks matching the criteria
        """
        if isinstance(difficulty, str):
            difficulty = Difficulty(difficulty)
        if isinstance(language, str):
            language = Language(language)

        all_tasks = self.load_all_tasks()
        filtered_tasks = [t for t in all_tasks if t.difficulty == difficulty]

        # Filter by language if specified
        if language:
            filtered_tasks = [t for t in filtered_tasks if t.language == language]

        if shuffle:
            filtered_tasks = random.sample(
                filtered_tasks,
                k=min(len(filtered_tasks), num_tasks or len(filtered_tasks))
            )
        elif num_tasks:
            filtered_tasks = filtered_tasks[:num_tasks]

        return filtered_tasks

    def load_tasks_by_language(
        self,
        language: Language | str,
        num_tasks: Optional[int] = None,
        shuffle: bool = False
    ) -> List[BenchmarkTask]:
        """
        Load tasks filtered by programming language.

        Args:
            language: Programming language to filter by
            num_tasks: Maximum number of tasks to return
            shuffle: If True, randomize task order

        Returns:
            List of tasks for the specified language
        """
        if isinstance(language, str):
            language = Language(language)

        all_tasks = self.load_all_tasks()
        filtered_tasks = [t for t in all_tasks if t.language == language]

        if shuffle:
            filtered_tasks = random.sample(
                filtered_tasks,
                k=min(len(filtered_tasks), num_tasks or len(filtered_tasks))
            )
        elif num_tasks:
            filtered_tasks = filtered_tasks[:num_tasks]

        return filtered_tasks

    def load_task_by_id(self, task_id: str) -> Optional[BenchmarkTask]:
        """
        Load a specific task by ID.

        Args:
            task_id: Task identifier

        Returns:
            BenchmarkTask if found, None otherwise
        """
        all_tasks = self.load_all_tasks()
        for task in all_tasks:
            if task.id == task_id:
                return task
        return None

    def get_task_count(self) -> dict[str, int]:
        """
        Get count of tasks by difficulty and language.

        Returns:
            Dictionary with task counts by difficulty and language
        """
        all_tasks = self.load_all_tasks()

        counts = {
            'total': len(all_tasks),
            'by_difficulty': {d.value: 0 for d in Difficulty},
            'by_language': {l.value: 0 for l in Language}
        }

        for task in all_tasks:
            counts['by_difficulty'][task.difficulty.value] += 1
            counts['by_language'][task.language.value] += 1

        return counts

    @staticmethod
    def _load_task_file(file_path: Path) -> BenchmarkTask:
        """
        Load a task from a JSON file.

        Args:
            file_path: Path to task JSON file

        Returns:
            BenchmarkTask object
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        return BenchmarkTask.from_dict(data)

    def validate_task(self, task: BenchmarkTask) -> List[str]:
        """
        Validate a benchmark task.

        Args:
            task: Task to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not task.id:
            errors.append("Task ID is required")

        if not task.prompt:
            errors.append("Task prompt is required")

        if not task.test_cases:
            errors.append("At least one test case is required")

        if not task.reference_solution:
            errors.append("Reference solution is required")

        # Validate test cases
        for i, test_case in enumerate(task.test_cases):
            if test_case.timeout <= 0:
                errors.append(f"Test case {i}: timeout must be positive")
            if test_case.weight <= 0:
                errors.append(f"Test case {i}: weight must be positive")

        return errors
