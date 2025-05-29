"""Unit tests for the core analyzer."""

import pytest
import tempfile
import os
from pathlib import Path
from obsidian_analyzer.analyzer import CodingFolderAnalyzer


class TestCodingFolderAnalyzer:
    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            coding_folder = vault_path / "Coding"
            coding_folder.mkdir()
            
            # Create test files
            (coding_folder / "test1.md").write_text("""
# Test Note 1
This mentions [[test2]] and has #python content.
```python
print("hello")
```
            """)
            
            (coding_folder / "test2.md").write_text("""
# Test Note 2
This has some content and mentions [[test1]].
## Section
More content here.
            """)
            
            yield str(vault_path)
    
    def test_initialization(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        assert analyzer.vault_path == Path(temp_vault)
        assert analyzer.coding_folder == Path(temp_vault) / "Coding"
    
    def test_load_notes(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        analyzer.load_coding_notes()
        
        assert len(analyzer.notes) == 2
        assert "test1" in analyzer.notes
        assert "test2" in analyzer.notes
        
        # Check note data
        test1 = analyzer.notes["test1"]
        assert test1["word_count"] > 0
        assert "test2" in test1["links"]
        assert ("languages", "python") in test1["topics"]
    
    def test_extract_links(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = "This has [[link1]] and [[link2|display text]] links."
        links = analyzer.extract_links(content)
        
        assert "link1" in links
        assert "link2" in links
        assert len(links) == 2
    
    def test_extract_tags(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = "Content with #tag1 and #tag2/subtag tags."
        tags = analyzer.extract_tags(content)
        
        assert "tag1" in tags
        assert "tag2/subtag" in tags
    
    def test_extract_headings(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        
        content = """# Main Heading
## Sub Heading
### Sub Sub Heading"""
        headings = analyzer.extract_headings(content)
        
        assert len(headings) == 3
        assert headings[0] == (1, "Main Heading")
        assert headings[1] == (2, "Sub Heading")
        assert headings[2] == (3, "Sub Sub Heading")
    
    def test_link_suggestions(self, temp_vault):
        analyzer = CodingFolderAnalyzer(temp_vault)
        analyzer.load_coding_notes()
        
        suggestions = analyzer.find_link_suggestions("test1")
        assert isinstance(suggestions, list)
        # Should find suggestions based on content analysis
