"""Obsidian Analyzer - Analyze and improve Obsidian vault structure."""

from .analyzer import CodingFolderAnalyzer, analyze_coding_folder, get_recommendations_for_note
from .models import LinkSuggestion, StructureSuggestion

__version__ = "0.1.0"
__all__ = [
    "CodingFolderAnalyzer",
    "analyze_coding_folder", 
    "get_recommendations_for_note",
    "LinkSuggestion",
    "StructureSuggestion"
]