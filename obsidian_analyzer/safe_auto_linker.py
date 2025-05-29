"""Safe Auto-Linker with comprehensive safety features."""

import os
import re
import shutil
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from .models import LinkSuggestion
from .analyzer import CodingFolderAnalyzer


class SafetyLevel(Enum):
    PARANOID = "paranoid"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


@dataclass
class SafetyReport:
    is_safe: bool
    risk_level: str
    warnings: List[str]
    blockers: List[str]
    file_count: int
    change_count: int
    backup_created: bool


class SafeAutoLinker:
    def __init__(self, vault_path: str, safety_level: SafetyLevel = SafetyLevel.CONSERVATIVE):
        self.vault_path = Path(vault_path)
        self.safety_level = safety_level
        self.backup_dir = Path.cwd() / "obsidian_safe_backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.limits = {
            SafetyLevel.PARANOID: {"max_files": 5, "max_changes": 25},
            SafetyLevel.CONSERVATIVE: {"max_files": 25, "max_changes": 100},
            SafetyLevel.BALANCED: {"max_files": 50, "max_changes": 250},
            SafetyLevel.AGGRESSIVE: {"max_files": 100, "max_changes": 500}
        }
    
    def create_safety_backup(self, files_to_change: List[Path]) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"safe_backup_{timestamp}"
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir()
        
        print(f"💾 Creating safety backup: {backup_id}")
        
        metadata = {
            "backup_id": backup_id,
            "timestamp": timestamp,
            "files": [],
            "safety_level": self.safety_level.value
        }
        
        for file_path in files_to_change:
            if not file_path.exists():
                continue
                
            relative_path = file_path.relative_to(self.vault_path)
            backup_file = backup_path / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(file_path, backup_file)
            
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            metadata["files"].append({
                "path": str(relative_path),
                "hash": file_hash,
                "size": file_path.stat().st_size
            })
        
        with open(backup_path / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Backup created: {len(metadata['files'])} files")
        return backup_id
    
    def safe_auto_link_folder(self, folder_name: str = "Coding", confidence_threshold: float = 0.8, dry_run: bool = True):
        print(f"🔒 Safe Auto-Linker ({self.safety_level.value} mode)")
        print(f"📁 Folder: {folder_name}")
        print(f"📊 Confidence: {confidence_threshold:.0%}")
        print(f"🧪 Dry run: {dry_run}")
        
        # Analyze folder
        analyzer = CodingFolderAnalyzer(str(self.vault_path))
        analyzer.coding_folder = self.vault_path / folder_name
        analyzer.load_coding_notes()
        
        if not analyzer.notes:
            return {"error": "No notes found"}
        
        # Get all suggestions
        all_suggestions = {}
        for note_name in analyzer.notes:
            suggestions = analyzer.find_link_suggestions(note_name)
            valid_suggestions = [s for s in suggestions if s.confidence >= confidence_threshold]
            if valid_suggestions:
                all_suggestions[note_name] = valid_suggestions
        
        if not all_suggestions:
            print("📝 No link suggestions found above confidence threshold")
            return {"message": "No suggestions found"}
        
        # Safety check
        total_changes = sum(len(suggestions) for suggestions in all_suggestions.values())
        limits = self.limits[self.safety_level]
        
        print(f"\n🛡️  SAFETY ASSESSMENT:")
        print(f"   Files to modify: {len(all_suggestions)}")
        print(f"   Total changes: {total_changes}")
        
        if len(all_suggestions) > limits["max_files"]:
            print(f"❌ Too many files: {len(all_suggestions)} > {limits['max_files']}")
            return {"error": "Safety limit exceeded"}
        
        if total_changes > limits["max_changes"]:
            print(f"❌ Too many changes: {total_changes} > {limits['max_changes']}")
            return {"error": "Safety limit exceeded"}
        
        print(f"✅ Safety check passed")
        
        # Create backup if not dry run
        backup_id = None
        if not dry_run:
            files_to_change = []
            folder_path = self.vault_path / folder_name
            for note_name in all_suggestions:
                note_path = folder_path / f"{note_name}.md"
                if note_path.exists():
                    files_to_change.append(note_path)
            
            backup_id = self.create_safety_backup(files_to_change)
        
        # Apply changes
        results = {}
        folder_path = self.vault_path / folder_name
        
        for note_name, suggestions in all_suggestions.items():
            note_path = folder_path / f"{note_name}.md"
            
            if not note_path.exists():
                continue
            
            print(f"\n📝 Processing: {note_name}")
            print(f"   Suggestions: {len(suggestions)}")
            
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
            except Exception as e:
                print(f"❌ Error reading {note_name}: {e}")
                continue
            
            modified_content = original_content
            changes_made = []
            
            for suggestion in suggestions:
                target = suggestion.target_note
                
                if f"[[{target}]]" in modified_content:
                    continue
                
                pattern = r'\b' + re.escape(target) + r'\b'
                matches = list(re.finditer(pattern, modified_content, re.IGNORECASE))
                
                if matches:
                    for match in reversed(matches):
                        start, end = match.span()
                        if not self._is_already_linked(modified_content, start, end):
                            modified_content = modified_content[:start] + f"[[{target}]]" + modified_content[end:]
                            changes_made.append(f"Linked '{target}' at position {start}")
            
            if changes_made:
                if not dry_run:
                    try:
                        with open(note_path, 'w', encoding='utf-8') as f:
                            f.write(modified_content)
                        print(f"✅ Applied {len(changes_made)} changes")
                    except Exception as e:
                        print(f"❌ Error writing {note_name}: {e}")
                        continue
                else:
                    print(f"🧪 Would apply {len(changes_made)} changes:")
                    for change in changes_made[:3]:
                        print(f"     {change}")
                
                results[note_name] = changes_made
        
        total_applied = sum(len(changes) for changes in results.values())
        print(f"\n📊 SUMMARY:")
        print(f"   Files processed: {len(results)}")
        print(f"   Links {'applied' if not dry_run else 'would apply'}: {total_applied}")
        if backup_id:
            print(f"   Backup: {backup_id}")
        
        return {
            "results": results,
            "backup_id": backup_id,
            "total_changes": total_applied,
            "dry_run": dry_run
        }
    
    def _is_already_linked(self, content: str, start: int, end: int) -> bool:
        look_back = max(0, start - 10)
        look_forward = min(len(content), end + 10)
        before = content[look_back:start]
        after = content[end:look_forward]
        return '[[' in before and ']]' in after
    
    def list_backups(self):
        backups = []
        for backup_dir in self.backup_dir.glob("safe_backup_*"):
            metadata_file = backup_dir / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    backups.append(json.load(f))
        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)
    
    def rollback_changes(self, backup_id: str, confirm: bool = False):
        if not confirm:
            print("❌ Rollback requires explicit confirmation")
            return False
        
        backup_path = self.backup_dir / backup_id
        metadata_file = backup_path / "metadata.json"
        
        if not metadata_file.exists():
            print(f"❌ Backup not found: {backup_id}")
            return False
        
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        print(f"🔄 Rolling back {len(metadata['files'])} files...")
        
        restored = 0
        for file_info in metadata["files"]:
            source_file = backup_path / file_info["path"]
            dest_file = self.vault_path / file_info["path"]
            
            if source_file.exists():
                shutil.copy2(source_file, dest_file)
                restored += 1
        
        print(f"✅ Rollback complete: {restored} files restored")
        return True
