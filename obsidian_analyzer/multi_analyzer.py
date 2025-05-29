"""Multi-Folder Analyzer for Obsidian Vaults - Analyze entire vault structure."""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime

from .analyzer import CodingFolderAnalyzer


@dataclass
class FolderStats:
    name: str
    note_count: int
    total_words: int
    total_links: int
    orphaned_notes: int
    notes_with_code: int
    top_topics: List[str]
    notes: List[str]


@dataclass
class VaultAnalysis:
    vault_path: str
    analysis_date: str
    total_folders: int
    total_notes: int
    total_words: int
    total_links: int
    global_orphaned_notes: int
    folder_stats: List[FolderStats]
    cross_folder_suggestions: Dict[str, List[str]]
    vault_health_score: float


class MultiVaultAnalyzer:
    """Analyze entire Obsidian vault across all folders."""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.folder_analyzers = {}
        self.all_notes = {}
        self.global_backlinks = defaultdict(set)
        
    def discover_folders(self) -> List[str]:
        """Find all folders with markdown files."""
        folders = []
        exclude_patterns = ['.obsidian', '.git', '.vscode', '__pycache__', 'node_modules']
        
        for root, dirs, files in os.walk(self.vault_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            # Check if this directory has markdown files
            md_files = [f for f in files if f.endswith('.md')]
            if md_files:
                folder_path = Path(root)
                folder_name = folder_path.relative_to(self.vault_path).as_posix()
                if folder_name == '.':
                    folder_name = 'Root'
                folders.append(folder_name)
        
        return sorted(folders)
    
    def analyze_folder(self, folder_name: str) -> Optional[FolderStats]:
        """Analyze a specific folder using adapted CodingFolderAnalyzer."""
        if folder_name == 'Root':
            folder_path = self.vault_path
        else:
            folder_path = self.vault_path / folder_name
            
        if not folder_path.exists():
            return None
            
        # Create a modified analyzer for this folder
        analyzer = CodingFolderAnalyzer(str(self.vault_path))
        analyzer.coding_folder = folder_path
        
        # Load notes from this specific folder
        try:
            analyzer.load_coding_notes()
        except Exception as e:
            print(f"⚠️  Error analyzing {folder_name}: {e}")
            return None
            
        if not analyzer.notes:
            return None
            
        # Store analyzer and notes for cross-folder analysis
        self.folder_analyzers[folder_name] = analyzer
        for note_name, note_data in analyzer.notes.items():
            full_note_name = f"{folder_name}/{note_name}"
            self.all_notes[full_note_name] = note_data
            
            # Build global backlinks
            for link in note_data['links']:
                self.global_backlinks[link].add(full_note_name)
        
        # Calculate folder stats
        total_words = sum(note['word_count'] for note in analyzer.notes.values())
        total_links = sum(len(note['links']) for note in analyzer.notes.values())
        notes_with_code = len([n for n in analyzer.notes.values() if n['code_blocks']])
        
        # Find orphaned notes in this folder
        orphaned = []
        for note_name in analyzer.notes:
            has_incoming = len(self.global_backlinks.get(note_name, set())) > 0
            has_outgoing = len(analyzer.notes[note_name]['links']) > 0
            if not has_incoming and not has_outgoing:
                orphaned.append(note_name)
        
        # Get top topics
        all_topics = Counter()
        for note in analyzer.notes.values():
            for category, topic in note['topics']:
                all_topics[f"{category}:{topic}"] += 1
        
        return FolderStats(
            name=folder_name,
            note_count=len(analyzer.notes),
            total_words=total_words,
            total_links=total_links,
            orphaned_notes=len(orphaned),
            notes_with_code=notes_with_code,
            top_topics=[topic for topic, _ in all_topics.most_common(5)],
            notes=list(analyzer.notes.keys())
        )
    
    def find_cross_folder_connections(self) -> Dict[str, List[str]]:
        """Find potential connections between notes in different folders."""
        cross_connections = defaultdict(list)
        
        for folder1, analyzer1 in self.folder_analyzers.items():
            for note_name1, note_data1 in analyzer1.notes.items():
                content_lower = note_data1['content'].lower()
                
                # Look for mentions of notes from other folders
                for folder2, analyzer2 in self.folder_analyzers.items():
                    if folder1 == folder2:
                        continue
                        
                    for note_name2 in analyzer2.notes:
                        # Skip if already linked
                        if note_name2 in note_data1['links']:
                            continue
                            
                        # Look for mentions
                        if note_name2.lower() in content_lower:
                            cross_connections[f"{folder1}/{note_name1}"].append(f"{folder2}/{note_name2}")
        
        return dict(cross_connections)
    
    def calculate_vault_health_score(self, folder_stats: List[FolderStats]) -> float:
        """Calculate overall vault health score (0-100)."""
        if not folder_stats:
            return 0.0
        
        total_notes = sum(fs.note_count for fs in folder_stats)
        if total_notes == 0:
            return 0.0
        
        # Factor 1: Linking ratio (notes with links vs total notes)
        total_links = sum(fs.total_links for fs in folder_stats)
        linking_ratio = min(total_links / total_notes, 1.0)  # Cap at 1.0
        
        # Factor 2: Orphaned notes ratio (lower is better)
        total_orphaned = sum(fs.orphaned_notes for fs in folder_stats)
        orphaned_ratio = 1 - (total_orphaned / total_notes)
        
        # Factor 3: Structure (notes with code/content)
        total_with_code = sum(fs.notes_with_code for fs in folder_stats)
        structure_ratio = total_with_code / total_notes
        
        # Factor 4: Folder diversity (more folders = better organization)
        folder_diversity = min(len(folder_stats) / 5, 1.0)  # Normalize to max 5 folders
        
        # Weighted average
        health_score = (
            linking_ratio * 0.3 +
            orphaned_ratio * 0.3 +
            structure_ratio * 0.2 +
            folder_diversity * 0.2
        ) * 100
        
        return round(health_score, 1)
    
    def analyze_entire_vault(self, folders: Optional[List[str]] = None) -> VaultAnalysis:
        """Perform complete vault analysis."""
        print("🔍 Starting comprehensive vault analysis...")
        
        # Discover folders
        discovered_folders = self.discover_folders()
        if folders:
            # Use only specified folders
            folders_to_analyze = [f for f in folders if f in discovered_folders]
        else:
            folders_to_analyze = discovered_folders
        
        print(f"📁 Found {len(discovered_folders)} folders, analyzing {len(folders_to_analyze)}")
        
        # Analyze each folder
        folder_stats = []
        for folder_name in folders_to_analyze:
            print(f"📝 Analyzing folder: {folder_name}")
            stats = self.analyze_folder(folder_name)
            if stats:
                folder_stats.append(stats)
        
        if not folder_stats:
            print("❌ No analyzable folders found")
            return None
        
        # Find cross-folder connections
        print("🌉 Finding cross-folder connections...")
        cross_connections = self.find_cross_folder_connections()
        
        # Calculate health score
        print("💪 Calculating vault health score...")
        health_score = self.calculate_vault_health_score(folder_stats)
        
        # Global stats
        total_notes = sum(fs.note_count for fs in folder_stats)
        total_words = sum(fs.total_words for fs in folder_stats)
        total_links = sum(fs.total_links for fs in folder_stats)
        global_orphaned = sum(fs.orphaned_notes for fs in folder_stats)
        
        return VaultAnalysis(
            vault_path=str(self.vault_path),
            analysis_date=datetime.now().isoformat(),
            total_folders=len(folder_stats),
            total_notes=total_notes,
            total_words=total_words,
            total_links=total_links,
            global_orphaned_notes=global_orphaned,
            folder_stats=folder_stats,
            cross_folder_suggestions=cross_connections,
            vault_health_score=health_score
        )
    
    def export_markdown_report(self, analysis: VaultAnalysis, output_path: Optional[str] = None) -> str:
        """Export analysis results to markdown report."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/vault_analysis_{timestamp}.md"
        
        report = []
        report.append("# 🔍 Obsidian Vault Analysis Report")
        report.append("")
        report.append(f"**Generated:** {analysis.analysis_date}")
        report.append(f"**Vault Path:** `{analysis.vault_path}`")
        report.append(f"**Health Score:** {analysis.vault_health_score}/100 {'🟢' if analysis.vault_health_score >= 70 else '🟡' if analysis.vault_health_score >= 40 else '🔴'}")
        report.append("")
        
        # Overview
        report.append("## 📊 Overview")
        report.append("")
        report.append(f"| Metric | Value |")
        report.append(f"|--------|-------|")
        report.append(f"| Total Folders | {analysis.total_folders} |")
        report.append(f"| Total Notes | {analysis.total_notes} |")
        report.append(f"| Total Words | {analysis.total_words:,} |")
        report.append(f"| Total Links | {analysis.total_links} |")
        report.append(f"| Orphaned Notes | {analysis.global_orphaned_notes} |")
        report.append("")
        
        # Folder breakdown
        report.append("## 📁 Folder Analysis")
        report.append("")
        
        # Sort folders by note count
        sorted_folders = sorted(analysis.folder_stats, key=lambda x: x.note_count, reverse=True)
        
        for folder in sorted_folders:
            report.append(f"### 📂 {folder.name}")
            report.append("")
            report.append(f"- **Notes:** {folder.note_count}")
            report.append(f"- **Words:** {folder.total_words:,}")
            report.append(f"- **Links:** {folder.total_links}")
            report.append(f"- **Orphaned:** {folder.orphaned_notes}")
            report.append(f"- **With Code:** {folder.notes_with_code}")
            
            if folder.top_topics:
                report.append(f"- **Top Topics:** {', '.join(folder.top_topics)}")
            
            if len(folder.notes) <= 10:
                report.append(f"- **Notes:** {', '.join(folder.notes)}")
            else:
                report.append(f"- **Sample Notes:** {', '.join(folder.notes[:5])} (and {len(folder.notes)-5} more)")
            
            report.append("")
        
        # Cross-folder connections
        if analysis.cross_folder_suggestions:
            report.append("## 🌉 Cross-Folder Connection Opportunities")
            report.append("")
            
            # Show top 10 cross-folder opportunities
            for note, suggestions in list(analysis.cross_folder_suggestions.items())[:10]:
                report.append(f"**{note}** could link to:")
                for suggestion in suggestions[:3]:
                    report.append(f"- {suggestion}")
                report.append("")
        
        # Health recommendations
        report.append("## 💡 Recommendations")
        report.append("")
        
        if analysis.vault_health_score >= 80:
            report.append("🎉 **Excellent Health Score!** Your vault is well-connected and organized.")
        elif analysis.vault_health_score >= 60:
            report.append("👍 **Good Health Score** - Your vault has solid structure with room for improvement.")
        elif analysis.vault_health_score >= 40:
            report.append("⚠️ **Moderate Health Score** - Your vault needs some attention.")
        else:
            report.append("🚨 **Low Health Score** - Your vault needs significant improvement.")
        
        report.append("")
        
        # Specific recommendations
        if analysis.global_orphaned_notes > analysis.total_notes * 0.2:
            report.append(f"- 🔗 **Connect Orphaned Notes:** {analysis.global_orphaned_notes} notes have no connections ({analysis.global_orphaned_notes/analysis.total_notes*100:.1f}% of vault)")
        
        if len(analysis.cross_folder_suggestions) > 0:
            report.append(f"- 🌉 **Cross-Folder Linking:** Found {len(analysis.cross_folder_suggestions)} opportunities to connect folders")
        
        if analysis.total_links < analysis.total_notes * 0.5:
            report.append(f"- 📎 **Increase Linking:** Average of {analysis.total_links/analysis.total_notes:.1f} links per note (aim for 2-3)")
        
        report_content = "\n".join(report)
        
        # Ensure reports directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Analysis report exported to: {output_path}")
        return output_path


def analyze_vault_main():
    """Main function for vault analysis."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m obsidian_analyzer.multi_analyzer /path/to/vault [folder1] [folder2] ...")
        return
    
    vault_path = sys.argv[1]
    specific_folders = sys.argv[2:] if len(sys.argv) > 2 else None
    
    analyzer = MultiVaultAnalyzer(vault_path)
    analysis = analyzer.analyze_entire_vault(specific_folders)
    
    if not analysis:
        print("❌ Analysis failed")
        return
    
    # Display summary
    print(f"\n📊 VAULT ANALYSIS COMPLETE")
    print(f"=" * 50)
    print(f"🏥 Health Score: {analysis.vault_health_score}/100")
    print(f"📁 Total Folders: {analysis.total_folders}")
    print(f"📝 Total Notes: {analysis.total_notes}")
    print(f"📊 Total Words: {analysis.total_words:,}")
    print(f"🔗 Total Links: {analysis.total_links}")
    print(f"👻 Orphaned Notes: {analysis.global_orphaned_notes}")
    print(f"🌉 Cross-Folder Opportunities: {len(analysis.cross_folder_suggestions)}")
    
    # Export report
    report_path = analyzer.export_markdown_report(analysis)
    print(f"📄 Full report saved to: {report_path}")


if __name__ == "__main__":
    analyze_vault_main()
