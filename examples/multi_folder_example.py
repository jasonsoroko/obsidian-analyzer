#!/usr/bin/env python3
"""
Example usage of the Multi-Folder Analyzer.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_analyzer import MultiVaultAnalyzer

def main():
    # Update this path to your actual vault
    vault_path = "/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault/Obsidian Vault"
    
    print("🔍 Multi-Folder Analyzer Example")
    print("=" * 40)
    
    analyzer = MultiVaultAnalyzer(vault_path)
    
    # Example 1: Discover all folders
    print("\n1️⃣ Discovering folders...")
    folders = analyzer.discover_folders()
    print(f"Found folders: {', '.join(folders)}")
    
    # Example 2: Analyze entire vault
    print("\n2️⃣ Analyzing entire vault...")
    analysis = analyzer.analyze_entire_vault()
    
    if analysis:
        print(f"✅ Analysis complete!")
        print(f"   Health Score: {analysis.vault_health_score}/100")
        print(f"   Total Notes: {analysis.total_notes}")
        print(f"   Cross-folder opportunities: {len(analysis.cross_folder_suggestions)}")
        
        # Example 3: Export report
        print("\n3️⃣ Exporting report...")
        report_path = analyzer.export_markdown_report(analysis)
        print(f"📄 Report saved to: {report_path}")
        
        # Example 4: Show folder breakdown
        print(f"\n4️⃣ Folder breakdown:")
        for folder in analysis.folder_stats:
            print(f"   📂 {folder.name}: {folder.note_count} notes, {folder.total_words} words")
    else:
        print("❌ Analysis failed")
    
    print("\n🎉 Example complete!")

if __name__ == "__main__":
    main()
