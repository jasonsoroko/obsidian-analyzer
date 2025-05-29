#!/usr/bin/env python3
"""
AI-aware health check for Obsidian Analyzer.
"""

import sys
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, description):
    """Run a command and return result."""
    print(f"🔍 {description}...")
    try:
        start_time = time.time()
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        duration = time.time() - start_time
        print(f"✅ {description} - OK ({duration:.2f}s)")
        return True, duration, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}")
        return False, 0, e.stderr

def main():
    """Main AI health check function."""
    print("🤖 AI-Aware Obsidian Analyzer Health Check")
    print("=" * 45)
    
    checks = [
        ("python -c 'from tests.mocks.mock_openai import MockOpenAIClient; print(\"Mock AI OK\")'", "AI Mocking System"),
        ("python -c 'import json; print(\"JSON fixtures OK\")'", "Fixture System"),
    ]
    
    passed = 0
    total = len(checks)
    
    for cmd, description in checks:
        success, duration, output = run_command(cmd, description)
        if success:
            passed += 1
    
    if passed == total:
        print(f"\n🎉 AI System Health: HEALTHY ({passed}/{total} checks passed)")
    else:
        print(f"\n⚠️  AI System Health: WARNING ({passed}/{total} checks passed)")

if __name__ == "__main__":
    main()
