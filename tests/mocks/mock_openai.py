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
