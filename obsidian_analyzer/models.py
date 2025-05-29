"""Data models for Obsidian Analyzer."""

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LinkSuggestion:
   """Represents a suggested link between notes."""
   target_note: str
   context_snippets: List[str]
   confidence: float
   mention_count: int
   
   def __str__(self):
       return f"Link to [[{self.target_note}]] (confidence: {self.confidence:.1%})"

@dataclass
class StructureSuggestion:
   """Represents a suggestion for improving note structure."""
   suggestion_type: str
   description: str
   examples: Optional[List[str]] = None
   
   def __str__(self):
       return f"{self.suggestion_type}: {self.description}"
