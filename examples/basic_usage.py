#!/usr/bin/env python3
"""Basic usage example for Obsidian Analyzer."""

from obsidian_analyzer import analyze_coding_folder, get_recommendations_for_note

def main():
    # Update this path to your vault
    vault_path = "/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault"
    
    print("🔍 Analyzing Coding folder...")
    analyzer = analyze_coding_folder(vault_path)
    
    if analyzer and analyzer.notes:
        # Get recommendations for the first note
        first_note = list(analyzer.notes.keys())[0]
        print(f"\n📋 Getting recommendations for: {first_note}")
        get_recommendations_for_note(analyzer, first_note)
        
        # Interactive mode
        print(f"\n{'='*50}")
        print("Available notes:")
        for i, note in enumerate(sorted(analyzer.notes.keys()), 1):
            print(f"{i:2d}. {note}")
        
        while True:
            try:
                choice = input(f"\nEnter note name (or 'quit' to exit): ").strip()
                if choice.lower() in ['quit', 'q', 'exit']:
                    break
                if choice in analyzer.notes:
                    get_recommendations_for_note(analyzer, choice)
                else:
                    print(f"Note '{choice}' not found.")
            except KeyboardInterrupt:
                break
        
        print("\n👋 Thanks for using Obsidian Analyzer!")

if __name__ == "__main__":
    main()