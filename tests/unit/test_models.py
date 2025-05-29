"""Unit tests for data models."""

import pytest
from obsidian_analyzer.models import LinkSuggestion, StructureSuggestion


class TestLinkSuggestion:
    def test_creation(self):
        suggestion = LinkSuggestion(
            target_note="Test Note",
            context_snippets=["context 1", "context 2"],
            confidence=0.8,
            mention_count=2
        )
        assert suggestion.target_note == "Test Note"
        assert suggestion.confidence == 0.8
        assert suggestion.mention_count == 2
        assert len(suggestion.context_snippets) == 2
    
    def test_string_representation(self):
        suggestion = LinkSuggestion(
            target_note="Test Note",
            context_snippets=["context"],
            confidence=0.75,
            mention_count=1
        )
        assert "Test Note" in str(suggestion)
        assert "75" in str(suggestion)


class TestStructureSuggestion:
    def test_creation(self):
        suggestion = StructureSuggestion(
            suggestion_type="add_headings",
            description="Add headings to improve structure",
            examples=["## Introduction", "## Conclusion"]
        )
        assert suggestion.suggestion_type == "add_headings"
        assert suggestion.description == "Add headings to improve structure"
        assert len(suggestion.examples) == 2
    
    def test_string_representation(self):
        suggestion = StructureSuggestion(
            suggestion_type="add_headings",
            description="Test description"
        )
        assert "add_headings" in str(suggestion)
        assert "Test description" in str(suggestion)
