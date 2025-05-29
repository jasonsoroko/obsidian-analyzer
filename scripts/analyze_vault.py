#!/usr/bin/env python3
"""
Command-line interface for multi-folder vault analysis.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_analyzer import MultiVaultAnalyzer


def main():
    parser = argparse.ArgumentParser(description="Analyze entire Obsidian vault")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folders", nargs="+", help="Specific folders to analyze (optional)")
    parser.add_argument("--output", help="Output file for report (default: auto-generated)")
    parser.add_argument("--json", action="store_true", help="Also export as JSON")
    
    args = parser.parse_args()
    
    # Validate vault path
    if not Path(args.vault_path).exists():
        print(f"❌ Error: Vault path does not exist: {args.vault_path}")
        sys.exit(1)
    
    print(f"🔍 Obsidian Multi-Folder Analyzer v0.1.0")
    print(f"📁 Vault: {args.vault_path}")
    
    try:
        analyzer = MultiVaultAnalyzer(args.vault_path)
        analysis = analyzer.analyze_entire_vault(args.folders)
        
        if not analysis:
            print("❌ Analysis failed - no analyzable content found")
            sys.exit(1)
        
        # Display summary
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"=" * 40)
        print(f"Health Score: {analysis.vault_health_score}/100")
        print(f"Folders: {analysis.total_folders}")
        print(f"Notes: {analysis.total_notes}")
        print(f"Words: {analysis.total_words:,}")
        print(f"Links: {analysis.total_links}")
        print(f"Orphaned: {analysis.global_orphaned_notes}")
        print(f"Cross-folder opportunities: {len(analysis.cross_folder_suggestions)}")
        
        # Export markdown report
        report_path = analyzer.export_markdown_report(analysis, args.output)
        
        # Export JSON if requested
        if args.json:
            import json
            from dataclasses import asdict
            
            json_path = report_path.replace('.md', '.json')
            with open(json_path, 'w') as f:
                json.dump(asdict(analysis), f, indent=2, default=str)
            print(f"📄 JSON report saved to: {json_path}")
            
    except KeyboardInterrupt:
        print("\n⏹️  Analysis cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
