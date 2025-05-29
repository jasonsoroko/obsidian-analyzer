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
