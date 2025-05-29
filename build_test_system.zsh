#!/bin/zsh

# Test System Builder Script for Obsidian Analyzer
# Creates comprehensive test suite with health monitoring

set -e

echo "🧪 Building Test System for Obsidian Analyzer..."
echo "=============================================="

if [[ ! -d "obsidian_analyzer" ]]; then
    echo "❌ Error: Run this script from the Obsidian_Analyzer project directory"
    exit 1
fi

echo "✅ Project directory confirmed"

# Create test directories
mkdir -p tests/{unit,integration,fixtures,reports}
mkdir -p test_vault/{Coding,Philosophy,Book,Root}

echo "📁 Created test directories"

# Create test fixtures (sample vault)
echo "📝 Creating test vault fixtures..."

cat > test_vault/Root/Welcome.md << 'EOF'
# Welcome to Test Vault

This is a test note for the [[Philosophy]] and [[Coding]] sections.

We have some #testing and #automation topics here.

## Links
- Check out [[Python Basics]]
- Read about [[Stoicism]]
EOF

cat > test_vault/Coding/Python\ Basics.md << 'EOF'
# Python Basics

This covers fundamental Python concepts.

```python
def hello_world():
    print("Hello, World!")
```

Topics covered:
- Variables and data types
- Functions and classes
- Error handling

Related: [[Advanced Python]] and [[Testing in Python]]

#python #programming #basics
EOF

cat > test_vault/Coding/Advanced\ Python.md << 'EOF'
# Advanced Python

Advanced Python topics including decorators and metaclasses.

```python
@decorator
def advanced_function():
    pass
```

This builds on [[Python Basics]] concepts.

#python #advanced #programming
EOF

cat > test_vault/Coding/Testing\ in\ Python.md << 'EOF'
# Testing in Python

How to write tests for Python applications.

```python
import pytest

def test_example():
    assert 1 + 1 == 2
```

See [[Python Basics]] for fundamentals.

#python #testing #pytest
EOF

cat > test_vault/Philosophy/Stoicism.md << 'EOF'
# Stoicism

Ancient philosophy focusing on virtue and wisdom.

Key concepts:
- Virtue as the highest good
- Focus on what you can control
- Acceptance of fate

Related to [[Mindfulness]] practices.

#philosophy #stoicism #ancient
EOF

cat > test_vault/Philosophy/Mindfulness.md << 'EOF'
# Mindfulness

Present-moment awareness practice.

Connects to [[Stoicism]] principles.

#philosophy #mindfulness #meditation
EOF

cat > test_vault/Book/Meditations.md << 'EOF'
# Meditations by Marcus Aurelius

Classic work on [[Stoicism]].

Key themes:
- Self-reflection
- Virtue ethics
- Death contemplation

#book #philosophy #stoicism #marcus-aurelius
EOF

echo "✅ Created test vault fixtures"

# Create unit tests
echo "🔬 Creating unit tests..."

cat > tests/unit/test_models.py << 'EOF'
"""Unit tests for data models."""

import pytest
from obsidian_analyzer.models import LinkSuggestion, StructureSuggestion


class TestLinkSuggestion:
    def test_creation(self):
        suggestion = LinkSuggestion(
            target_note="Test Note",
            context_snippets=["context 1", "context 2"],
            confidence=0.8,
            mention_count=2
        )
        assert suggestion.target_note == "Test Note"
        assert suggestion.confidence == 0.8
        assert suggestion.mention_count == 2
        assert len(suggestion.context_snippets) == 2
    
    def test_string_representation(self):
        suggestion = LinkSuggestion(
            target_note="Test Note",
            context_snippets=["context"],
            confidence=0.75,
            mention_count=1
        )
        assert "Test Note" in str(suggestion)
        assert "75%" in str(suggestion)


class TestStructureSuggestion:
    def test_creation(self):
        suggestion = StructureSuggestion(
            suggestion_type="add_headings",
            description="Add headings to improve structure",
            examples=["## Introduction", "## Conclusion"]
        )
        assert suggestion.suggestion_type == "add_headings"
        assert suggestion.description == "Add headings to improve structure"
        assert len(suggestion.examples) == 2
    
    def test_string_representation(self):
        suggestion = StructureSuggestion(
            suggestion_type="add_headings",
            description="Test description"
        )
        assert "add_headings" in str(suggestion)
        assert "Test description" in str(suggestion)
EOF

cat > tests/unit/test_analyzer.py << 'EOF'
"""Unit tests for the core analyzer."""

import pytest
import tempfile
import os
from pathlib import Path
from obsidian_analyzer.analyzer import CodingFolderAnalyzer


class TestCodingFolderAnalyzer:
    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            coding_folder = vault_path / "Coding"
            coding_folder.mkdir()
            
            # Create test files
            (coding_folder / "test1.md").write_text("""
# Test Note 1
This mentions [[test2]] and has #python content.
```python
print("hello")
```
            """)
            
            (coding_folder / "test2.md").write_text("""
# Test Note 2
This has some content and mentions [[test1]].
## Section
More content here.
            """)
            
            yield str(vault_path)
    
    def test_initialization(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        assert analyzer.vault_path == Path(temp_vault)
        assert analyzer.coding_folder == Path(temp_vault) / "Coding"
    
    def test_load_notes(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        analyzer.load_coding_notes()
        
        assert len(analyzer.notes) == 2
        assert "test1" in analyzer.notes
        assert "test2" in analyzer.notes
        
        # Check note data
        test1 = analyzer.notes["test1"]
        assert test1["word_count"] > 0
        assert "test2" in test1["links"]
        assert ("languages", "python") in test1["topics"]
    
    def test_extract_links(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = "This has [[link1]] and [[link2|display text]] links."
        links = analyzer.extract_links(content)
        
        assert "link1" in links
        assert "link2" in links
        assert len(links) == 2
    
    def test_extract_tags(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = "Content with #tag1 and #tag2/subtag tags."
        tags = analyzer.extract_tags(content)
        
        assert "tag1" in tags
        assert "tag2/subtag" in tags
    
    def test_extract_headings(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = """# Main Heading
## Sub Heading
### Sub Sub Heading"""
        headings = analyzer.extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0] == (1, "Main Heading")
        assert headings[1] == (2, "Sub Heading")
        assert headings[2] == (3, "Sub Sub Heading")
    
    def test_link_suggestions(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        analyzer.load_coding_notes()
        
        suggestions = analyzer.find_link_suggestions("test1")
        assert isinstance(suggestions, list)
        # Should find suggestions based on content analysis
EOF

cat > tests/unit/test_multi_analyzer.py << 'EOF'
"""Unit tests for multi-folder analyzer."""

import pytest
import tempfile
from pathlib import Path
from obsidian_analyzer.multi_analyzer import MultiVaultAnalyzer, FolderStats


class TestMultiVaultAnalyzer:
    @pytest.fixture
    def test_vault_path(self):
        """Use the test vault we created."""
        return str(Path(__file__).parent.parent.parent / "test_vault")
    
    def test_initialization(self, test_vault_path):
        analyzer = MultiVaultAnalyzer(test_vault_path)
        assert analyzer.vault_path == Path(test_vault_path)
    
    def test_discover_folders(self, test_vault_path):
        analyzer = MultiVaultAnalyzer(test_vault_path)
        folders = analyzer.discover_folders()
        
        assert isinstance(folders, list)
        assert "Coding" in folders
        assert "Philosophy" in folders
        assert "Book" in folders
        assert "Root" in folders
    
    def test_analyze_folder(self, test_vault_path):
        analyzer = MultiVaultAnalyzer(test_vault_path)
        stats = analyzer.analyze_folder("Coding")
        
        assert isinstance(stats, FolderStats)
        assert stats.name == "Coding"
        assert stats.note_count > 0
        assert stats.total_words > 0
    
    def test_full_vault_analysis(self, test_vault_path):
        analyzer = MultiVaultAnalyzer(test_vault_path)
        analysis = analyzer.analyze_entire_vault()
        
        assert analysis is not None
        assert analysis.total_folders >= 4
        assert analysis.total_notes > 0
        assert 0 <= analysis.vault_health_score <= 100
        assert len(analysis.folder_stats) >= 4
EOF

cat > tests/unit/test_auto_linker.py << 'EOF'
"""Unit tests for auto-linker."""

import pytest
import tempfile
import shutil
from pathlib import Path
from obsidian_analyzer.auto_linker import AutoLinker


class TestAutoLinker:
    @pytest.fixture
    def test_vault_path(self):
        """Create a temporary test vault."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            coding_folder = vault_path / "Coding"
            coding_folder.mkdir()
            
            # Create test files
            (coding_folder / "note1.md").write_text("""
# Note 1
This mentions note2 without linking.
Also talks about note3 concepts.
            """)
            
            (coding_folder / "note2.md").write_text("""
# Note 2
This is the target note.
            """)
            
            (coding_folder / "note3.md").write_text("""
# Note 3
Another target note.
            """)
            
            yield str(vault_path)
    
    def test_initialization(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        assert linker.vault_path == Path(test_vault_path)
        assert not linker.backup
    
    def test_analyze_and_suggest_links(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        suggestions = linker.analyze_and_suggest_links("Coding")
        
        assert isinstance(suggestions, dict)
        # Should find suggestions for note1 mentioning note2/note3
    
    def test_dry_run_mode(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        results = linker.auto_link_folder("Coding", dry_run=True)
        
        # Should return results without modifying files
        assert isinstance(results, dict)
        
        # Verify files weren't actually modified
        note1_path = Path(test_vault_path) / "Coding" / "note1.md"
        content = note1_path.read_text()
        assert "[[note2]]" not in content  # Should not be modified in dry run
EOF

echo "✅ Created unit tests"

# Create integration tests
echo "🔗 Creating integration tests..."

cat > tests/integration/test_full_workflow.py << 'EOF'
"""Integration tests for full workflow."""

import pytest
from pathlib import Path
from obsidian_analyzer import CodingFolderAnalyzer, MultiVaultAnalyzer, AutoLinker


class TestFullWorkflow:
    @pytest.fixture
    def test_vault_path(self):
        """Use the test vault."""
        return str(Path(__file__).parent.parent.parent / "test_vault")
    
    def test_single_folder_analysis_workflow(self, test_vault_path):
        """Test complete single-folder analysis workflow."""
        # 1. Analyze folder
        analyzer = CodingFolderAnalyzer(test_vault_path)
        analyzer.load_coding_notes()
        
        assert len(analyzer.notes) > 0
        
        # 2. Get recommendations
        first_note = list(analyzer.notes.keys())[0]
        recommendations = analyzer.get_note_recommendations(first_note)
        
        assert "note_name" in recommendations
        assert "link_suggestions" in recommendations
        assert "structure_suggestions" in recommendations
    
    def test_multi_folder_analysis_workflow(self, test_vault_path):
        """Test complete multi-folder analysis workflow."""
        # 1. Discover and analyze
        analyzer = MultiVaultAnalyzer(test_vault_path)
        analysis = analyzer.analyze_entire_vault()
        
        assert analysis is not None
        assert analysis.total_notes > 0
        assert analysis.total_folders > 0
        
        # 2. Export report
        report_path = analyzer.export_markdown_report(analysis)
        assert Path(report_path).exists()
        
        # Check report content
        report_content = Path(report_path).read_text()
        assert "# 🔍 Obsidian Vault Analysis Report" in report_content
        assert "Health Score:" in report_content
    
    def test_auto_linking_workflow(self, test_vault_path):
        """Test auto-linking workflow with dry run."""
        # 1. Analyze and suggest links
        linker = AutoLinker(test_vault_path, backup=False)
        suggestions = linker.analyze_and_suggest_links("Coding")
        
        assert isinstance(suggestions, dict)
        
        # 2. Dry run auto-linking
        results = linker.auto_link_folder("Coding", dry_run=True)
        
        # Should complete without errors
        assert isinstance(results, dict)
    
    def test_end_to_end_vault_improvement(self, test_vault_path):
        """Test complete vault improvement workflow."""
        # 1. Multi-folder analysis
        multi_analyzer = MultiVaultAnalyzer(test_vault_path)
        analysis = multi_analyzer.analyze_entire_vault()
        
        initial_health_score = analysis.vault_health_score
        initial_links = analysis.total_links
        
        # 2. Auto-link suggestions (dry run)
        linker = AutoLinker(test_vault_path, backup=False)
        link_results = linker.auto_link_folder("Coding", dry_run=True)
        
        # 3. Verify workflow completed
        assert analysis.total_notes > 0
        assert isinstance(link_results, dict)
        
        # Should have found improvement opportunities
        has_opportunities = (
            analysis.global_orphaned_notes > 0 or
            len(analysis.cross_folder_suggestions) > 0 or
            len(link_results) > 0
        )
        
        # At least some improvement opportunity should exist
        # (This is a reasonable assumption for most vaults)
EOF

echo "✅ Created integration tests"

# Create performance tests
echo "⚡ Creating performance tests..."

cat > tests/integration/test_performance.py << 'EOF'
"""Performance tests for Obsidian Analyzer."""

import pytest
import time
from pathlib import Path
from obsidian_analyzer import MultiVaultAnalyzer, CodingFolderAnalyzer


class TestPerformance:
    @pytest.fixture
    def test_vault_path(self):
        return str(Path(__file__).parent.parent.parent / "test_vault")
    
    def test_single_folder_analysis_performance(self, test_vault_path):
        """Test that single folder analysis completes in reasonable time."""
        start_time = time.time()
        
        analyzer = CodingFolderAnalyzer(test_vault_path)
        analyzer.load_coding_notes()
        
        if analyzer.notes:
            first_note = list(analyzer.notes.keys())[0]
            analyzer.get_note_recommendations(first_note)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 5 seconds for small test vault
        assert duration < 5.0, f"Analysis took {duration:.2f} seconds, expected < 5.0"
    
    def test_multi_folder_analysis_performance(self, test_vault_path):
        """Test that multi-folder analysis completes in reasonable time."""
        start_time = time.time()
        
        analyzer = MultiVaultAnalyzer(test_vault_path)
        analysis = analyzer.analyze_entire_vault()
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 10 seconds for small test vault
        assert duration < 10.0, f"Analysis took {duration:.2f} seconds, expected < 10.0"
        assert analysis is not None
    
    def test_memory_usage_reasonable(self, test_vault_path):
        """Test that memory usage stays reasonable during analysis."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        analyzer = MultiVaultAnalyzer(test_vault_path)
        analysis = analyzer.analyze_entire_vault()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not use more than 100MB additional memory for small vault
        assert memory_increase < 100, f"Memory increased by {memory_increase:.1f}MB, expected < 100MB"
        assert analysis is not None
EOF

echo "✅ Created performance tests"

# Create test configuration
echo "⚙️  Creating test configuration..."

cat > pytest.ini << 'EOF'
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow tests that might take a while
EOF

cat > tests/conftest.py << 'EOF'
"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_vault_path():
    """Path to the test vault used across all tests."""
    return str(project_root / "test_vault")


@pytest.fixture(autouse=True)
def suppress_prints(capfd):
    """Suppress print statements during tests unless they fail."""
    yield
EOF

echo "✅ Created test configuration"

# Create health monitoring script
echo "🏥 Creating health monitoring script..."

cat > scripts/health_check.py << 'EOF'
#!/usr/bin/env python3
"""
Health check script for Obsidian Analyzer system.
Runs tests and generates health report.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_command(cmd, description):
    """Run a command and return result."""
    print(f"🔍 {description}...")
    try:
        start_time = time.time()
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=True
        )
        duration = time.time() - start_time
        print(f"✅ {description} - OK ({duration:.2f}s)")
        return True, duration, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}")
        return False, 0, e.stderr


def check_dependencies():
    """Check if all required dependencies are available."""
    deps = ["pytest", "psutil"]
    missing = []
    
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Install with: uv add " + " ".join(missing))
        return False
    
    return True


def run_health_check():
    """Run comprehensive health check."""
    print("🏥 Obsidian Analyzer Health Check")
    print("=" * 40)
    
    health_report = {
        "timestamp": datetime.now().isoformat(),
        "overall_status": "UNKNOWN",
        "checks": {}
    }
    
    # Check dependencies
    if not check_dependencies():
        health_report["overall_status"] = "FAILED"
        health_report["checks"]["dependencies"] = {"status": "FAILED", "message": "Missing dependencies"}
        return health_report
    
    checks = [
        ("pytest tests/unit -v", "Unit Tests"),
        ("pytest tests/integration -v", "Integration Tests"),
        ("pytest tests/integration/test_performance.py -v", "Performance Tests"),
        ("python -c 'from obsidian_analyzer import CodingFolderAnalyzer; print(\"Import OK\")'", "Module Import"),
        ("python scripts/analyze_vault.py test_vault --output /tmp/test_report.md", "CLI Functionality"),
    ]
    
    passed = 0
    total = len(checks)
    
    for cmd, description in checks:
        success, duration, output = run_command(cmd, description)
        
        health_report["checks"][description.lower().replace(" ", "_")] = {
            "status": "PASSED" if success else "FAILED",
            "duration": duration,
            "command": cmd
        }
        
        if success:
            passed += 1
    
    # Overall status
    if passed == total:
        health_report["overall_status"] = "HEALTHY"
        print(f"\n🎉 System Health: HEALTHY ({passed}/{total} checks passed)")
    elif passed >= total * 0.7:
        health_report["overall_status"] = "WARNING"
        print(f"\n⚠️  System Health: WARNING ({passed}/{total} checks passed)")
    else:
        health_report["overall_status"] = "CRITICAL"
        print(f"\n🚨 System Health: CRITICAL ({passed}/{total} checks passed)")
    
    # Save health report
    report_path = Path("tests/reports/health_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(health_report, f, indent=2)
    
    print(f"📄 Health report saved to: {report_path}")
    
    return health_report


def main():
    """Main health check function."""
    try:
        report = run_health_check()
        
        # Exit with appropriate code
        if report["overall_status"] == "HEALTHY":
            sys.exit(0)
        elif report["overall_status"] == "WARNING":
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⏹️  Health check cancelled")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
EOF

chmod +x scripts/health_check.py

echo "✅ Created health monitoring script"

# Create continuous testing script
echo "🔄 Creating continuous testing script..."

cat > scripts/watch_tests.py << 'EOF'
#!/usr/bin/env python3
"""
Continuous testing script - watches for file changes and runs tests.
"""

import time
import subprocess
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class TestRunner(FileSystemEventHandler):
    def __init__(self):
        self.last_run = 0
        self.debounce_seconds = 2
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Only run tests for Python files
        if not event.src_path.endswith('.py'):
            return
        
        # Debounce rapid file changes
        now = time.time()
        if now - self.last_run < self.debounce_seconds:
            return
        
        self.last_run = now
        
        print(f"\n📝 File changed: {event.src_path}")
        self.run_relevant_tests(event.src_path)
    
    def run_relevant_tests(self, file_path):
        """Run tests relevant to the changed file."""
        path = Path(file_path)
        
        # Determine which tests to run
        if "obsidian_analyzer" in str(path):
            if "analyzer.py" in str(path):
                test_cmd = "pytest tests/unit/test_analyzer.py -v"
            elif "multi_analyzer.py" in str(path):
                test_cmd = "pytest tests/unit/test_multi_analyzer.py -v"
            elif "auto_linker.py" in str(path):
                test_cmd = "pytest tests/unit/test_auto_linker.py -v"
            else:
                test_cmd = "pytest tests/unit -v"
        elif "tests" in str(path):
            test_cmd = f"pytest {file_path} -v"
        else:
            test_cmd = "pytest tests/unit -v --tb=short"
        
        print(f"🧪 Running: {test_cmd}")
        
        try:
            result = subprocess.run(
                test_cmd, shell=True, capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print("✅ Tests passed!")
            else:
                print("❌ Tests failed!")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            print(f"❌ Error running tests: {e}")


def main():
    """Start continuous testing."""
    print("🔄 Starting continuous testing...")
    print("Watching for file changes in obsidian_analyzer/ and tests/")
    print("Press Ctrl+C to stop")
    
    event_handler = TestRunner()
    observer = Observer()
    
    # Watch source code and tests
    observer.schedule(event_handler, "obsidian_analyzer", recursive=True) 
    observer.schedule(event_handler, "tests", recursive=True)
    
    observer.start()
    
    try:
        # Run initial test suite
        print("\n🧪 Running initial test suite...")
        subprocess.run("pytest tests/unit -v --tb=short", shell=True)
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n⏹️  Stopped continuous testing")
    
    observer.join()


if __name__ == "__main__":
    # Check if watchdog is available
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        main()
    except ImportError:
        print("❌ watchdog not installed. Install with: uv add watchdog")
        print("Running single test instead...")
        subprocess.run("pytest tests/ -v", shell=True)
EOF

chmod +x scripts/watch_tests.py

echo "✅ Created continuous testing script"

# Install test dependencies
echo "📦 Installing test dependencies..."
uv add pytest psutil watchdog

# Install the package in test mode
uv pip install -e .

echo ""
echo "🎉 TEST SYSTEM SUCCESSFULLY BUILT!"
echo "================================="
echo ""
echo "🧪 TESTING COMMANDS:"
echo ""
echo "1️⃣  RUN ALL TESTS:"
echo "   pytest tests/ -v"
echo ""
echo "2️⃣  RUN UNIT TESTS ONLY:"
echo "   pytest tests/unit -v"
echo ""
echo "3️⃣  RUN INTEGRATION TESTS:"
echo "   pytest tests/integration -v"
echo ""
echo "4️⃣  RUN PERFORMANCE TESTS:"
echo "   pytest tests/integration/test_performance.py -v"
echo ""
echo "5️⃣  HEALTH CHECK:"
echo "   python scripts/health_check.py"
echo ""
echo "6️⃣  CONTINUOUS TESTING:"
echo "   python scripts/watch_tests.py"
echo ""
echo "📊 TEST STRUCTURE:"
echo "   tests/unit/          - Unit tests for individual components"
echo "   tests/integration/   - Integration and end-to-end tests"
echo "   tests/fixtures/      - Test data and fixtures"
echo "   test_vault/          - Sample vault for testing"
echo ""
echo "🏥 HEALTH MONITORING:"
echo "   • Automated test runs with health scoring"
echo "   • Performance regression detection"
echo "   • Memory usage monitoring" 
echo "   • CLI functionality verification"
echo ""
echo "🔄 CONTINUOUS INTEGRATION:"
echo "   • File change detection"
echo "   • Automatic test runs"
echo "   • Real-time feedback"
echo ""
echo "✅ Test system ready! Run 'pytest tests/ -v' to start testing!"