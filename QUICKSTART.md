# Quick Start Guide

Get your Python model benchmark up and running in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Git
- API keys for models you want to test (OpenAI, Anthropic, etc.)

## Installation

### 1. Clone and Setup

```bash
# Navigate to the project (already cloned)
cd /Users/swastiklohchab/Desktop/Comparison-tool

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your favorite editor
```

Add your API keys:
```env
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key
```

### 3. Configure Models

Edit `config.yaml` to enable/disable models:

```yaml
models:
  - name: "gpt-4-turbo"
    provider: "openai"
    enabled: true  # Set to false to disable

  - name: "claude-3-sonnet"
    provider: "anthropic"
    enabled: true
```

## Running Your First Benchmark

### Option 1: Quick Test (Recommended for First Run)

```bash
# Run a small test with just a few tasks
python -m src.main --difficulty easy --num-tasks 2
```

This will:
- Load 2 easy tasks
- Run them through enabled models
- Show results in terminal

### Option 2: Full Benchmark

```bash
# Run the complete benchmark suite
python -m src.main
```

### Option 3: Specific Model

```bash
# Test only your fine-tuned model
python -m src.main --model your-fine-tuned-model
```

## Viewing Results

### Terminal Output
Results are displayed automatically after each run.

### Dashboard (Coming Soon)
```bash
streamlit run src/dashboard/app.py
```
Open: http://localhost:8501

### Database
Results are saved to: `benchmarks/results/benchmark.db`

Query with any SQLite tool:
```bash
sqlite3 benchmarks/results/benchmark.db
SELECT * FROM model_results LIMIT 10;
```

## Current Status

### What Works Now ✅
- Project structure setup
- Configuration system
- Task format specification
- 2 example tasks (easy + medium)

### What's Being Built 🚧
- Model provider implementations
- Code execution sandbox
- Scoring system
- Dashboard

### Next Steps for You

1. **Add More Tasks** (Easiest way to contribute!)
   - Copy `benchmarks/tasks/easy/task_001_reverse_string.json`
   - Modify for new problem
   - Follow schema in `DATASET_STRUCTURE.md`

2. **Test with Your Model**
   - Add your model to `config.yaml`
   - Set up API endpoint if local model
   - Run benchmark

3. **Help Build Core Features**
   - Check `IMPLEMENTATION_STATUS.md` for what needs work
   - Pick a component and contribute!

## Adding Your Fine-Tuned Model

### If Your Model Has an API

Add to `config.yaml`:

```yaml
models:
  - name: "my-python-expert"
    provider: "local"
    endpoint: "http://localhost:8000/v1/completions"
    api_key_env: "MY_MODEL_API_KEY"
    enabled: true
```

Add key to `.env`:
```env
MY_MODEL_API_KEY=your-key-here
```

### If Your Model is Hugging Face

```yaml
models:
  - name: "my-hf-model"
    provider: "huggingface"
    model_id: "your-username/your-model-name"
    api_key_env: "HUGGINGFACE_API_KEY"
    enabled: true
```

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### API key errors
```bash
# Check .env file exists
cat .env

# Verify keys are set
echo $OPENAI_API_KEY  # Should show your key
```

### Docker issues
```bash
# Build sandbox image
docker build -t python-benchmark-sandbox .

# Test Docker
docker run --rm python-benchmark-sandbox python --version
```

## Example Workflow

Here's a complete workflow from start to finish:

```bash
# 1. Setup (one time)
cd /Users/swastiklohchab/Desktop/Comparison-tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys

# 2. Add a task
cat > benchmarks/tasks/easy/my_task.json << 'EOF'
{
  "id": "easy_002",
  "difficulty": "easy",
  "category": "list_operations",
  "title": "Sum of List",
  "prompt": "Write a function that returns the sum of all numbers in a list...",
  ...
}
EOF

# 3. Run benchmark
python -m src.main --difficulty easy --num-tasks 5

# 4. View results
# Results printed to terminal

# 5. Repeat!
```

## Getting Help

- **Documentation**: Check `README.md` and `ARCHITECTURE.md`
- **Examples**: See `benchmarks/tasks/*/` for task examples
- **Issues**: Open a GitHub issue
- **Status**: Check `IMPLEMENTATION_STATUS.md` for current progress

## What to Expect

### Current State (v0.1.0)
This is an early version. Core infrastructure is set up, but many features are still being built.

### Coming Soon
- Complete model integrations
- Automated scoring
- Interactive dashboard
- 150+ curated tasks

### Timeline
- **Week 1-2**: Basic functionality working
- **Month 1**: First usable version
- **Month 2**: Feature complete
- **Month 3**: Public launch

## Contributing

Want to help build this? Check out:
1. `IMPLEMENTATION_STATUS.md` - See what needs work
2. `ARCHITECTURE.md` - Understand the system
3. GitHub Issues - Find tasks to work on

**The easiest contribution: Add benchmark tasks!**

---

## Quick Reference

```bash
# Virtual environment
source venv/bin/activate          # Activate
deactivate                         # Deactivate

# Running benchmarks
python -m src.main                 # Full suite
python -m src.main --difficulty easy   # Easy only
python -m src.main --model gpt-4-turbo # One model
python -m src.main --num-tasks 5   # Limit tasks

# Development
pytest                             # Run tests
black src/ tests/                  # Format code
ruff check src/                    # Lint
mypy src/                          # Type check

# Docker
docker-compose up                  # Start all services
docker-compose down                # Stop all services
```

**LET'S GOOO! 🚀**
