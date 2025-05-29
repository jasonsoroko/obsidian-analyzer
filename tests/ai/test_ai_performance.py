"""Performance tests for AI functionality."""

import pytest
import time
from unittest.mock import patch
from pathlib import Path

from obsidian_analyzer import AISemanticLinker, ContentGapAnalyzer
from tests.mocks.mock_openai import MockOpenAIClient


class TestAIPerformance:
    """Test AI functionality performance characteristics."""
    
    @pytest.fixture
    def large_vault(self, tmp_path):
        """Create a large test vault for performance testing."""
        vault_path = tmp_path / "large_vault"
        coding_folder = vault_path / "Coding"
        coding_folder.mkdir(parents=True)
        
        # Create many test notes
        for i in range(20):  # 20 notes for performance testing
            note_content = f"""
# Test Note {i}
This is test note number {i} for performance testing.
It contains various topics like Python, testing, development.
#test #python #note{i}
            """
            (coding_folder / f"test_note_{i}.md").write_text(note_content)
        
        return str(vault_path)
    
    @patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI')
    def test_semantic_analysis_performance(self, mock_openai, large_vault):
        """Test semantic analysis performance with large vault."""
        mock_openai.return_value = MockOpenAIClient()
        
        linker = AISemanticLinker(large_vault)
        
        start_time = time.time()
        connections = linker.analyze_semantic_connections("Coding")
        analysis_time = time.time() - start_time
        
        # With 20 notes, we have 20*19/2 = 190 comparisons
        # Mocked calls should be fast, but set reasonable limit
        assert analysis_time < 10.0  # 10 seconds max for mocked calls
        assert isinstance(connections, list)
        
        print(f"Analyzed 20 notes in {analysis_time:.2f} seconds")
        print(f"Found {len(connections)} connections")
    
    @patch('obsidian_analyzer.content_gap_analyzer.openai.OpenAI')
    def test_gap_analysis_performance(self, mock_openai, large_vault):
        """Test content gap analysis performance."""
        mock_openai.return_value = MockOpenAIClient()
        
        analyzer = ContentGapAnalyzer(large_vault)
        
        start_time = time.time()
        gaps = analyzer.analyze_content_gaps("Coding")
        analysis_time = time.time() - start_time
        
        # Gap analysis should be faster as it makes fewer AI calls
        assert analysis_time < 5.0  # 5 seconds max
        assert isinstance(gaps, list)
        
        print(f"Gap analysis completed in {analysis_time:.2f} seconds")
        print(f"Found {len(gaps)} content gaps")
    
    def test_memory_usage_reasonable(self, large_vault):
        """Test that AI operations don't consume excessive memory."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI') as mock_openai:
            mock_openai.return_value = MockOpenAIClient()
            
            linker = AISemanticLinker(large_vault)
            connections = linker.analyze_semantic_connections("Coding")
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Should not use excessive memory (arbitrary limit for test)
            assert memory_increase < 200  # Less than 200MB increase
            assert isinstance(connections, list)
            
            print(f"Memory usage increased by {memory_increase:.1f}MB")
