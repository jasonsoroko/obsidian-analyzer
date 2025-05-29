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
