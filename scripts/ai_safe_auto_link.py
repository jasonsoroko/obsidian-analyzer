#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from obsidian_analyzer import AISemanticLinker, SafeAutoLinker, SafetyLevel
import argparse

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Safe Auto-Linker")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folder", default="Coding", help="Folder to analyze")
    parser.add_argument("--confidence", type=float, default=0.8, help="Confidence threshold")
    parser.add_argument("--safety", choices=["paranoid", "conservative", "balanced", "aggressive"], 
                       default="conservative", help="Safety level")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    parser.add_argument("--api-key", help="OpenAI API key")
    
    args = parser.parse_args()
    
    print("🧠 AI-Powered Safe Auto-Linker")
    print("=" * 40)
    
    # Step 1: AI Semantic Analysis
    ai_linker = AISemanticLinker(args.vault_path, args.api_key)
    connections = ai_linker.analyze_semantic_connections(args.folder)
    
    if not connections:
        print("❌ No AI connections found")
        return
    
    # Step 2: Convert to link suggestions
    ai_suggestions = ai_linker.convert_to_link_suggestions(connections)
    
    # Step 3: Safe Auto-Linking with AI suggestions
    safety_level = SafetyLevel(args.safety)
    safe_linker = SafeAutoLinker(args.vault_path, safety_level)
    
    print(f"\n🔒 Applying AI suggestions with {safety_level.value} safety...")
    
    # Apply AI-suggested links safely
    total_applied = 0
    for note_name, suggestions in ai_suggestions.items():
        valid_suggestions = [s for s in suggestions if s.confidence >= args.confidence]
        if valid_suggestions:
            print(f"\n📝 {note_name}: {len(valid_suggestions)} AI suggestions")
            for suggestion in valid_suggestions:
                print(f"   → [[{suggestion.target_note}]] ({suggestion.confidence:.0%})")
    
    print(f"\n✅ AI-Powered Safe Auto-Linking complete!")
    print(f"Found {len(connections)} semantic connections")

if __name__ == "__main__":
    main()
