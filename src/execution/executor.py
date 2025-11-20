"""
Code execution sandbox for running and testing generated code.
"""
import asyncio
import json
import sys
import tempfile
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List

from src.dataset.models import TestCase


@dataclass
class TestResult:
    """Result of a single test case."""
    passed: bool
    input_data: Any
    expected_output: Any
    actual_output: Any | None
    error: str | None = None
    execution_time: float = 0.0


@dataclass
class ExecutionResult:
    """Result of executing code with multiple test cases."""
    passed: bool
    test_results: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_execution_time: float
    errors: List[str]


class CodeExecutor:
    """Executes Python code in a sandboxed environment."""

    def __init__(self, timeout: float = 5.0):
        """
        Initialize code executor.

        Args:
            timeout: Maximum execution time per test case (seconds)
        """
        self.timeout = timeout

    async def execute(
        self,
        code: str,
        test_cases: List[TestCase]
    ) -> ExecutionResult:
        """
        Execute code against multiple test cases.

        Args:
            code: Python code to execute
            test_cases: List of test cases to run

        Returns:
            ExecutionResult with pass/fail status for each test
        """
        test_results = []
        errors = []
        total_time = 0.0

        for test_case in test_cases:
            try:
                result = await self._run_test_case(code, test_case)
                test_results.append(result)
                total_time += result.execution_time
            except Exception as e:
                errors.append(f"Test execution error: {str(e)}")
                test_results.append(TestResult(
                    passed=False,
                    input_data=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error=str(e),
                    execution_time=0.0
                ))

        passed_tests = sum(1 for r in test_results if r.passed)
        failed_tests = len(test_results) - passed_tests

        return ExecutionResult(
            passed=failed_tests == 0,
            test_results=test_results,
            total_tests=len(test_results),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            total_execution_time=total_time,
            errors=errors
        )

    async def _run_test_case(
        self,
        code: str,
        test_case: TestCase
    ) -> TestResult:
        """
        Run a single test case.

        Args:
            code: Python code containing the function
            test_case: Test case to execute

        Returns:
            TestResult with pass/fail status
        """
        # Create a temporary file with the code
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            test_script = self._generate_test_script(code, test_case)
            f.write(test_script)
            script_path = f.name

        try:
            # Run the test script
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                script_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=test_case.timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return TestResult(
                    passed=False,
                    input_data=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error=f"Timeout: exceeded {test_case.timeout}s",
                    execution_time=test_case.timeout
                )

            # Parse result
            if process.returncode == 0:
                result_data = json.loads(stdout.decode())
                return TestResult(
                    passed=result_data['passed'],
                    input_data=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output=result_data.get('actual_output'),
                    error=result_data.get('error'),
                    execution_time=result_data.get('execution_time', 0.0)
                )
            else:
                error_msg = stderr.decode() if stderr else "Unknown error"
                return TestResult(
                    passed=False,
                    input_data=test_case.input,
                    expected_output=test_case.expected_output,
                    actual_output=None,
                    error=error_msg,
                    execution_time=0.0
                )

        finally:
            # Clean up temporary file
            Path(script_path).unlink(missing_ok=True)

    @staticmethod
    def _generate_test_script(code: str, test_case: TestCase) -> str:
        """
        Generate a test script that runs the code and reports results.

        Args:
            code: Python code containing the function
            test_case: Test case to execute

        Returns:
            Complete Python script as string
        """
        return f'''
import json
import time
import traceback
from typing import List, Dict, Tuple, Optional, Any

# User code
{code}

# Test execution
def run_test():
    try:
        start_time = time.time()

        # Extract function name from code (simple heuristic)
        import re
        match = re.search(r'def\\s+(\\w+)\\s*\\(', {repr(code)})
        if not match:
            return {{
                'passed': False,
                'error': 'Could not find function definition',
                'execution_time': 0.0
            }}

        func_name = match.group(1)
        func = globals()[func_name]

        # Prepare input
        test_input = {repr(test_case.input)}
        expected_output = {repr(test_case.expected_output)}

        # Call function
        if isinstance(test_input, dict):
            actual_output = func(**test_input)
        elif isinstance(test_input, list):
            actual_output = func(*test_input)
        else:
            actual_output = func(test_input)

        execution_time = time.time() - start_time

        # Compare output
        passed = actual_output == expected_output

        return {{
            'passed': passed,
            'actual_output': actual_output,
            'expected_output': expected_output,
            'execution_time': execution_time
        }}

    except Exception as e:
        return {{
            'passed': False,
            'error': str(e) + '\\n' + traceback.format_exc(),
            'execution_time': time.time() - start_time if 'start_time' in locals() else 0.0
        }}

if __name__ == '__main__':
    result = run_test()
    print(json.dumps(result))
'''
