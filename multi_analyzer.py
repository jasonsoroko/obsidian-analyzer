
"""
Multi-Folder Analyzer for Obsidian Vaults
Analyzes entire vault structure, not just single folders.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from datetime import datetime

from .models import LinkSuggestion, StructureSuggestion


@dataclass
class FolderStats:
    """Statistics for a single folder."""
    name: str
    path: str
    note_count: int
    total_words: int
    total_links: int
    orphaned_notes: int
    notes_with_code: int
    common_topics: List[Tuple[str, int]]
    notes: List[str]


@dataclass  
class VaultAnalysis:
    """Complete vault analysis results."""
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
        self.all_notes = {}  # note_name -> note_data
        self.folder_notes = defaultdict(dict)  # folder -> {note_name -> note_data}
        self.global_backlinks = defaultdict(set)
        self.code_patterns = {
            'languages': ['python', 'javascript', 'java', 'cpp', 'rust', 'go', 'ruby', 'php', 'swift', 'kotlin', 'typescript', 'c#', 'scala', 'r'],
            'frameworks': ['react', 'django', 'flask', 'spring', 'express', 'vue', 'angular', 'laravel', 'rails', 'nextjs', 'nuxt'],
            'concepts': ['algorithm', 'data structure', 'design pattern', 'api', 'database', 'testing', 'debugging', 'optimization', 'security'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'terraform', 'ansible', 'webpack', 'babel']
        }
    
    def discover_folders(self, exclude_patterns: Optional[List[str]] = None) -> List[Path]:
        """Discover all folders in the vault that contain markdown files."""
        if exclude_patterns is None:
            exclude_patterns = ['.obsidian', '.git', '.vscode', '__pycache__', 'node_modules']
        
        folders_with_notes = []
        
        for root, dirs, files in os.walk(self.vault_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            # Check if this directory has markdown files
            md_files = [f for f in files if f.endswith('.md')]
            if md_files:
                folder_path = Path(root)
                folders_with_notes.append(folder_path)
        
        return folders_with_notes
    
    def load_all_notes(self, folders: Optional[List[str]] = None) -> None:
        """Load all notes from specified folders or auto-discover."""
        if folders:
            folder_paths = [self.vault_path / folder for folder in folders]
        else:
            folder_paths = self.discover_folders()
        
        print(f"🔍 Discovering folders in vault...")
        print(f"📁 Found {len(folder_paths)} folders with notes")
        
        for folder_path in folder_paths:
            folder_name = folder_path.relative_to(self.vault_path).as_posix()
            if folder_name == '.':
                folder_name = 'Root'
            
            folder_notes = self._load_folder_notes(folder_path, folder_name)
            if folder_notes:
                self.folder_notes[folder_name] = folder_notes
                self.all_notes.update(folder_notes)
                print(f"  📝 {folder_name}: {len(folder_notes)} notes")
    
    def _load_folder_notes(self, folder_path: Path, folder_name: str) -> Dict[str, dict]:
        """Load all notes from a specific folder."""
        notes = {}
        
        for md_file in folder_path.glob("**/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                note_name = md_file.stem
                relative_path = md_file.relative_to(self.vault_path)
                
                notes[note_name] = {
                    'path': md_file,
                    'relative_path': relative_path,
                    'folder': folder_name,
                    'content': content,
                    'word_count': len(content.split()),
                    'lines': content.count('\n') + 1,
                    'links': self._extract_links(content),
                    'tags': self._extract_tags(content),
                    'headings': self._extract_headings(content),
                    'code_blocks': self._extract_code_blocks(content),
                    'topics': self._identify_topics(content)
                }
            except Exception as e:
                print(f"⚠️  Error reading {md_file}: {e}")
                
        return notes
    
    def _extract_links(self, content: str) -> Set[str]:
        """Extract wikilinks from content."""
        import re
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        return set(links)
    
    def _extract_tags(self, content: str) -> Set[str]:
        """Extract hashtags from content."""
        import re
        tags = re.findall(r'#(\w+(?:/\w+)*)', content)
        return set(tags)
    
    def _extract_headings(self, content: str) -> List[Tuple[int, str]]:
        """Extract markdown headings."""
        import re
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        return [(len(h[0]), h[1].strip()) for h in headings]
    
    def _extract_code_blocks(self, content: str) -> List[Tuple[str, str]]:
        """Extract code blocks with language info."""
        import re
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        code_blocks.extend(re.findall(r'~~~(\w+)?\n(.*?)\n~~~', content, re.DOTALL))
        return code_blocks
    
    def _identify_topics(self, content: str) -> Set[Tuple[str, str]]:
        """Identify topics mentioned in content."""
        content_lower = content.lower()
        topics = set()
        
        for category, items in self.code_patterns.items():
            for item in items:
                if item in content_lower:
                    topics.add((category, item))
        
        return topics
    
    def build_global_backlinks(self) -> None:
        """Build backlink graph across entire vault."""
        for note_name, note_data in self.all_notes.items():
            for link in note_data['links']:
                if link in self.all_notes:
                    self.global_backlinks[link].add(note_name)
    
    def analyze_folder(self, folder_name: str) -> FolderStats:
        """Analyze a specific folder."""
        if folder_name not in self.folder_notes:
            return None
        
        notes = self.folder_notes[folder_name]
        
        # Calculate stats
        total_words = sum(note['word_count'] for note in notes.values())
        total_links = sum(len(note['links']) for note in notes.values())
        notes_with_code = len([n for n in notes.values() if n['code_blocks']])
        
        # Find orphaned notes (no incoming or outgoing links)
        orphaned = set()
        for note_name in notes:
            has_incoming = len(self.global_backlinks[note_name]) > 0
            has_outgoing = len(notes[note_name]['links']) > 0
            if not has_incoming and not has_outgoing:
                orphaned.add(note_name)
        
        # Common topics
        all_topics = Counter()
        for note in notes.values():
            for category, topic in note['topics']:
                all_topics[f"{category}:{topic}"] += 1
        
        return FolderStats(
            name=folder_name,
            path=str(self.vault_path / folder_name if folder_name != 'Root' else self.vault_path),
            note_count=len(notes),
            total_words=total_words,
            total_links=total_links,
            orphaned_notes=len(orphaned),
            notes_with_code=notes_with_code,
            common_topics=all_topics.most_common(10),
            notes=list(notes.keys())
        )
    
    def find_cross_folder_connections(self) -> Dict[str, List[str]]:
        """Find potential connections between notes in different folders."""
        cross_connections = defaultdict(list)
        
        for note_name, note_data in self.all_notes.items():
            current_folder = note_data['folder']
            content_lower = note_data['content'].lower()
            
            # Look for mentions of notes from other folders
            for other_name, other_data in self.all_notes.items():
                if other_name == note_name:
                    continue
                    
                other_folder = other_data['folder']
                if other_folder == current_folder:
                    continue
                
                # Skip if already linked
                if other_name in note_data['links']:
                    continue
                
                # Look for mentions
                if other_name.lower() in content_lower:
                    cross_connections[note_name].append(f"{other_name} (in {other_folder})")
        
        return dict(cross_connections)
    
    def calculate_vault_health_score(self) -> float:
        """Calculate overall vault health score (0-100)."""
        if not self.all_notes:
            return 0.0
        
        total_notes = len(self.all_notes)
        
        # Factor 1: Linking ratio (notes with links vs total notes)
        notes_with_links = sum(1 for note in self.all_notes.values() if note['links'])
        linking_ratio = notes_with_links / total_notes
        
        # Factor 2: Orphaned notes ratio (lower is better)
        orphaned_count = sum(1 for note_name in self.all_notes 
                           if not self.global_backlinks[note_name] and not self.all_notes[note_name]['links'])
        orphaned_ratio = 1 - (orphaned_count / total_notes)
        
        # Factor 3: Cross-folder connections
        cross_connections = self.find_cross_folder_connections()
        cross_ratio = len(cross_connections) / total_notes if cross_connections else 0
        
        # Factor 4: Structure (notes with headings)
        structured_notes = sum(1 for note in self.all_notes.values() if note['headings'])
        structure_ratio = structured_notes / total_notes
        
        # Weighted average
        health_score = (
            linking_ratio * 0.3 +
            orphaned_ratio * 0.3 +
            cross_ratio * 0.2 +
            structure_ratio * 0.2
        ) * 100
        
        return round(health_score, 1)
    
    def analyze_entire_vault(self, folders: Optional[List[str]] = None) -> VaultAnalysis:
        """Perform complete vault analysis."""
        print("🔍 Starting comprehensive vault analysis...")
        
        # Load all notes
        self.load_all_notes(folders)
        
        if not self.all_notes:
            print("❌ No notes found in vault")
            return None
        
        # Build global backlinks
        print("🔗 Building global backlink graph...")
        self.build_global_backlinks()
        
        # Analyze each folder
        print("📊 Analyzing individual folders...")
        folder_stats = []
        for folder_name in self.folder_notes:
            stats = self.analyze_folder(folder_name)
            if stats:
                folder_stats.append(stats)
        
        # Find cross-folder connections
        print("🌉 Finding cross-folder connections...")
        cross_connections = self.find_cross_folder_connections()
        
        # Calculate health score
        print("💪 Calculating vault health score...")
        health_score = self.calculate_vault_health_score()
        
        # Global stats
        total_words = sum(note['word_count'] for note in self.all_notes.values())
        total_links = sum(len(note['links']) for note in self.all_notes.values())
        global_orphaned = sum(1 for note_name in self.all_notes 
                            if not self.global_backlinks[note_name] and not self.all_notes[note_name]['links'])
        
        return VaultAnalysis(
            vault_path=str(self.vault_path),
            analysis_date=datetime.now().isoformat(),
            total_folders=len(self.folder_notes),
            total_notes=len(self.all_notes),
            total_words=total_words,
            total_links=total_links,
            global_orphaned_notes=global_orphaned,
            folder_stats=folder_stats,
            cross_folder_suggestions=cross_connections,
            vault_health_score=health_score
        )
    
    def export_analysis_report(self, analysis: VaultAnalysis, output_path: Optional[str] = None) -> str:
        """Export analysis results to markdown report."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"vault_analysis_{timestamp}.md"
        
        report = []
        report.append(f"# Obsidian Vault Analysis Report")
        report.append(f"")
        report.append(f"**Generated:** {analysis.analysis_date}")
        report.append(f"**Vault Path:** `{analysis.vault_path}`")
        report.append(f"**Health Score:** {analysis.vault_health_score}/100")
        report.append(f"")
        
        # Overview
        report.append(f"## 📊 Overview")
        report.append(f"")
        report.append(f"- **Total Folders:** {analysis.total_folders}")
        report.append(f"- **Total Notes:** {analysis.total_notes}")
        report.append(f"- **Total Words:** {analysis.total_words:,}")
        report.append(f"- **Total Links:** {analysis.total_links}")
        report.append(f"- **Orphaned Notes:** {analysis.global_orphaned_notes}")
        report.append(f"")
        
        # Folder breakdown
        report.append(f"## 📁 Folder Analysis")
        report.append(f"")
        for folder in sorted(analysis.folder_stats, key=lambda x: x.note_count, reverse=True):
            report.append(f"### {folder.name}")
            report.append(f"")
            report.append(f"- **Notes:** {folder.note_count}")
            report.append(f"- **Words:** {folder.total_words:,}")
            report.append(f"- **Links:** {folder.total_links}")
            report.append(f"- **Orphaned:** {folder.orphaned_notes}")
            report.append(f"- **With Code:** {folder.notes_with_code}")
            
            if folder.common_topics:
                report.append(f"- **Top Topics:** {', '.join([t[0] for t in folder.common_topics[:5]])}")
            report.append(f"")
        
        # Cross-folder connections
        if analysis.cross_folder_suggestions:
            report.append(f"## 🌉 Cross-Folder Connection Opportunities")
            report.append(f"")
            for note, suggestions in list(analysis.cross_folder_suggestions.items())[:10]:
                report.append(f"**{note}** could link to:")
                for suggestion in suggestions[:3]:
                    report.append(f"- {suggestion}")
                report.append(f"")
        
        # Health recommendations
        report.append(f"## 💡 Recommendations")
        report.append(f"")
        
        if analysis.vault_health_score < 50:
            report.append(f"⚠️ **Low Health Score** - Your vault needs attention!")
        elif analysis.vault_health_score < 75:
            report.append(f"📈 **Moderate Health Score** - Good foundation with room for improvement.")
        else:
            report.append(f"✅ **High Health Score** - Well-connected vault with good structure!")
        
        report.append(f"")
        if analysis.global_orphaned_notes > analysis.total_notes * 0.2:
            report.append(f"- **Connect Orphaned Notes:** {analysis.global_orphaned_notes} notes have no connections")
        
        if len(analysis.cross_folder_suggestions) > 0:
            report.append(f"- **Cross-Folder Linking:** Found {len(analysis.cross_folder_suggestions)} opportunities")
        
        report_content = "\n".join(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 Analysis report exported to: {output_path}")
        return output_path
    
    def get_folder_suggestions(self, folder_name: str) -> List[Dict]:
        """Get specific suggestions for improving a folder."""
        if folder_name not in self.folder_notes:
            return []
        
        notes = self.folder_notes[folder_name]
        suggestions = []
        
        # Find orphaned notes
        orphaned = []
        for note_name in notes:
            has_incoming = len(self.global_backlinks[note_name]) > 0
            has_outgoing = len(notes[note_name]['links']) > 0
            if not has_incoming and not has_outgoing:
                orphaned.append(note_name)
        
        if orphaned:
            suggestions.append({
                'type': 'orphaned_notes',
                'title': f'Connect {len(orphaned)} orphaned notes',
                'notes': orphaned,
                'priority': 'high'
            })
        
        # Find notes without structure
        unstructured = [name for name, data in notes.items() 
                       if data['word_count'] > 200 and not data['headings']]
        
        if unstructured:
            suggestions.append({
                'type': 'add_structure',
                'title': f'Add headings to {len(unstructured)} long notes',
                'notes': unstructured[:5],
                'priority': 'medium'
            })
        
        return suggestions


def analyze_vault_cli():
    """Command-line interface for vault analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze entire Obsidian vault")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folders", nargs="+", help="Specific folders to analyze (optional)")
    parser.add_argument("--output", help="Output file for report (optional)")
    parser.add_argument("--json", action="store_true", help="Export as JSON instead of markdown")
    
    args = parser.parse_args()
    
    analyzer = MultiVaultAnalyzer(args.vault_path)
    analysis = analyzer.analyze_entire_vault(args.folders)
    
    if not analysis:
        print("❌ Analysis failed")
        return
    
    # Display summary
    print(f"\n📊 VAULT ANALYSIS COMPLETE")
    print(f"=" * 50)
    print(f"Health Score: {analysis.vault_health_score}/100")
    print(f"Total Notes: {analysis.total_notes}")
    print(f"Total Folders: {analysis.total_folders}")
    print(f"Orphaned Notes: {analysis.global_orphaned_notes}")
    print(f"Cross-Folder Opportunities: {len(analysis.cross_folder_suggestions)}")
    
    # Export report
    if args.json:
        output_file = args.output or f"vault_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(asdict(analysis), f, indent=2, default=str)
        print(f"📄 JSON report exported to: {output_file}")
    else:
        output_file = analyzer.export_analysis_report(analysis, args.output)


if __name__ == "__main__":
    analyze_vault_cli()