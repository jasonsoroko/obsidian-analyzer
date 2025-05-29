"""AI-Powered Semantic Link Discovery using GPT-4o-mini"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import openai

from .models import LinkSuggestion
from .analyzer import CodingFolderAnalyzer


@dataclass
class SemanticConnection:
    source_note: str
    target_note: str
    relationship_type: str
    explanation: str
    confidence: float
    suggested_context: str


class AISemanticLinker:
    def __init__(self, vault_path: str, api_key: Optional[str] = None):
        self.vault_path = Path(vault_path)
        
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI()
    
    def analyze_semantic_connections(self, folder_name: str = "Coding") -> List[SemanticConnection]:
        analyzer = CodingFolderAnalyzer(str(self.vault_path))
        analyzer.coding_folder = self.vault_path / folder_name
        analyzer.load_coding_notes()
        
        if not analyzer.notes:
            return []
        
        print(f"🧠 AI analyzing semantic connections for {len(analyzer.notes)} notes...")
        
        connections = []
        notes_list = list(analyzer.notes.items())
        
        for i, (source_name, source_data) in enumerate(notes_list):
            for j, (target_name, target_data) in enumerate(notes_list):
                if i >= j:
                    continue
                
                print(f"🔍 Analyzing: {source_name} ↔ {target_name}")
                
                connection = self._find_semantic_relationship(
                    source_name, source_data['content'],
                    target_name, target_data['content']
                )
                
                if connection:
                    connections.append(connection)
        
        return sorted(connections, key=lambda x: x.confidence, reverse=True)
    
    def _find_semantic_relationship(self, source_name, source_content, target_name, target_content) -> Optional[SemanticConnection]:
        prompt = f"""Analyze these two Obsidian notes and determine if they should be linked based on semantic relationships.

Note 1: "{source_name}"
Content preview: {source_content[:800]}...

Note 2: "{target_name}" 
Content preview: {target_content[:800]}...

Determine:
1. Should these notes be linked? (yes/no)
2. What type of relationship exists? (prerequisite, related_concept, example_of, continuation, methodology, tool_for, etc.)
3. Explanation of the relationship (1-2 sentences)
4. Confidence score (0.0-1.0)
5. Suggested context for where to add the link

Respond with ONLY a JSON object (no markdown formatting):
{{
    "should_link": boolean,
    "relationship_type": "string",
    "explanation": "string", 
    "confidence": float,
    "suggested_context": "string"
}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            result = json.loads(content)
            
            if result.get("should_link", False) and result.get("confidence", 0) > 0.5:
                return SemanticConnection(
                    source_note=source_name,
                    target_note=target_name,
                    relationship_type=result.get("relationship_type", "related"),
                    explanation=result.get("explanation", ""),
                    confidence=result.get("confidence", 0.5),
                    suggested_context=result.get("suggested_context", "")
                )
        
        except Exception as e:
            print(f"⚠️ AI analysis error for {source_name} ↔ {target_name}: {e}")
            return None
        
        return None
    
    def convert_to_link_suggestions(self, connections: List[SemanticConnection]) -> Dict[str, List[LinkSuggestion]]:
        suggestions = {}
        
        for conn in connections:
            if conn.source_note not in suggestions:
                suggestions[conn.source_note] = []
            
            suggestions[conn.source_note].append(LinkSuggestion(
                target_note=conn.target_note,
                context_snippets=[conn.suggested_context],
                confidence=conn.confidence,
                mention_count=1
            ))
            
            if conn.target_note not in suggestions:
                suggestions[conn.target_note] = []
            
            suggestions[conn.target_note].append(LinkSuggestion(
                target_note=conn.source_note,
                context_snippets=[f"Reverse connection: {conn.explanation}"],
                confidence=conn.confidence * 0.8,
                mention_count=1
            ))
        
        return suggestions
    
    def generate_semantic_report(self, connections: List[SemanticConnection]) -> str:
        report = []
        report.append("# 🧠 AI Semantic Link Discovery Report")
        report.append("")
        report.append(f"Found {len(connections)} semantic connections")
        report.append("")
        
        for conn in connections:
            report.append(f"## {conn.source_note} → {conn.target_note}")
            report.append(f"**Relationship:** {conn.relationship_type}")
            report.append(f"**Confidence:** {conn.confidence:.0%}")
            report.append(f"**Explanation:** {conn.explanation}")
            report.append(f"**Suggested Context:** {conn.suggested_context}")
            report.append("")
        
        return "\n".join(report)


def analyze_semantic_cli():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Semantic Link Discovery")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folder", default="Coding", help="Folder to analyze")
    parser.add_argument("--api-key", help="OpenAI API key (or use OPENAI_API_KEY env var)")
    parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    linker = AISemanticLinker(args.vault_path, args.api_key)
    connections = linker.analyze_semantic_connections(args.folder)
    
    print(f"\n🎯 SEMANTIC ANALYSIS RESULTS:")
    print(f"Found {len(connections)} AI-identified connections")
    
    for conn in connections:
        print(f"\n📋 {conn.source_note} → {conn.target_note}")
        print(f"   Type: {conn.relationship_type}")
        print(f"   Confidence: {conn.confidence:.0%}")
        print(f"   Reason: {conn.explanation}")
    
    if args.output:
        report = linker.generate_semantic_report(connections)
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")


if __name__ == "__main__":
    analyze_semantic_cli()
