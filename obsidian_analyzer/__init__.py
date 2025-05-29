"""Obsidian Analyzer - Analyze and improve Obsidian vault structure."""

from .analyzer import CodingFolderAnalyzer, analyze_coding_folder, get_recommendations_for_note
from .auto_linker import AutoLinker
from .multi_analyzer import MultiVaultAnalyzer, VaultAnalysis, FolderStats

__version__ = "0.1.0"
from .safe_auto_linker import SafeAutoLinker, SafetyLevel
from .safe_auto_linker import SafeAutoLinker, SafetyLevel
from .ai_semantic_linker import AISemanticLinker, SemanticConnection
from .content_gap_analyzer import ContentGapAnalyzer, ContentGap, KnowledgeCluster
