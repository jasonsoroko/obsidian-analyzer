"""Tests for AI Semantic Linker functionality."""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from obsidian_analyzer.ai_semantic_linker import AISemanticLinker, SemanticConnection
from tests.mocks.mock_openai import MockOpenAIClient


class TestAISemanticLinker:
    """Test AI-powered semantic linking functionality."""
    
    @pytest.fixture
    def mock_vault_path(self, tmp_path):
        """Create a temporary vault for testing."""
        vault_path = tmp_path / "test_vault"
        coding_folder = vault_path / "Coding"
        coding_folder.mkdir(parents=True)
        
        # Create test notes
        (coding_folder / "note1.md").write_text("""
# Python Testing
This note covers Python testing frameworks and best practices.
Topics: unit testing, pytest, test automation
#python #testing
        """)
        
        (coding_folder / "note2.md").write_text("""
# API Development
Guide to building REST APIs with Python.
Topics: FastAPI, Flask, REST principles
#python #api #development
        """)
        
        return str(vault_path)
    
    @pytest.fixture
    def ai_linker(self, mock_vault_path):
        """Create AI linker with mocked OpenAI client."""
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI') as mock_openai:
            mock_openai.return_value = MockOpenAIClient()
            linker = AISemanticLinker(mock_vault_path)
            return linker
    
    def test_initialization(self, mock_vault_path):
        """Test AI linker initialization."""
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI'):
            linker = AISemanticLinker(mock_vault_path)
            assert linker.vault_path == Path(mock_vault_path)
    
    def test_analyze_semantic_connections(self, ai_linker):
        """Test semantic connection analysis."""
        connections = ai_linker.analyze_semantic_connections("Coding")
        
        assert isinstance(connections, list)
        # Should find connections between our test notes
        assert len(connections) > 0
        
        if connections:
            conn = connections[0]
            assert isinstance(conn, SemanticConnection)
            assert conn.source_note in ["note1", "note2"]
            assert conn.target_note in ["note1", "note2"]
            assert 0.0 <= conn.confidence <= 1.0
    
    def test_convert_to_link_suggestions(self, ai_linker):
        """Test conversion of semantic connections to link suggestions."""
        # Create a test connection
        connection = SemanticConnection(
            source_note="note1",
            target_note="note2", 
            relationship_type="related_concept",
            explanation="Both cover Python development",
            confidence=0.85,
            suggested_context="When discussing Python frameworks"
        )
        
        suggestions = ai_linker.convert_to_link_suggestions([connection])
        
        assert "note1" in suggestions
        assert "note2" in suggestions
        assert len(suggestions["note1"]) > 0
        
        suggestion = suggestions["note1"][0]
        assert suggestion.target_note == "note2"
        assert suggestion.confidence == 0.85
    
    def test_generate_semantic_report(self, ai_linker):
        """Test semantic analysis report generation."""
        connection = SemanticConnection(
            source_note="note1",
            target_note="note2",
            relationship_type="related_concept", 
            explanation="Test explanation",
            confidence=0.8,
            suggested_context="Test context"
        )
        
        report = ai_linker.generate_semantic_report([connection])
        
        assert "AI Semantic Link Discovery Report" in report
        assert "note1" in report
        assert "note2" in report
        assert "related_concept" in report
        assert "80%" in report
    
    def test_api_error_handling(self, mock_vault_path):
        """Test handling of OpenAI API errors."""
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI') as mock_openai:
            mock_client = MockOpenAIClient()
            mock_client.simulate_api_error()
            mock_openai.return_value = mock_client
            
            linker = AISemanticLinker(mock_vault_path)
            connections = linker.analyze_semantic_connections("Coding")
            
            # Should handle errors gracefully and return empty list
            assert isinstance(connections, list)
    
    def test_empty_vault_handling(self, tmp_path):
        """Test handling of empty vaults."""
        empty_vault = tmp_path / "empty_vault"
        empty_vault.mkdir()
        (empty_vault / "Coding").mkdir()
        
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI'):
            linker = AISemanticLinker(str(empty_vault))
            connections = linker.analyze_semantic_connections("Coding")
            
            assert connections == []
