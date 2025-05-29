#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_analyzer import SafeAutoLinker, SafetyLevel
import argparse

def main():
   parser = argparse.ArgumentParser(description="Safe Auto-Linker for Obsidian")
   parser.add_argument("vault_path", help="Path to Obsidian vault")
   parser.add_argument("--folder", default="Coding", help="Folder to analyze")
   parser.add_argument("--confidence", type=float, default=0.8, help="Confidence threshold")
   parser.add_argument("--safety", choices=["paranoid", "conservative", "balanced", "aggressive"], 
                      default="conservative", help="Safety level")
   parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
   parser.add_argument("--rollback", help="Rollback using backup ID")
   parser.add_argument("--list-backups", action="store_true", help="List available backups")
   
   args = parser.parse_args()
   
   safety_level = SafetyLevel(args.safety)
   linker = SafeAutoLinker(args.vault_path, safety_level)
   
   if args.rollback:
       success = linker.rollback_changes(args.rollback, confirm=True)
       exit(0 if success else 1)
   
   if args.list_backups:
       backups = linker.list_backups()
       print(f"📦 Available backups: {len(backups)}")
       for backup in backups:
           print(f"  {backup['backup_id']} - {backup['timestamp']} ({len(backup['files'])} files)")
       exit(0)
   
   results = linker.safe_auto_link_folder(
       args.folder, 
       args.confidence, 
       dry_run=not args.apply
   )
   
   if "error" in results:
       print(f"❌ {results['error']}")
       exit(1)
   
   print("✅ Safe auto-linking complete!")

if __name__ == "__main__":
   main()
