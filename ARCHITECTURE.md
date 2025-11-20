# Technical Architecture

## System Overview
An automated benchmark system that evaluates Python coding assistants across multiple dimensions with transparent, reproducible results.

## Tech Stack

### Core
- **Python 3.11+**: Main language
- **FastAPI**: API server for running comparisons
- **SQLite/PostgreSQL**: Store results and benchmarks
- **Docker**: Sandboxed code execution environment

### Model Integration
- **OpenAI API**: GPT-4, GPT-3.5
- **Anthropic API**: Claude models
- **Hugging Face**: Open-source models
- **Local Model Support**: Ollama, vLLM for self-hosted models

### Testing & Evaluation
- **pytest**: Test case execution
- **coverage.py**: Code coverage analysis
- **pylint/ruff**: Code quality scoring
- **radon**: Complexity metrics

### Frontend/Visualization
- **Streamlit** or **Gradio**: Interactive dashboard
- **Plotly**: Charts and visualizations
- **Markdown**: Static result reports

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Benchmark Runner                      │
│  - Orchestrates entire evaluation pipeline              │
│  - Manages concurrent model testing                     │
└────────────┬────────────────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
┌───▼────────┐   ┌───▼──────────┐
│  Dataset   │   │ Model        │
│  Manager   │   │ Providers    │
│            │   │              │
│ - Easy     │   │ - OpenAI     │
│ - Medium   │   │ - Anthropic  │
│ - Hard     │   │ - HuggingFace│
│ - Extreme  │   │ - Local      │
└────────────┘   └───┬──────────┘
                     │
             ┌───────┴────────┐
             │                │
      ┌──────▼──────┐  ┌─────▼──────┐
      │ Execution   │  │  Scoring   │
      │ Sandbox     │  │  Engine    │
      │             │  │            │
      │ - Docker    │  │ - Correct  │
      │ - Timeout   │  │ - Quality  │
      │ - Resource  │  │ - Speed    │
      │   Limits    │  │ - Style    │
      └─────────────┘  └─────┬──────┘
                             │
                      ┌──────▼──────┐
                      │   Results   │
                      │   Database  │
                      │             │
                      │ - Metrics   │
                      │ - Responses │
                      │ - Rankings  │
                      └──────┬──────┘
                             │
                      ┌──────▼──────┐
                      │ Visualization│
                      │  Dashboard  │
                      │             │
                      │ - Rankings  │
                      │ - Charts    │
                      │ - Reports   │
                      └─────────────┘
```

## Core Components

### 1. Dataset Manager
**Location**: `src/dataset/`

```python
class BenchmarkTask:
    id: str
    difficulty: Literal["easy", "medium", "hard", "extreme"]
    prompt: str
    test_cases: List[TestCase]
    reference_solution: str
    metadata: Dict[str, Any]

class TestCase:
    input: Any
    expected_output: Any
    timeout: float
    weight: float  # importance of this test case
```

**Responsibilities**:
- Load benchmark tasks from JSON/YAML
- Validate task structure
- Provide random sampling
- Track task versioning

### 2. Model Provider Interface
**Location**: `src/models/`

```python
class ModelProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> ModelResponse:
        pass

    @abstractmethod
    def get_pricing(self) -> PricingInfo:
        pass

class ModelResponse:
    code: str
    completion_time: float
    tokens_used: int
    cost: float
```

**Implementations**:
- `OpenAIProvider`
- `AnthropicProvider`
- `HuggingFaceProvider`
- `LocalModelProvider`

### 3. Execution Sandbox
**Location**: `src/execution/`

```python
class CodeExecutor:
    def execute(
        self,
        code: str,
        test_cases: List[TestCase],
        timeout: float = 5.0
    ) -> ExecutionResult:
        # Run in isolated Docker container
        # Capture stdout, stderr, exceptions
        # Measure execution time and memory
        pass

class ExecutionResult:
    passed: bool
    test_results: List[TestResult]
    execution_time: float
    memory_used: float
    errors: List[str]
```

**Security**:
- Docker isolation
- Network disabled
- Resource limits (CPU, memory, time)
- No file system access outside /tmp

### 4. Scoring Engine
**Location**: `src/scoring/`

```python
class Scorer:
    def evaluate(
        self,
        task: BenchmarkTask,
        model_response: ModelResponse,
        execution_result: ExecutionResult
    ) -> Score:
        # Calculate composite score
        pass

class Score:
    correctness: float  # 0-100 (test pass rate)
    speed: float        # 0-100 (response time vs baseline)
    quality: float      # 0-100 (code quality metrics)
    efficiency: float   # 0-100 (runtime performance)
    overall: float      # weighted average
```

**Scoring Breakdown**:
- **Correctness (40%)**: Test case pass rate
- **Speed (20%)**: Response generation time
- **Quality (25%)**: pylint score, complexity, style
- **Efficiency (15%)**: Runtime performance vs reference

### 5. Results Database
**Location**: `src/database/`

**Schema**:
```sql
CREATE TABLE benchmark_runs (
    id TEXT PRIMARY KEY,
    timestamp DATETIME,
    total_tasks INTEGER,
    completed_tasks INTEGER
);

CREATE TABLE model_results (
    id TEXT PRIMARY KEY,
    run_id TEXT,
    model_name TEXT,
    task_id TEXT,
    difficulty TEXT,
    prompt TEXT,
    generated_code TEXT,
    execution_result JSON,
    score JSON,
    response_time FLOAT,
    tokens_used INTEGER,
    cost FLOAT,
    timestamp DATETIME
);

CREATE TABLE rankings (
    model_name TEXT,
    difficulty TEXT,
    avg_score FLOAT,
    tasks_completed INTEGER,
    total_cost FLOAT,
    avg_response_time FLOAT
);
```

### 6. Visualization Dashboard
**Location**: `src/dashboard/`

**Features**:
- Overall leaderboard
- Difficulty-specific rankings
- Speed vs accuracy tradeoffs
- Cost analysis
- Task-by-task comparison
- Code diff viewer
- Export results to markdown/PDF

## Data Flow

1. **Load Tasks**: Dataset Manager loads benchmark tasks
2. **Run Models**: For each model, send prompts and collect responses
3. **Execute Code**: Run generated code in sandbox with test cases
4. **Score Results**: Evaluate correctness, quality, speed, efficiency
5. **Store Results**: Save to database
6. **Generate Rankings**: Aggregate scores across tasks
7. **Visualize**: Create dashboard and reports

## Configuration

**config.yaml**:
```yaml
models:
  - name: "gpt-4"
    provider: "openai"
    api_key: "${OPENAI_API_KEY}"
  - name: "claude-3-opus"
    provider: "anthropic"
    api_key: "${ANTHROPIC_API_KEY}"
  - name: "your-fine-tuned-model"
    provider: "local"
    endpoint: "http://localhost:8000"

execution:
  timeout: 5
  memory_limit: "512m"
  cpu_limit: 1

scoring:
  weights:
    correctness: 0.40
    speed: 0.20
    quality: 0.25
    efficiency: 0.15
```

## Extensibility

### Adding New Models
```python
class YourModelProvider(ModelProvider):
    async def generate(self, prompt: str) -> ModelResponse:
        # Your implementation
        pass
```

### Adding New Metrics
```python
class CustomScorer(Scorer):
    def evaluate(self, ...) -> Score:
        # Custom scoring logic
        pass
```

### Adding New Tasks
```json
{
  "id": "task_001",
  "difficulty": "medium",
  "prompt": "Write a function that...",
  "test_cases": [...],
  "reference_solution": "..."
}
```

## Deployment

### Local Development
```bash
pip install -r requirements.txt
python -m src.main --config config.yaml
```

### Docker
```bash
docker-compose up
```

### CI/CD
- GitHub Actions for automated benchmarking
- Weekly runs to track model improvements
- Auto-generate reports

## Future Enhancements

1. **Multi-file Projects**: Test models on larger codebases
2. **Debugging Tasks**: Given buggy code, fix it
3. **Code Review**: Evaluate review suggestions
4. **Documentation**: Generate docstrings and comments
5. **Refactoring**: Improve existing code
6. **Real-world Tasks**: Pull requests, issue resolution
7. **Human Evaluation**: Community voting on results
8. **Adversarial Testing**: Edge cases, security vulnerabilities

## Performance Targets

- Run 100 tasks across 5 models in < 30 minutes
- Support concurrent model testing
- Handle rate limits gracefully
- Cache results for re-evaluation
- Sub-second dashboard response time

## Open Source Strategy

- **License**: MIT or Apache 2.0
- **Repository**: GitHub with comprehensive README
- **Documentation**: Full API docs + tutorials
- **Community**: Accept task contributions
- **Transparency**: All results publicly visible
- **Reproducibility**: Lock dependency versions
