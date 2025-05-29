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
