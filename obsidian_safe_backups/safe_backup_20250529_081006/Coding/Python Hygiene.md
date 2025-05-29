For someone who likes living on the edge with the latest Python stuff, here's a modern hygiene setup that embraces bleeding-edge tools:

## The Bleeding-Edge Stack

**Core Tools:**

```bash
# Install the fastest, newest tools
uv tool install ruff          # Replaces black, isort, flake8
uv tool install mypy          # Type checking
uv tool install pre-commit    # Git hooks
```

## Daily Hygiene Commands

**The "make it perfect" one-liner:**

```bash
uv run ruff check --fix . && uv run ruff format . && uv run mypy src/
```

**Or create a simple script** (`scripts/fix.py`):

```python
#!/usr/bin/env python3
import subprocess
import sys

def run(cmd):
    print(f"🚀 {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

# Fix everything automatically
if not run("ruff check --fix ."):
    print("❌ Linting issues found")
    
if not run("ruff format ."):
    print("❌ Formatting failed")
    
if not run("mypy src/"):
    print("❌ Type checking failed")
    
print("✅ All clean!")
```

Then just: `uv run scripts/fix.py`

## Modern pyproject.toml Setup

```toml
[project]
name = "my-app"
requires-python = ">=3.12"  # Always latest stable
dependencies = [
    # Pin major versions, let minor/patch float
    "fastapi>=0.100",
    "uvicorn>=0.30",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.6",      # Latest ruff
    "mypy>=1.8",      # Latest mypy  
    "pytest>=8.0",    # Latest pytest
    "pre-commit>=3.0",
]

# Ruff replaces black, isort, flake8, and more
[tool.ruff]
target-version = "py312"
line-length = 88

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings  
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
    "RUF", # Ruff-specific rules
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.12"
strict = true  # Go hard or go home
warn_return_any = true
warn_unused_configs = true
```

## Pre-commit Setup for Automated Hygiene

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0  # Keep this updated
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
      
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

## Update Strategy for Bleeding Edge

**Weekly update ritual:**

```bash
# Update all tools
uv tool upgrade --all

# Update project dependencies  
uv sync --upgrade

# Update pre-commit hooks
pre-commit autoupdate

# Test everything still works
uv run pytest
```

**Monthly "chaos engineering":**

```bash
# Upgrade to latest Python version
uv python install 3.13
echo "3.13" > .python-version

# Recreate venv with new Python
rm -rf .venv
uv sync

# See what breaks and fix it!
```

## Advanced Hygiene with Just

Install `just` (modern make replacement):

```bash
uv tool install just
```

`justfile`:

```make
# Run all hygiene checks
check:
    ruff check .
    ruff format --check .
    mypy src/
    pytest

# Fix everything automatically  
fix:
    ruff check --fix .
    ruff format .

# Update everything to bleeding edge
update:
    uv sync --upgrade
    uv tool upgrade --all
    pre-commit autoupgrade
    
# Nuclear option: upgrade Python version
upgrade-python version:
    uv python install {{version}}
    echo "{{version}}" > .python-version
    rm -rf .venv
    uv sync
```

Then just: `just fix` or `just update`

## CI/CD for Continuous Hygiene

`.github/workflows/hygiene.yml`:

```yaml
name: Hygiene
on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Check code quality
        run: |
          uv sync
          uv run ruff check .
          uv run ruff format --check .
          uv run mypy src/
          uv run pytest
```

## Pro Tips for Bleeding Edge Life

1. **Pin major versions only** - Let minor/patch versions float for automatic security updates
    
2. **Use `uv sync --upgrade` regularly** - Keeps you on latest compatible versions
    
3. **Embrace Ruff** - It's replacing like 6 different tools and is 100x faster
    
4. **Type everything** - Modern Python is typed Python, embrace strict mypy
    
5. **Test in CI** - Since you're living dangerously, at least catch issues early
    
6. **Keep a rollback plan** - `uv.lock` files let you pin exact versions when things break
    

The beauty of this setup is it's **fast** (ruff is insanely quick), **comprehensive** (catches most issues), and **automated** (pre-commit hooks do the work). Perfect for someone who wants to stay cutting-edge without spending all day on maintenance!