"""
Main entry point for Python Model Benchmark.
"""
import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, List

import click
import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from src.dataset.loader import DatasetLoader
from src.dataset.models import Difficulty
from src.execution.executor import CodeExecutor
from src.models.openai_provider import OpenAIProvider
from src.models.anthropic_provider import AnthropicProvider
from src.models.base import ModelProvider
from src.scoring.scorer import Scorer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def initialize_models(config: dict, model_filter: Optional[str] = None) -> List[ModelProvider]:
    """Initialize model providers from config."""
    models = []

    for model_config in config.get('models', []):
        # Skip disabled models
        if not model_config.get('enabled', True):
            continue

        # Filter by name if specified
        if model_filter and model_config['name'] != model_filter:
            continue

        name = model_config['name']
        provider = model_config['provider']
        model_id = model_config['model_id']

        try:
            if provider == 'openai':
                api_key = os.getenv(model_config.get('api_key_env', 'OPENAI_API_KEY'))
                models.append(OpenAIProvider(name, model_id, api_key))
            elif provider == 'anthropic':
                api_key = os.getenv(model_config.get('api_key_env', 'ANTHROPIC_API_KEY'))
                models.append(AnthropicProvider(name, model_id, api_key))
            else:
                logger.warning(f"Unknown provider '{provider}' for model '{name}'")

        except Exception as e:
            logger.error(f"Failed to initialize {name}: {e}")

    return models


async def run_benchmark(
    config: dict,
    difficulty: Optional[str] = None,
    model_name: Optional[str] = None,
    num_tasks: Optional[int] = None,
    language: Optional[str] = None
) -> None:
    """
    Run the benchmark suite.

    Args:
        config: Configuration dictionary
        difficulty: Optional difficulty filter (easy/medium/hard/extreme)
        model_name: Optional model name filter
        num_tasks: Optional number of tasks to run per difficulty
        language: Optional language filter (python/rust/c/cpp/etc.)
    """
    lang_display = language.upper() if language else "Multi-Language"
    console.print(f"\n[bold cyan]🚀 {lang_display} Model Benchmark[/bold cyan]")
    console.print("=" * 60)

    # Load tasks
    console.print("\n[cyan]Loading benchmark tasks...[/cyan]")
    loader = DatasetLoader()

    if difficulty:
        tasks = loader.load_tasks_by_difficulty(difficulty, num_tasks, language=language)
        lang_str = f"{language} " if language else ""
        console.print(f"Loaded {len(tasks)} {lang_str}{difficulty} tasks")
    elif language:
        tasks = loader.load_tasks_by_language(language, num_tasks)
        console.print(f"Loaded {len(tasks)} {language} tasks")
    else:
        tasks = loader.load_all_tasks()
        if num_tasks:
            tasks = tasks[:num_tasks]
        console.print(f"Loaded {len(tasks)} total tasks")

    if not tasks:
        console.print("[yellow]No tasks found! Add tasks to benchmarks/tasks/[/yellow]")
        return

    # Initialize models
    console.print("\n[cyan]Initializing models...[/cyan]")
    models = initialize_models(config, model_name)

    if not models:
        console.print("[red]No models configured! Check config.yaml and API keys[/red]")
        return

    for model in models:
        console.print(f"  ✓ {model.name}")

    # Initialize executor and scorer
    executor = CodeExecutor(timeout=config.get('execution', {}).get('timeout', 5.0))

    weights = config.get('scoring', {}).get('weights', {
        'correctness': 0.40,
        'speed': 0.20,
        'quality': 0.25,
        'efficiency': 0.15
    })
    scorer = Scorer(
        correctness_weight=weights.get('correctness', 0.40),
        speed_weight=weights.get('speed', 0.20),
        quality_weight=weights.get('quality', 0.25),
        efficiency_weight=weights.get('efficiency', 0.15)
    )

    # Run benchmark
    console.print("\n[cyan]Running benchmark...[/cyan]")
    results = []

    for model in models:
        console.print(f"\n[bold]Testing {model.name}[/bold]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task_progress = progress.add_task(
                f"Running {len(tasks)} tasks...",
                total=len(tasks)
            )

            for task in tasks:
                try:
                    # Generate code
                    response = await model.generate(task.prompt)

                    # Execute and test
                    execution_result = await executor.execute(
                        response.code,
                        task.test_cases
                    )

                    # Score
                    score = scorer.evaluate(task, response, execution_result)

                    results.append({
                        'model': model.name,
                        'task_id': task.id,
                        'difficulty': task.difficulty.value,
                        'score': score,
                        'passed': execution_result.passed
                    })

                except Exception as e:
                    logger.error(f"Error testing {model.name} on {task.id}: {e}")

                progress.update(task_progress, advance=1)

    # Display results
    console.print("\n[bold green]✓ Benchmark Complete![/bold green]")
    display_results(results)


def display_results(results: list) -> None:
    """Display benchmark results in a nice table."""
    if not results:
        console.print("[yellow]No results to display[/yellow]")
        return

    # Group by model
    model_scores = {}
    for result in results:
        model = result['model']
        if model not in model_scores:
            model_scores[model] = []
        model_scores[model].append(result['score'])

    # Create results table
    table = Table(title="Benchmark Results")
    table.add_column("Model", style="cyan", no_wrap=True)
    table.add_column("Tasks", justify="right")
    table.add_column("Passed", justify="right", style="green")
    table.add_column("Avg Score", justify="right", style="bold")
    table.add_column("Correctness", justify="right")
    table.add_column("Speed", justify="right")
    table.add_column("Quality", justify="right")
    table.add_column("Cost ($)", justify="right")

    for model, scores in model_scores.items():
        total_tasks = len(scores)
        passed_tasks = sum(1 for r in results if r['model'] == model and r['passed'])
        avg_overall = sum(s.overall for s in scores) / len(scores)
        avg_correctness = sum(s.correctness for s in scores) / len(scores)
        avg_speed = sum(s.speed for s in scores) / len(scores)
        avg_quality = sum(s.quality for s in scores) / len(scores)
        total_cost = sum(s.cost for s in scores)

        table.add_row(
            model,
            str(total_tasks),
            f"{passed_tasks}/{total_tasks}",
            f"{avg_overall:.1f}",
            f"{avg_correctness:.1f}",
            f"{avg_speed:.1f}",
            f"{avg_quality:.1f}",
            f"{total_cost:.4f}"
        )

    console.print("\n")
    console.print(table)


@click.command()
@click.option(
    '--config',
    default='config.yaml',
    help='Path to configuration file',
    type=click.Path(exists=True)
)
@click.option(
    '--language',
    type=click.Choice(['python', 'rust', 'c', 'cpp', 'javascript', 'typescript', 'go', 'java']),
    help='Filter tasks by programming language'
)
@click.option(
    '--difficulty',
    type=click.Choice(['easy', 'medium', 'hard', 'extreme']),
    help='Run only tasks of specific difficulty'
)
@click.option(
    '--model',
    help='Run benchmark for specific model only'
)
@click.option(
    '--num-tasks',
    type=int,
    help='Number of tasks to run per difficulty tier'
)
@click.option(
    '--verbose',
    is_flag=True,
    help='Enable verbose logging'
)
def main(
    config: str,
    language: Optional[str],
    difficulty: Optional[str],
    model: Optional[str],
    num_tasks: Optional[int],
    verbose: bool
) -> None:
    """
    Compare Your Models - Evaluate AI coding assistants across multiple languages.

    Examples:
        python -m src.main --language python
        python -m src.main --language rust --difficulty easy
        python -m src.main --model gpt-4-turbo --language python
        python -m src.main --num-tasks 5 --verbose
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    try:
        cfg = load_config(config)
    except Exception as e:
        console.print(f"[bold red]Error loading config:[/bold red] {e}")
        return

    # Run benchmark
    try:
        asyncio.run(run_benchmark(
            config=cfg,
            difficulty=difficulty,
            model_name=model,
            num_tasks=num_tasks,
            language=language
        ))
    except KeyboardInterrupt:
        console.print("\n[yellow]Benchmark interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        logger.exception("Benchmark failed")


if __name__ == "__main__":
    main()
