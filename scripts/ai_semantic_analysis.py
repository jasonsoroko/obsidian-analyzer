#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from obsidian_analyzer.ai_semantic_linker import analyze_semantic_cli
if __name__ == "__main__": analyze_semantic_cli()
