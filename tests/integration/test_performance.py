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
