#!/usr/bin/env python3
"""
Continuous testing script - watches for file changes and runs tests.
"""

import time
import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":
    # Check if watchdog is available
    try:
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

        main()
    except ImportError:
        print("❌ watchdog not installed. Install with: uv add watchdog")
        print("Running single test instead...")
        subprocess.run("pytest tests/ -v", shell=True)
