"""Unit tests for auto-linker."""

import pytest
import tempfile
import shutil
from pathlib import Path
from obsidian_analyzer.auto_linker import AutoLinker


class TestAutoLinker:
    @pytest.fixture
    def test_vault_path(self):
        """Create a temporary test vault."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            coding_folder = vault_path / "Coding"
            coding_folder.mkdir()
            
            # Create test files
            (coding_folder / "note1.md").write_text("""
# Note 1
This mentions note2 without linking.
Also talks about note3 concepts.
            """)
            
            (coding_folder / "note2.md").write_text("""
# Note 2
This is the target note.
            """)
            
            (coding_folder / "note3.md").write_text("""
# Note 3
Another target note.
            """)
            
            yield str(vault_path)
    
    def test_initialization(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        assert linker.vault_path == Path(test_vault_path)
        assert not linker.backup
    
    def test_analyze_and_suggest_links(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        suggestions = linker.analyze_and_suggest_links("Coding")

        assert isinstance(suggestions, dict)
        # Should find suggestions for note1 mentioning note2/note3
        assert "note1" in suggestions
        assert any(s.target_note == "note2" for s in suggestions["note1"])
    
    def test_dry_run_mode(self, test_vault_path):
        linker = AutoLinker(test_vault_path, backup=False)
        results = linker.auto_link_folder("Coding", dry_run=True)
        
        # Should return results without modifying files
        assert isinstance(results, dict)
        
        # Verify files weren't actually modified
        note1_path = Path(test_vault_path) / "Coding" / "note1.md"
        content = note1_path.read_text()
        assert "[[note2]]" not in content  # Should not be modified in dry run
