## Prerequisites

Install these tools first:

- **Python 3.11+** (3.12 recommended for best performance)
- **direnv** - Auto-loads environment variables
- **uv** - Fast Python package manager (replaces pip/pip-tools)

```bash
# Install direnv (macOS)
brew install direnv

# Install direnv (Ubuntu/Debian)
sudo apt install direnv

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Project Structure

Create your project with this modern structure:

```
my-project/
├── .envrc                 # direnv config
├── .gitignore
├── .python-version        # Python version pinning
├── pyproject.toml         # Modern Python config
├── README.md
├── requirements.lock      # Locked dependencies
├── src/
│   └── my_project/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── .venv/                 # Virtual environment (auto-created)
```

## Step-by-Step Setup

### 1. Initialize the Project

```bash
mkdir my-project && cd my-project
echo "3.12" > .python-version
```

### 2. Create `.envrc` for direnv

```bash
# .envrc
export VIRTUAL_ENV=.venv
layout python python3.12

# Optional: Add custom environment variables
export DEBUG=true
export DATABASE_URL="sqlite:///dev.db"
```

### 3. Allow direnv and Create Virtual Environment

```bash
direnv allow
uv venv --python 3.12
```

### 4. Create Modern `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "0.1.0"
description = "A modern Python project"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    # Add your runtime dependencies here
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov",
    "black",
    "isort",
    "flake8",
    "mypy",
    "pre-commit",
]

[project.urls]
Repository = "https://github.com/yourusername/my-project"

[project.scripts]
my-project = "my_project.main:main"

# Tool configurations
[tool.black]
line-length = 88
target-version = ['py311']

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--cov=src --cov-report=html --cov-report=term-missing"
```

### 5. Install Dependencies

```bash
# Install dev dependencies
uv add --dev pytest pytest-cov black isort flake8 mypy pre-commit

# Install runtime dependencies (examples)
uv add requests fastapi

# Generate lock file
uv export --format requirements-txt > requirements.lock
```

### 6. Create Source Code Structure

```bash
mkdir -p src/my_project tests
touch src/my_project/__init__.py tests/__init__.py
```

**src/my_project/main.py:**

```python
"""Main application module."""

def main() -> None:
    """Entry point for the application."""
    print("Hello, modern Python!")

if __name__ == "__main__":
    main()
```

**tests/test_main.py:**

```python
"""Tests for main module."""
import pytest
from my_project.main import main

def test_main():
    """Test main function runs without error."""
    main()  # Should not raise
```

### 7. Setup Code Quality Tools

```bash
# Initialize pre-commit
pre-commit install

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
EOF
```

### 8. Create `.gitignore`

```bash
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore
echo ".envrc" >> .gitignore  # Keep direnv config private if it has secrets
```

## Daily Workflow

### Adding Dependencies

```bash
# Runtime dependency
uv add requests

# Development dependency
uv add --dev pytest-mock

# Update lock file
uv export --format requirements-txt > requirements.lock
```

### Running Code Quality Checks

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Run tests
pytest

# All at once with pre-commit
pre-commit run --all-files
```

### Environment Management

```bash
# direnv automatically activates when you cd into the project
cd my-project  # .venv activates automatically

# Check Python path
which python  # Should show .venv/bin/python

# Deactivate (rarely needed with direnv)
cd ..  # Automatically deactivates
```

## Modern Best Practices Included

- **uv** for fast dependency management and virtual environments
- **direnv** for automatic environment activation
- **src layout** to avoid import issues
- **pyproject.toml** for all configuration
- **Type hints** and mypy for static typing
- **Pre-commit hooks** for code quality
- **Locked dependencies** for reproducible builds
- **Modern testing** with pytest and coverage
- **Black + isort** for consistent formatting

## Pro Tips

1. **Pin Python version** with `.python-version` for team consistency
2. **Use `uv sync`** in CI/CD for faster, reproducible installs
3. **Commit `requirements.lock`** for deployment reproducibility
4. **Keep `pyproject.toml`** as single source of truth for all config
5. **Use `src/` layout** to catch import errors early

This setup gives you a production-ready Python project with modern tooling and best practices built in from day one.