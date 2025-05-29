#!/bin/zsh

# Auto-Link Tool Builder Script for Obsidian Analyzer
# Run this in your VS Code terminal from the Obsidian_Analyzer directory

set -e  # Exit on any error

echo "🚀 Building Auto-Link Insertion Tool..."
echo "======================================"

# Check if we're in the right directory
if [[ ! -d "obsidian_analyzer" ]]; then
    echo "❌ Error: Run this script from the Obsidian_Analyzer project directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "✅ Project directory confirmed"

# Create scripts directory if it doesn't exist
mkdir -p scripts

# Create the auto-linker module
echo "📝 Creating auto-linker module..."
cat > obsidian_analyzer/auto_linker.py << 'EOF'
"""
Auto-Link Insertion Tool for Obsidian Analyzer
Automatically adds [[wikilinks]] based on analyzer suggestions.
"""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

from .models import LinkSuggestion
from .analyzer import CodingFolderAnalyzer


class AutoLinker:
    """Automatically insert links into Obsidian notes based on suggestions."""
    
    def __init__(self, vault_path: str, backup: bool = True):
        self.vault_path = Path(vault_path)
        self.backup = backup
        self.changes_made = []
        self.backup_dir = None
        
        if backup:
            self.backup_dir = self._create_backup()
    
    def _create_backup(self) -> Path:
        """Create a backup of notes before modification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path.cwd() / f"obsidian_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)
        
        print(f"📁 Creating backup at: {backup_dir}")
        return backup_dir
    
    def _backup_file(self, file_path: Path):
        """Backup individual file before modification."""
        if not self.backup or not self.backup_dir:
            return
            
        relative_path = file_path.relative_to(self.vault_path)
        backup_file = self.backup_dir / relative_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_file)
    
    def analyze_and_suggest_links(self, folder_name: str = "Coding") -> Dict[str, List[LinkSuggestion]]:
        """Analyze folder and get link suggestions for all notes."""
        analyzer = CodingFolderAnalyzer(self.vault_path)
        analyzer.load_coding_notes()
        
        if not analyzer.notes:
            print(f"❌ No notes found in {folder_name} folder")
            return {}
        
        suggestions = {}
        for note_name in analyzer.notes:
            note_suggestions = analyzer.find_link_suggestions(note_name)
            if note_suggestions:
                suggestions[note_name] = note_suggestions
                
        return suggestions
    
    def insert_links_in_note(self, note_path: Path, suggestions: List[LinkSuggestion], 
                            confidence_threshold: float = 0.5, dry_run: bool = False) -> List[str]:
        """Insert links into a specific note file."""
        if not note_path.exists():
            return []
        
        # Filter suggestions by confidence
        filtered_suggestions = [s for s in suggestions if s.confidence >= confidence_threshold]
        if not filtered_suggestions:
            return []
        
        # Read file content
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ Error reading {note_path}: {e}")
            return []
        
        original_content = content
        changes = []
        
        for suggestion in filtered_suggestions:
            target = suggestion.target_note
            # Only add links if not already present
            if f"[[{target}]]" in content:
                continue
                
            # Find mentions and replace with links
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(target) + r'\b'
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            
            if matches:
                # Replace from end to beginning to preserve positions
                for match in reversed(matches):
                    start, end = match.span()
                    # Check if already part of a link
                    if not self._is_already_linked(content, start, end):
                        content = content[:start] + f"[[{target}]]" + content[end:]
                        changes.append(f"Linked '{target}' at position {start}")
        
        # Save changes if not dry run
        if changes and not dry_run:
            self._backup_file(note_path)
            try:
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Updated {note_path.name} with {len(changes)} links")
            except Exception as e:
                print(f"❌ Error writing {note_path}: {e}")
                # Restore original content
                try:
                    with open(note_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                except:
                    pass
                return []
        
        return changes
    
    def _is_already_linked(self, content: str, start: int, end: int) -> bool:
        """Check if text is already part of a wikilink."""
        # Look backwards for [[
        look_back = max(0, start - 10)
        before = content[look_back:start]
        
        # Look forwards for ]]
        look_forward = min(len(content), end + 10)
        after = content[end:look_forward]
        
        return '[[' in before and ']]' in after
    
    def auto_link_folder(self, folder_name: str = "Coding", 
                        confidence_threshold: float = 0.7,
                        dry_run: bool = False) -> Dict[str, List[str]]:
        """Automatically add links to all notes in a folder."""
        print(f"🔗 Auto-linking notes in {folder_name} folder...")
        print(f"📊 Confidence threshold: {confidence_threshold:.0%}")
        
        if dry_run:
            print("🧪 DRY RUN MODE - No files will be modified")
        
        # Get suggestions
        all_suggestions = self.analyze_and_suggest_links(folder_name)
        if not all_suggestions:
            print("❌ No link suggestions found")
            return {}
        
        results = {}
        folder_path = self.vault_path / folder_name
        
        for note_name, suggestions in all_suggestions.items():
            note_path = folder_path / f"{note_name}.md"
            
            print(f"\n📝 Processing: {note_name}")
            print(f"   Suggestions: {len(suggestions)}")
            
            # Show what will be linked
            valid_suggestions = [s for s in suggestions if s.confidence >= confidence_threshold]
            if valid_suggestions:
                print(f"   Will link to: {', '.join([s.target_note for s in valid_suggestions])}")
                
                changes = self.insert_links_in_note(note_path, suggestions, confidence_threshold, dry_run)
                if changes:
                    results[note_name] = changes
            else:
                print(f"   No suggestions above {confidence_threshold:.0%} threshold")
        
        return results
    
    def interactive_link_insertion(self, folder_name: str = "Coding"):
        """Interactive mode for selective link insertion."""
        print(f"🎯 Interactive auto-linking for {folder_name} folder")
        
        all_suggestions = self.analyze_and_suggest_links(folder_name)
        if not all_suggestions:
            print("❌ No link suggestions found")
            return
        
        total_applied = 0
        folder_path = self.vault_path / folder_name
        
        for note_name, suggestions in all_suggestions.items():
            print(f"\n{'='*60}")
            print(f"📝 Note: {note_name}")
            print(f"📊 {len(suggestions)} suggestions found")
            
            for i, suggestion in enumerate(suggestions, 1):
                print(f"\n{i}. Link to: [[{suggestion.target_note}]]")
                print(f"   Confidence: {suggestion.confidence:.0%}")
                print(f"   Mentions: {suggestion.mention_count}")
                if suggestion.context_snippets:
                    print(f"   Context: \"{suggestion.context_snippets[0][:100]}...\"")
                
                while True:
                    choice = input("   Apply this link? (y/n/q for quit): ").lower().strip()
                    if choice in ['y', 'yes']:
                        note_path = folder_path / f"{note_name}.md"
                        changes = self.insert_links_in_note(note_path, [suggestion], 0.0)
                        if changes:
                            print(f"   ✅ Applied {len(changes)} links")
                            total_applied += len(changes)
                        break
                    elif choice in ['n', 'no']:
                        print("   ⏭️  Skipped")
                        break
                    elif choice in ['q', 'quit']:
                        print(f"\n🎉 Session complete! Applied {total_applied} links total")
                        return
                    else:
                        print("   Please enter y, n, or q")
            
            if input(f"\nContinue with next note? (y/n): ").lower().startswith('n'):
                break
        
        print(f"\n🎉 Auto-linking complete! Applied {total_applied} links total")
    
    def show_summary(self, results: Dict[str, List[str]]):
        """Show summary of changes made."""
        if not results:
            print("\n📊 No changes were made")
            return
        
        print(f"\n📊 SUMMARY: Modified {len(results)} notes")
        total_links = sum(len(changes) for changes in results.values())
        print(f"🔗 Total links added: {total_links}")
        
        if self.backup_dir:
            print(f"💾 Backup created at: {self.backup_dir}")
        
        print("\n📝 Changes by note:")
        for note_name, changes in results.items():
            print(f"  • {note_name}: {len(changes)} links")
EOF

echo "✅ Created auto_linker.py"

# Update __init__.py to include the new module
echo "🔄 Updating __init__.py..."
cat > obsidian_analyzer/__init__.py << 'EOF'
"""Obsidian Analyzer - Analyze and improve Obsidian vault structure."""

from .analyzer import CodingFolderAnalyzer, analyze_coding_folder, get_recommendations_for_note
from .auto_linker import AutoLinker

__version__ = "0.1.0"
EOF

echo "✅ Updated __init__.py"

# Create CLI script
echo "📝 Creating CLI script..."
cat > scripts/auto_link.py << 'EOF'
#!/usr/bin/env python3
"""
Command-line interface for auto-linking Obsidian notes.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import obsidian_analyzer
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_analyzer import AutoLinker


def main():
    parser = argparse.ArgumentParser(description="Auto-link Obsidian notes")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folder", default="Coding", help="Folder to analyze (default: Coding)")
    parser.add_argument("--confidence", type=float, default=0.7, help="Confidence threshold (default: 0.7)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without modifying files")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode for selective linking")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating backup")
    
    args = parser.parse_args()
    
    # Validate vault path
    if not Path(args.vault_path).exists():
        print(f"❌ Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)
    
    # Create auto-linker
    print(f"🔗 Obsidian Auto-Linker v0.1.0")
    print(f"📁 Vault: {args.vault_path}")
    
    linker = AutoLinker(args.vault_path, backup=not args.no_backup)
    
    try:
        if args.interactive:
            linker.interactive_link_insertion(args.folder)
        else:
            results = linker.auto_link_folder(args.folder, args.confidence, args.dry_run)
            linker.show_summary(results)
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
EOF

echo "✅ Created CLI script"

# Make scripts executable
chmod +x scripts/auto_link.py

# Install the updated package
echo "📦 Installing updated package..."
uv pip install -e .

echo ""
echo "🎉 AUTO-LINK TOOL SUCCESSFULLY BUILT!"
echo "======================================"
echo ""
echo "🚀 USAGE OPTIONS:"
echo ""
echo "1️⃣  DRY RUN (SAFE - Preview only):"
echo "   python scripts/auto_link.py \"/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault/Obsidian Vault\" --dry-run"
echo ""
echo "2️⃣  INTERACTIVE MODE (Selective):"
echo "   python scripts/auto_link.py \"/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault/Obsidian Vault\" --interactive"
echo ""  
echo "3️⃣  AUTO-LINK (High confidence):"
echo "   python scripts/auto_link.py \"/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault/Obsidian Vault\" --confidence 0.8"
echo ""
echo "⚠️  SAFETY FEATURES:"
echo "   • Automatic backups before any changes"
echo "   • Dry-run mode to preview changes"  
echo "   • Interactive mode for selective linking"
echo "   • Confidence thresholds to avoid false positives"
echo ""
echo "✅ Ready to auto-link your notes!"
