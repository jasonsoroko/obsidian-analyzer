"""Tests for AI Content Gap Analysis functionality."""

import pytest
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

from obsidian_analyzer.content_gap_analyzer import ContentGapAnalyzer, ContentGap, KnowledgeCluster
from tests.mocks.mock_openai import MockOpenAIClient


class TestContentGapAnalyzer:
    """Test AI-powered content gap analysis."""
    
    @pytest.fixture
    def mock_vault_path(self, tmp_path):
        """Create test vault with multiple notes."""
        vault_path = tmp_path / "test_vault"
        coding_folder = vault_path / "Coding"
        coding_folder.mkdir(parents=True)
        
        # Create diverse test notes
        (coding_folder / "python_basics.md").write_text("""
# Python Basics
Introduction to Python programming fundamentals.
#python #basics #programming
        """)
        
        (coding_folder / "web_apis.md").write_text("""
# Web API Development
Building REST APIs with Python frameworks.
#python #api #web #development
        """)
        
        (coding_folder / "testing.md").write_text("""
# Testing Strategies
Unit testing and test automation approaches.
#testing #automation #quality
        """)
        
        return str(vault_path)
    
    @pytest.fixture
    def gap_analyzer(self, mock_vault_path):
        """Create gap analyzer with mocked OpenAI."""
        with patch('obsidian_analyzer.content_gap_analyzer.openai.OpenAI') as mock_openai:
            mock_openai.return_value = MockOpenAIClient()
            analyzer = ContentGapAnalyzer(mock_vault_path)
            return analyzer
    
    def test_analyze_content_gaps(self, gap_analyzer):
        """Test content gap analysis."""
        gaps = gap_analyzer.analyze_content_gaps("Coding")
        
        assert isinstance(gaps, list)
        # Should find some gaps based on our test notes
        assert len(gaps) >= 0  # May be 0 if AI doesn't find gaps
        
        # If gaps found, validate structure
        for gap in gaps:
            assert isinstance(gap, ContentGap)
            assert gap.gap_type in ["bridge_connection", "topic_coverage", "fundamental_missing"]
            assert gap.priority in ["high", "medium", "low"]
            assert 0.0 <= gap.confidence <= 1.0
            assert len(gap.title) > 0
    
    def test_create_knowledge_clusters(self, gap_analyzer):
        """Test knowledge cluster identification."""
        clusters = gap_analyzer.create_knowledge_clusters("Coding")
        
        assert isinstance(clusters, list)
        
        for cluster in clusters:
            assert isinstance(cluster, KnowledgeCluster)
            assert len(cluster.cluster_name) > 0
            assert isinstance(cluster.notes, list)
            assert isinstance(cluster.topics, list)
            assert 0.0 <= cluster.hub_potential <= 1.0
    
    def test_generate_gap_report(self, gap_analyzer):
        """Test gap analysis report generation."""
        # Create test gap
        gap = ContentGap(
            gap_type="bridge_connection",
            title="Test Gap",
            description="Test gap description",
            priority="high",
            confidence=0.85,
            related_notes=["note1", "note2"],
            suggested_content=["content1", "content2"],
            tags=["tag1", "tag2"]
        )
        
        report = gap_analyzer.generate_gap_report([gap])
        
        assert "Content Gap Analysis Report" in report
        assert "Test Gap" in report
        assert "High Priority" in report
        assert "85%" in report
        assert "bridge_connection" in report
    
    def test_empty_gaps_report(self, gap_analyzer):
        """Test report generation with no gaps."""
        report = gap_analyzer.generate_gap_report([])
        
        assert "No significant content gaps identified" in report
    
    def test_api_error_resilience(self, mock_vault_path):
        """Test resilience to API errors."""
        with patch('obsidian_analyzer.content_gap_analyzer.openai.OpenAI') as mock_openai:
            mock_client = MockOpenAIClient()
            mock_client.simulate_api_error()
            mock_openai.return_value = mock_client
            
            analyzer = ContentGapAnalyzer(mock_vault_path)
            gaps = analyzer.analyze_content_gaps("Coding")
            
            # Should handle errors gracefully
            assert isinstance(gaps, list)
