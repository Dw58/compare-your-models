# Compare Your Models

> **Open-source benchmark tool for comparing AI coding assistants across multiple programming languages**

Transparently evaluate and compare AI models (GPT-4, Claude, custom fine-tuned models) on real coding tasks. Start with Python, expand to Rust, C, C++, JavaScript, and more.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

---

## Why This Exists

Most AI coding assistants claim to be "the best" without transparent, reproducible benchmarks. **Compare Your Models** levels the playing field by:

- ✅ **Open-source benchmarks**: Anyone can verify results
- ✅ **Multi-language support**: Python (live), Rust, C, C++, JS/TS, Go, Java (coming soon)
- ✅ **Comprehensive evaluation**: Tests correctness, speed, code quality, AND efficiency
- ✅ **Real-world tasks**: Practical coding problems, not toy examples
- ✅ **Reproducible results**: Versioned tasks, locked dependencies, deterministic scoring

## Quick Start

```bash
# Clone & setup
git clone https://github.com/YOUR_USERNAME/compare-your-models.git
cd compare-your-models
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Add API keys
cp .env.example .env
# Edit .env with your API keys

# Run benchmark
python -m src.main --language python --difficulty easy
```

## Supported Languages

| Language | Status | Tasks Available |
|----------|--------|-----------------|
| Python | ✅ Live | 3+ (growing) |
| Rust | 🚧 Coming Soon | 0 |
| C | 🚧 Coming Soon | 0 |
| C++ | 🚧 Coming Soon | 0 |
| JavaScript | 🚧 Coming Soon | 0 |
| TypeScript | 🚧 Coming Soon | 0 |
| Go | 🚧 Coming Soon | 0 |
| Java | 🚧 Coming Soon | 0 |

**Want to add a language?** Contributions welcome! See [CONTRIBUTING.md](#contributing)

## Evaluation Metrics

### 1. Correctness (40%)
- Test case pass rate
- Edge case handling
- Error handling

### 2. Speed (20%)
- Response generation time
- Comparison against baseline

### 3. Code Quality (25%)
- Linting score
- Cyclomatic complexity
- Type hints usage
- Documentation completeness

### 4. Efficiency (15%)
- Runtime performance
- Memory usage
- Big-O optimality

## Benchmark Tasks by Language

### Python (Current Focus)

Tasks organized by difficulty:

**Easy (3+ tasks)**: String manipulation, list operations, basic file I/O
**Medium (1+ tasks)**: Algorithms, OOP, error handling
**Hard (coming soon)**: Graph algorithms, async patterns, design patterns
**Extreme (coming soon)**: Advanced data structures, system design, optimization

Target: 150+ Python tasks

### Other Languages (Roadmap)

Each language will follow the same structure:
- 50+ Easy tasks
- 50+ Medium tasks
- 30+ Hard tasks
- 20+ Extreme tasks

## Usage Examples

```bash
# Run all Python benchmarks
python -m src.main --language python

# Compare models on specific difficulty
python -m src.main --language python --difficulty easy

# Test specific model
python -m src.main --language python --model gpt-4-turbo

# Limit number of tasks
python -m src.main --language python --num-tasks 5

# Future: Rust benchmarks
python -m src.main --language rust --difficulty medium
```

## Sample Results

```
🚀 PYTHON Model Benchmark
============================================================

Benchmark Results
┏━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
┃ Model         ┃ Tasks ┃ Passed ┃ Avg Score ┃ Correctness ┃ Speed ┃ Quality ┃ Cost ($) ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
│ gpt-3.5-turbo │     3 │    3/3 │    85.1 │  100.0 │  88.1 │    80.0 │ 0.0004 │
│ gpt-4-turbo   │     3 │    3/3 │    80.7 │  100.0 │  66.2 │    80.0 │ 0.0078 │
│ claude-3-opus │     3 │    3/3 │    80.2 │  100.0 │  63.5 │    80.0 │ 0.0188 │
└───────────────┴───────┴────────┴─────────┴────────┴───────┴─────────┴────────┘
```

## Project Structure

```
compare-your-models/
├── benchmarks/
│   └── tasks/
│       ├── easy/          # Easy difficulty tasks
│       ├── medium/        # Medium difficulty tasks
│       ├── hard/          # Hard difficulty tasks
│       └── extreme/       # Extremely hard tasks
├── src/
│   ├── dataset/           # Task management & loading
│   ├── models/            # Model provider integrations
│   ├── execution/         # Sandboxed code execution
│   ├── scoring/           # Evaluation metrics
│   ├── database/          # Results storage
│   └── dashboard/         # Visualization
├── docs/
│   ├── PROJECT_VISION.md
│   ├── ARCHITECTURE.md
│   └── DATASET_STRUCTURE.md
└── tests/                 # Unit tests
```

## Adding Your Model

### Option 1: API-based Model

```yaml
# config.yaml
models:
  - name: "my-python-expert"
    provider: "local"
    endpoint: "http://localhost:8000/v1/completions"
    api_key_env: "MY_MODEL_API_KEY"
    enabled: true
```

### Option 2: Custom Provider

```python
# src/models/my_provider.py
from src.models.base import ModelProvider

class MyModelProvider(ModelProvider):
    async def generate(self, prompt: str) -> ModelResponse:
        # Your implementation
        pass
```

## Contributing

We welcome contributions!

### Add Benchmark Tasks

1. Choose a language and difficulty
2. Create JSON in `benchmarks/tasks/{difficulty}/`
3. Follow schema in `DATASET_STRUCTURE.md`
4. Include test cases and reference solution
5. Submit PR

### Add Language Support

1. Create executor for the language (see `src/execution/`)
2. Add language-specific test runner
3. Create initial task set (minimum 10 tasks)
4. Update documentation

### Improve the Tool

- See open issues
- Follow code style (black, ruff, mypy)
- Add tests
- Update docs

## Roadmap

- [x] Core benchmark infrastructure
- [x] Python language support
- [x] OpenAI & Anthropic integrations
- [x] Multi-language architecture
- [ ] 100+ Python tasks
- [ ] Rust language support
- [ ] C/C++ language support
- [ ] JavaScript/TypeScript support
- [ ] Public leaderboard website
- [ ] GitHub Actions CI/CD
- [ ] VSCode extension

## Use Cases

### 1. Model Developers
Prove your fine-tuned model outperforms GPT-4 with transparent data.

### 2. Enterprises
Compare models before deploying AI coding assistants to your team.

### 3. Researchers
Benchmark new techniques with reproducible results.

### 4. Educators
Teach AI evaluation with real-world examples.

## FAQ

**Q: Why start with Python?**
A: Python is the most popular language for AI/ML work. It's the natural starting point, but the architecture supports any language.

**Q: Can I add tasks for other languages now?**
A: Yes! The data model supports all languages. You'll need to implement the executor for non-Python languages.

**Q: How much does it cost to run?**
A: Depends on models. ~$0.0004-0.02 per task with GPT/Claude. Full suite: $5-20 for commercial models.

**Q: Are results reproducible?**
A: Yes! Pin model versions, lock dependencies, version tasks.

**Q: Can I use this commercially?**
A: Yes! MIT licensed. Attribution appreciated.

## Citation

```bibtex
@software{compare_your_models,
  title = {Compare Your Models: Multi-Language AI Coding Benchmark},
  author = {Open Source Contributors},
  year = {2025},
  url = {https://github.com/YOUR_USERNAME/compare-your-models}
}
```

## License

MIT License - see [LICENSE](LICENSE)

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/compare-your-models/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/compare-your-models/discussions)

---

**Built to make AI coding benchmarks transparent and multi-language.**

**Compare your models. Prove they're better. Share the results.**
