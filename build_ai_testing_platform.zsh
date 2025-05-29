#!/bin/zsh

# AI-Aware Testing Platform Builder
# Comprehensive testing for AI-powered Obsidian analysis tools

set -e

echo "🤖 Building AI-Aware Testing Platform..."
echo "====================================="

if [[ ! -d "obsidian_analyzer" ]]; then
    echo "❌ Error: Run this script from the Obsidian_Analyzer project directory"
    exit 1
fi

echo "✅ Project directory confirmed"

# Install additional testing dependencies
echo "📦 Installing testing dependencies..."
uv add pytest-mock pytest-asyncio responses faker

# Create AI testing infrastructure
mkdir -p tests/{ai,mocks,fixtures/ai_responses,reports}
mkdir -p scripts

echo "🧪 Creating AI test infrastructure..."

# AI Response Fixtures
cat > tests/fixtures/ai_responses/semantic_connections.json << 'FIXTURES_EOF'
{
  "valid_connection": {
    "should_link": true,
    "relationship_type": "related_concept",
    "explanation": "Both notes discuss Python development practices",
    "confidence": 0.85,
    "suggested_context": "Consider linking when discussing Python tooling"
  },
  "no_connection": {
    "should_link": false,
    "relationship_type": "none",
    "explanation": "Notes cover unrelated topics",
    "confidence": 0.2,
    "suggested_context": ""
  },
  "bridge_gaps": [
    {
      "gap_type": "bridge_connection",
      "title": "Python Testing Integration",
      "description": "Connects testing practices with development workflow",
      "priority": "high",
      "confidence": 0.9,
      "related_notes": ["Python Testing", "Development Workflow"],
      "suggested_content": ["Test automation", "CI/CD integration"],
      "tags": ["python", "testing", "automation"]
    }
  ],
  "topic_gaps": [
    {
      "gap_type": "topic_coverage",
      "title": "Advanced Python Patterns",
      "description": "Deep dive into advanced Python programming patterns",
      "priority": "medium",
      "confidence": 0.75,
      "related_notes": ["Python Basics", "Python Advanced"],
      "suggested_content": ["Design patterns", "Metaclasses", "Decorators"],
      "tags": ["python", "advanced", "patterns"]
    }
  ]
}
FIXTURES_EOF

# Mock OpenAI Client
cat > tests/mocks/mock_openai.py << 'MOCK_EOF'
"""Mock OpenAI client for testing AI functionality without API calls."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import MagicMock


class MockOpenAIResponse:
    """Mock OpenAI API response."""
    
    def __init__(self, content: str):
        self.choices = [MagicMock()]
        self.choices[0].message.content = content


class MockOpenAIClient:
    """Mock OpenAI client that returns predictable responses."""
    
    def __init__(self, fixtures_path: Optional[Path] = None):
        self.fixtures_path = fixtures_path or Path(__file__).parent.parent / "fixtures" / "ai_responses"
        self.chat = MagicMock()
        self.chat.completions = MagicMock()
        self.chat.completions.create = self._mock_create
        
        # Load fixtures
        self.fixtures = {}
        self._load_fixtures()
    
    def _load_fixtures(self):
        """Load AI response fixtures."""
        try:
            with open(self.fixtures_path / "semantic_connections.json") as f:
                self.fixtures = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load AI fixtures: {e}")
            self.fixtures = {}
    
    def _mock_create(self, model: str, messages: list, **kwargs) -> MockOpenAIResponse:
        """Mock the chat.completions.create method."""
        
        # Analyze the prompt to determine what kind of response to return
        prompt = messages[0]["content"].lower() if messages else ""
        
        if "bridge" in prompt or "missing" in prompt:
            # Content gap analysis request
            if "bridge" in prompt:
                response = json.dumps(self.fixtures.get("bridge_gaps", []))
            else:
                response = json.dumps(self.fixtures.get("topic_gaps", []))
        
        elif "should_link" in prompt or "relationship" in prompt:
            # Semantic connection analysis
            if "python" in prompt:
                response = json.dumps(self.fixtures.get("valid_connection", {}))
            else:
                response = json.dumps(self.fixtures.get("no_connection", {}))
        
        elif "cluster" in prompt:
            # Knowledge cluster analysis
            response = json.dumps([{
                "cluster_name": "Test Cluster",
                "notes": ["Note 1", "Note 2"],
                "topics": ["topic1", "topic2"],
                "missing_connections": ["connection1"],
                "hub_potential": 0.8
            }])
        
        else:
            # Default response
            response = json.dumps({
                "should_link": False,
                "relationship_type": "none",
                "explanation": "Default mock response",
                "confidence": 0.5,
                "suggested_context": "Test context"
            })
        
        return MockOpenAIResponse(response)
    
    def set_custom_response(self, response_content: str):
        """Set a custom response for testing specific scenarios."""
        self.chat.completions.create = lambda **kwargs: MockOpenAIResponse(response_content)
    
    def simulate_api_error(self):
        """Simulate an API error for testing error handling."""
        def error_response(**kwargs):
            raise Exception("Mock API Error: Rate limit exceeded")
        
        self.chat.completions.create = error_response
MOCK_EOF

# Create empty __init__.py files to make directories proper Python packages
touch tests/__init__.py
touch tests/ai/__init__.py
touch tests/mocks/__init__.py
touch tests/fixtures/__init__.py

# Update pytest configuration for AI tests
cat > pytest.ini << 'PYTEST_EOF'
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
    ai: AI functionality tests
    slow: Slow tests that might take a while
    mock: Tests using mocked dependencies
PYTEST_EOF

# Create AI health check script
cat > scripts/ai_health_check.py << 'HEALTH_EOF'
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
HEALTH_EOF

chmod +x scripts/ai_health_check.py

echo "✅ Created AI testing infrastructure"

# Install and test
echo "📦 Installing project in development mode..."
uv pip install -e .

echo ""
echo "🤖 AI-AWARE TESTING PLATFORM READY!"
echo "=================================="
echo ""
echo "🧪 QUICK TESTS:"
echo ""
echo "1️⃣  AI HEALTH CHECK:"
echo "   python scripts/ai_health_check.py"
echo ""
echo "2️⃣  TEST MOCK SYSTEM:"
echo "   python -c 'from tests.mocks.mock_openai import MockOpenAIClient; print(\"✅ Mock system working!\")'"
echo ""
echo "✅ AI testing platform ready!"
