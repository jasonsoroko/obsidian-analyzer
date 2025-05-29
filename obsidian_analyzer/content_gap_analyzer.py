"""
AI-Powered Content Gap Analysis for Obsidian Vaults
Identifies missing knowledge connections and suggests new content to create.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import openai

from .analyzer import CodingFolderAnalyzer


@dataclass
class ContentGap:
    gap_type: str
    title: str
    description: str
    priority: str
    confidence: float
    related_notes: List[str]
    suggested_content: List[str]
    tags: List[str]


@dataclass
class KnowledgeCluster:
    cluster_name: str
    notes: List[str]
    topics: List[str]
    missing_connections: List[str]
    hub_potential: float


class ContentGapAnalyzer:
    """AI-powered analysis to find gaps in knowledge coverage."""
    
    def __init__(self, vault_path: str, api_key: Optional[str] = None):
        self.vault_path = Path(vault_path)
        
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI()
    
    def analyze_content_gaps(self, folder_name: str = "Coding") -> List[ContentGap]:
        """Find content gaps using AI analysis."""
        
        analyzer = CodingFolderAnalyzer(str(self.vault_path))
        analyzer.coding_folder = self.vault_path / folder_name
        analyzer.load_coding_notes()
        
        if not analyzer.notes:
            return []
        
        print(f"🔍 AI analyzing content gaps for {len(analyzer.notes)} notes...")
        
        # Get note summaries for AI analysis
        note_summaries = self._create_note_summaries(analyzer.notes)
        
        # Analyze gaps
        gaps = []
        
        # 1. Missing bridge connections
        bridge_gaps = self._find_bridge_gaps(note_summaries)
        gaps.extend(bridge_gaps)
        
        # 2. Incomplete topics
        topic_gaps = self._find_topic_gaps(note_summaries)
        gaps.extend(topic_gaps)
        
        # 3. Missing fundamentals
        fundamental_gaps = self._find_fundamental_gaps(note_summaries)
        gaps.extend(fundamental_gaps)
        
        return sorted(gaps, key=lambda x: x.confidence, reverse=True)
    
    def _create_note_summaries(self, notes: Dict) -> Dict[str, str]:
        """Create concise summaries of each note for AI analysis."""
        summaries = {}
        
        for note_name, note_data in notes.items():
            content = note_data['content'][:1000]
            topics = [f"{cat}:{item}" for cat, item in note_data['topics']]
            tags = list(note_data['tags'])
            
            summary = f"Title: {note_name}\n"
            summary += f"Topics: {', '.join(topics)}\n"
            summary += f"Tags: {', '.join(tags)}\n"
            summary += f"Content preview: {content}..."
            
            summaries[note_name] = summary
        
        return summaries
    
    def _find_bridge_gaps(self, note_summaries: Dict[str, str]) -> List[ContentGap]:
        """Find missing bridge connections between notes."""
        
        prompt = f"""Analyze these Obsidian notes and identify missing "bridge" content that would connect related concepts.

Notes in vault:
{chr(10).join([f"- {name}: {summary[:200]}..." for name, summary in note_summaries.items()])}

Identify 2-3 missing bridge notes that would connect these existing notes. For each gap, provide:

1. What type of bridge content is missing
2. Suggested title for the missing note
3. Why this bridge is important
4. Which existing notes it would connect
5. Key topics it should cover

Respond with ONLY a JSON array:
[
  {{
    "gap_type": "bridge_connection",
    "title": "Connecting Python Development with Note Organization",
    "description": "A note explaining how to use Python tools for Obsidian workflow automation",
    "priority": "high",
    "confidence": 0.85,
    "related_notes": ["Python Hygiene", "The PARA-ish + MOCs System"],
    "suggested_content": ["Automation scripts", "Workflow integration", "Tool synergy"],
    "tags": ["python", "obsidian", "automation"]
  }}
]"""
        
        try:
            response = self._call_ai(prompt)
            gaps_data = json.loads(response)
            
            gaps = []
            for gap_data in gaps_data:
                gaps.append(ContentGap(
                    gap_type=gap_data.get("gap_type", "bridge_connection"),
                    title=gap_data.get("title", ""),
                    description=gap_data.get("description", ""),
                    priority=gap_data.get("priority", "medium"),
                    confidence=gap_data.get("confidence", 0.5),
                    related_notes=gap_data.get("related_notes", []),
                    suggested_content=gap_data.get("suggested_content", []),
                    tags=gap_data.get("tags", [])
                ))
            
            return gaps
            
        except Exception as e:
            print(f"⚠️ Bridge gap analysis error: {e}")
            return []
    
    def _find_topic_gaps(self, note_summaries: Dict[str, str]) -> List[ContentGap]:
        """Find incomplete topic coverage."""
        
        prompt = f"""Analyze these notes for incomplete topic coverage - areas that are mentioned but not fully explored.

Notes:
{chr(10).join([f"- {name}: {summary[:200]}..." for name, summary in note_summaries.items()])}

Identify 2-3 topics that are mentioned across notes but lack dedicated coverage. For each gap:

1. What topic needs deeper coverage
2. Suggested title for a comprehensive note
3. Why this topic deserves its own note
4. Which existing notes reference it
5. Key subtopics to cover

Respond with ONLY a JSON array:
[
  {{
    "gap_type": "topic_coverage",
    "title": "Python Testing Strategies",
    "description": "Comprehensive guide to testing approaches mentioned across multiple notes",
    "priority": "medium",
    "confidence": 0.75,
    "related_notes": ["Python Hygiene", "Modern Python Project Setup Guide (2025)"],
    "suggested_content": ["Unit testing", "Integration testing", "Test automation"],
    "tags": ["python", "testing", "best-practices"]
  }}
]"""
        
        try:
            response = self._call_ai(prompt)
            gaps_data = json.loads(response)
            
            gaps = []
            for gap_data in gaps_data:
                gaps.append(ContentGap(
                    gap_type=gap_data.get("gap_type", "topic_coverage"),
                    title=gap_data.get("title", ""),
                    description=gap_data.get("description", ""),
                    priority=gap_data.get("priority", "medium"),
                    confidence=gap_data.get("confidence", 0.5),
                    related_notes=gap_data.get("related_notes", []),
                    suggested_content=gap_data.get("suggested_content", []),
                    tags=gap_data.get("tags", [])
                ))
            
            return gaps
            
        except Exception as e:
            print(f"⚠️ Topic gap analysis error: {e}")
            return []
    
    def _find_fundamental_gaps(self, note_summaries: Dict[str, str]) -> List[ContentGap]:
        """Find missing fundamental/foundational content."""
        
        prompt = f"""Analyze these notes and identify missing foundational content that would support the existing knowledge.

Notes:
{chr(10).join([f"- {name}: {summary[:200]}..." for name, summary in note_summaries.items()])}

Identify 1-2 fundamental notes that are missing - basic concepts that other notes assume knowledge of. For each:

1. What fundamental concept is missing
2. Suggested title for the foundational note
3. Why this foundation is important
4. Which advanced notes would benefit from this foundation
5. Key fundamentals to cover

Respond with ONLY a JSON array:
[
  {{
    "gap_type": "fundamental_missing",
    "title": "Python Development Environment Basics",
    "description": "Foundational concepts for Python development environments",
    "priority": "high",
    "confidence": 0.8,
    "related_notes": ["Python Hygiene", "Modern Python Project Setup Guide (2025)"],
    "suggested_content": ["Virtual environments", "Package management", "Environment variables"],
    "tags": ["python", "fundamentals", "environment"]
  }}
]"""
        
        try:
            response = self._call_ai(prompt)
            gaps_data = json.loads(response)
            
            gaps = []
            for gap_data in gaps_data:
                gaps.append(ContentGap(
                    gap_type=gap_data.get("gap_type", "fundamental_missing"),
                    title=gap_data.get("title", ""),
                    description=gap_data.get("description", ""),
                    priority=gap_data.get("priority", "medium"),
                    confidence=gap_data.get("confidence", 0.5),
                    related_notes=gap_data.get("related_notes", []),
                    suggested_content=gap_data.get("suggested_content", []),
                    tags=gap_data.get("tags", [])
                ))
            
            return gaps
            
        except Exception as e:
            print(f"⚠️ Fundamental gap analysis error: {e}")
            return []
    
    def _call_ai(self, prompt: str) -> str:
        """Make AI API call with error handling."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up markdown formatting
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()
    
    def generate_gap_report(self, gaps: List[ContentGap]) -> str:
        """Generate detailed gap analysis report."""
        
        if not gaps:
            return "# Content Gap Analysis\n\nNo significant content gaps identified."
        
        report = []
        report.append("# 🔍 Content Gap Analysis Report")
        report.append("")
        report.append(f"Found {len(gaps)} content gaps to address")
        report.append("")
        
        # Group by priority
        high_priority = [g for g in gaps if g.priority == "high"]
        medium_priority = [g for g in gaps if g.priority == "medium"]
        low_priority = [g for g in gaps if g.priority == "low"]
        
        for priority_name, priority_gaps in [("High Priority", high_priority), 
                                           ("Medium Priority", medium_priority), 
                                           ("Low Priority", low_priority)]:
            if not priority_gaps:
                continue
                
            report.append(f"## 🎯 {priority_name} Gaps")
            report.append("")
            
            for gap in priority_gaps:
                report.append(f"### {gap.title}")
                report.append(f"**Type:** {gap.gap_type}")
                report.append(f"**Confidence:** {gap.confidence:.0%}")
                report.append(f"**Description:** {gap.description}")
                report.append("")
                
                if gap.related_notes:
                    report.append("**Connects to:**")
                    for note in gap.related_notes:
                        report.append(f"- [[{note}]]")
                    report.append("")
                
                if gap.suggested_content:
                    report.append("**Should cover:**")
                    for content in gap.suggested_content:
                        report.append(f"- {content}")
                    report.append("")
                
                if gap.tags:
                    report.append(f"**Suggested tags:** {', '.join([f'#{tag}' for tag in gap.tags])}")
                    report.append("")
                
                report.append("---")
                report.append("")
        
        return "\n".join(report)
    
    def create_knowledge_clusters(self, folder_name: str = "Coding") -> List[KnowledgeCluster]:
        """Identify knowledge clusters and hub opportunities."""
        
        analyzer = CodingFolderAnalyzer(str(self.vault_path))
        analyzer.coding_folder = self.vault_path / folder_name
        analyzer.load_coding_notes()
        
        if not analyzer.notes:
            return []
        
        note_summaries = self._create_note_summaries(analyzer.notes)
        
        prompt = f"""Analyze these notes and identify knowledge clusters - groups of related notes that could benefit from a hub/MOC note.

Notes:
{chr(10).join([f"- {name}" for name in note_summaries.keys()])}

Identify 2-3 knowledge clusters where multiple notes could be connected through a hub note. For each cluster:

1. Cluster name
2. Which notes belong to this cluster
3. Common topics/themes
4. What connections are missing
5. Hub potential score (0.0-1.0)

Respond with ONLY a JSON array:
[
  {{
    "cluster_name": "Python Development Workflow",
    "notes": ["Python Hygiene", "Modern Python Project Setup Guide (2025)"],
    "topics": ["python", "development", "tooling"],
    "missing_connections": ["Testing integration", "Deployment workflow"],
    "hub_potential": 0.85
  }}
]"""
        
        try:
            response = self._call_ai(prompt)
            clusters_data = json.loads(response)
            
            clusters = []
            for cluster_data in clusters_data:
                clusters.append(KnowledgeCluster(
                    cluster_name=cluster_data.get("cluster_name", ""),
                    notes=cluster_data.get("notes", []),
                    topics=cluster_data.get("topics", []),
                    missing_connections=cluster_data.get("missing_connections", []),
                    hub_potential=cluster_data.get("hub_potential", 0.5)
                ))
            
            return clusters
            
        except Exception as e:
            print(f"⚠️ Cluster analysis error: {e}")
            return []


def analyze_gaps_cli():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Content Gap Analysis")
    parser.add_argument("vault_path", help="Path to Obsidian vault")
    parser.add_argument("--folder", default="Coding", help="Folder to analyze")
    parser.add_argument("--api-key", help="OpenAI API key")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--clusters", action="store_true", help="Also analyze knowledge clusters")
    
    args = parser.parse_args()
    
    analyzer = ContentGapAnalyzer(args.vault_path, args.api_key)
    
    print("🔍 AI Content Gap Analysis")
    print("=" * 40)
    
    # Analyze content gaps
    gaps = analyzer.analyze_content_gaps(args.folder)
    
    print(f"\n📊 CONTENT GAP ANALYSIS RESULTS:")
    print(f"Found {len(gaps)} content gaps")
    
    for gap in gaps:
        print(f"\n📋 {gap.title}")
        print(f"   Type: {gap.gap_type}")
        print(f"   Priority: {gap.priority}")
        print(f"   Confidence: {gap.confidence:.0%}")
        print(f"   Description: {gap.description}")
        if gap.related_notes:
            print(f"   Connects: {', '.join(gap.related_notes)}")
    
    # Knowledge clusters
    if args.clusters:
        clusters = analyzer.create_knowledge_clusters(args.folder)
        print(f"\n🔗 KNOWLEDGE CLUSTERS:")
        for cluster in clusters:
            print(f"\n📂 {cluster.cluster_name}")
            print(f"   Notes: {', '.join(cluster.notes)}")
            print(f"   Hub Potential: {cluster.hub_potential:.0%}")
    
    # Generate report
    if args.output:
        report = analyzer.generate_gap_report(gaps)
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Gap analysis report saved to: {args.output}")


if __name__ == "__main__":
    analyze_gaps_cli()
