import os
import re
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple

@dataclass
class LinkSuggestion:
    target_note: str
    context_snippets: List[str]
    confidence: float
    mention_count: int
    
@dataclass
class StructureSuggestion:
    suggestion_type: str
    description: str
    examples: List[str] = None

class CodingFolderAnalyzer:
    def __init__(self, vault_path):
        self.vault_path = Path(vault_path)
        self.coding_folder = self.vault_path / "Coding"
        self.notes = {}
        self.backlinks = defaultdict(set)
        self.code_patterns = {
            'languages': ['python', 'javascript', 'java', 'cpp', 'rust', 'go', 'ruby', 'php', 'swift', 'kotlin'],
            'frameworks': ['react', 'django', 'flask', 'spring', 'express', 'vue', 'angular', 'laravel'],
            'concepts': ['algorithm', 'data structure', 'design pattern', 'api', 'database', 'testing', 'debugging'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'terraform', 'ansible']
        }
        
    def load_coding_notes(self):
        """Load all markdown files from the Coding folder"""
        if not self.coding_folder.exists():
            print(f"Coding folder not found at: {self.coding_folder}")
            return
            
        print(f"Analyzing notes in: {self.coding_folder}")
        
        for md_file in self.coding_folder.glob("**/*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    relative_path = md_file.relative_to(self.coding_folder)
                    note_name = md_file.stem
                    
                    self.notes[note_name] = {
                        'path': md_file,
                        'relative_path': relative_path,
                        'content': content,
                        'word_count': len(content.split()),
                        'lines': content.count('\n') + 1,
                        'links': self.extract_links(content),
                        'tags': self.extract_tags(content),
                        'headings': self.extract_headings(content),
                        'code_blocks': self.extract_code_blocks(content),
                        'topics': self.identify_coding_topics(content)
                    }
            except Exception as e:
                print(f"Error reading {md_file}: {e}")
                
        print(f"Loaded {len(self.notes)} notes from Coding folder")
    
    def extract_links(self, content):
        """Extract existing wikilinks from content"""
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)
        return set(links)
    
    def extract_tags(self, content):
        """Extract hashtags from content"""
        tags = re.findall(r'#(\w+(?:/\w+)*)', content)
        return set(tags)
    
    def extract_headings(self, content):
        """Extract markdown headings with their levels"""
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        return [(len(h[0]), h[1].strip()) for h in headings]
    
    def extract_code_blocks(self, content):
        """Extract code blocks with language info"""
        # Match both ``` and ~~~ code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        code_blocks.extend(re.findall(r'~~~(\w+)?\n(.*?)\n~~~', content, re.DOTALL))
        return code_blocks
    
    def identify_coding_topics(self, content):
        """Identify coding-related topics mentioned in the content"""
        content_lower = content.lower()
        topics = set()
        
        for category, items in self.code_patterns.items():
            for item in items:
                if item in content_lower:
                    topics.add((category, item))
        
        return topics
    
    def find_link_suggestions(self, note_name):
        """Find potential links for a specific note"""
        if note_name not in self.notes:
            return []
            
        note = self.notes[note_name]
        content = note['content']
        content_lower = content.lower()
        suggestions = []
        
        for other_name, other_note in self.notes.items():
            if other_name == note_name:
                continue
            
            # Skip if already linked
            if other_name in note['links']:
                continue
            
            # Look for exact title mentions
            title_mentions = self.find_title_mentions(content, other_name)
            if title_mentions:
                suggestions.append(LinkSuggestion(
                    target_note=other_name,
                    context_snippets=title_mentions,
                    confidence=0.9,
                    mention_count=len(title_mentions)
                ))
                continue
            
            # Look for topic overlap
            topic_overlap = self.calculate_topic_overlap(note, other_note)
            if topic_overlap > 0.3:  # 30% topic overlap threshold
                context = self.find_topic_context(content, other_note['topics'])
                if context:
                    suggestions.append(LinkSuggestion(
                        target_note=other_name,
                        context_snippets=context,
                        confidence=topic_overlap,
                        mention_count=len(context)
                    ))
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:10]  # Top 10 suggestions
    
    def find_title_mentions(self, content, title):
        """Find mentions of note title in content with context"""
        mentions = []
        lines = content.split('\n')
        title_lower = title.lower()
        
        for i, line in enumerate(lines):
            if title_lower in line.lower():
                # Get context (line with mention plus surrounding lines)
                start = max(0, i-1)
                end = min(len(lines), i+2)
                context = ' '.join(lines[start:end]).strip()
                mentions.append(context[:200] + "..." if len(context) > 200 else context)
        
        return mentions
    
    def calculate_topic_overlap(self, note1, note2):
        """Calculate topic similarity between two notes"""
        topics1 = set(item for _, item in note1['topics'])
        topics2 = set(item for _, item in note2['topics'])
        
        if not topics1 or not topics2:
            return 0
        
        intersection = topics1.intersection(topics2)
        union = topics1.union(topics2)
        
        return len(intersection) / len(union) if union else 0
    
    def find_topic_context(self, content, topics):
        """Find context where topics are mentioned"""
        context_snippets = []
        lines = content.split('\n')
        topic_items = set(item for _, item in topics)
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for topic in topic_items:
                if topic in line_lower:
                    # Get surrounding context
                    start = max(0, i-1)
                    end = min(len(lines), i+2)
                    context = ' '.join(lines[start:end]).strip()
                    snippet = context[:150] + "..." if len(context) > 150 else context
                    if snippet not in context_snippets:
                        context_snippets.append(snippet)
                    break
        
        return context_snippets[:3]  # Max 3 context snippets
    
    def analyze_note_structure(self, note_name):
        """Analyze and suggest structure improvements for a note"""
        if note_name not in self.notes:
            return None
        
        note = self.notes[note_name]
        suggestions = []
        
        # Check for headings structure
        if note['word_count'] > 300 and len(note['headings']) == 0:
            suggestions.append(StructureSuggestion(
                "add_headings",
                "This note is long but has no headings. Consider adding structure.",
                ["## Overview", "## Implementation", "## Examples", "## Related Topics"]
            ))
        
        # Check heading hierarchy
        if len(note['headings']) > 1:
            levels = [h[0] for h in note['headings']]
            if any(level > 2 for level in levels) and 1 not in levels:
                suggestions.append(StructureSuggestion(
                    "heading_hierarchy",
                    "Consider adding a main H1 heading to establish document hierarchy."
                ))
        
        # Suggest code organization
        if len(note['code_blocks']) > 3:
            suggestions.append(StructureSuggestion(
                "code_organization",
                "Multiple code blocks found. Consider organizing them under headings.",
                ["## Setup", "## Implementation", "## Testing", "## Usage Examples"]
            ))
        
        # Check for missing code language tags
        unlabeled_code = sum(1 for lang, _ in note['code_blocks'] if not lang)
        if unlabeled_code > 0:
            suggestions.append(StructureSuggestion(
                "code_language_tags",
                f"Found {unlabeled_code} code blocks without language tags. Add language for better syntax highlighting.",
                ["```python", "```javascript", "```bash"]
            ))
        
        # Suggest topic organization
        if len(note['topics']) > 5:
            topic_categories = defaultdict(list)
            for category, topic in note['topics']:
                topic_categories[category].append(topic)
            
            if len(topic_categories) > 2:
                suggestions.append(StructureSuggestion(
                    "topic_sections",
                    f"This note covers multiple topic areas. Consider organizing into sections.",
                    [f"## {category.title()}" for category in topic_categories.keys()]
                ))
        
        # Suggest tagging improvements
        common_topics = [topic for _, topic in note['topics']]
        missing_tags = set(common_topics) - note['tags']
        if missing_tags:
            suggestions.append(StructureSuggestion(
                "add_tags",
                "Consider adding tags for better discoverability.",
                [f"#{tag}" for tag in list(missing_tags)[:5]]
            ))
        
        return suggestions
    
    def generate_coding_report(self):
        """Generate comprehensive analysis of the Coding folder"""
        self.load_coding_notes()
        
        if not self.notes:
            return {"error": "No notes found in Coding folder"}
        
        # Build backlink graph
        for note_name, note_data in self.notes.items():
            for link in note_data['links']:
                if link in self.notes:
                    self.backlinks[link].add(note_name)
        
        # Find orphaned notes
        orphaned = set()
        for note_name, note_data in self.notes.items():
            has_incoming = len(self.backlinks[note_name]) > 0
            has_outgoing = len(note_data['links']) > 0
            if not has_incoming and not has_outgoing:
                orphaned.add(note_name)
        
        # Topic analysis
        all_topics = Counter()
        for note_data in self.notes.values():
            for category, topic in note_data['topics']:
                all_topics[f"{category}:{topic}"] += 1
        
        return {
            'summary': {
                'total_notes': len(self.notes),
                'total_words': sum(note['word_count'] for note in self.notes.values()),
                'total_links': sum(len(note['links']) for note in self.notes.values()),
                'orphaned_notes': len(orphaned),
                'notes_with_code': len([n for n in self.notes.values() if n['code_blocks']]),
                'common_topics': all_topics.most_common(10)
            },
            'orphaned_notes': list(orphaned),
            'notes': list(self.notes.keys())
        }
    
    def get_note_recommendations(self, note_name):
        """Get specific recommendations for a note"""
        link_suggestions = self.find_link_suggestions(note_name)
        structure_suggestions = self.analyze_note_structure(note_name)
        
        return {
            'note_name': note_name,
            'link_suggestions': link_suggestions,
            'structure_suggestions': structure_suggestions,
            'note_info': {
                'word_count': self.notes[note_name]['word_count'],
                'current_links': len(self.notes[note_name]['links']),
                'headings': len(self.notes[note_name]['headings']),
                'code_blocks': len(self.notes[note_name]['code_blocks']),
                'topics': list(self.notes[note_name]['topics'])
            }
        }


# Usage functions
def analyze_coding_folder(vault_path):
    """Main function to analyze the Coding folder"""
    analyzer = CodingFolderAnalyzer(vault_path)
    report = analyzer.generate_coding_report()
    
    if 'error' in report:
        print(report['error'])
        return
    
    print("=== CODING FOLDER ANALYSIS ===\n")
    print(f"📁 Total Notes: {report['summary']['total_notes']}")
    print(f"📝 Total Words: {report['summary']['total_words']:,}")
    print(f"🔗 Total Links: {report['summary']['total_links']}")
    print(f"👻 Orphaned Notes: {report['summary']['orphaned_notes']}")
    print(f"💻 Notes with Code: {report['summary']['notes_with_code']}")
    
    print(f"\n=== TOP CODING TOPICS ===")
    for topic, count in report['summary']['common_topics']:
        category, item = topic.split(':', 1)
        print(f"• {item} ({category}): {count} notes")
    
    if report['orphaned_notes']:
        print(f"\n=== ORPHANED NOTES ===")
        for note in report['orphaned_notes']:
            print(f"• {note}")
    
    print(f"\n=== AVAILABLE NOTES FOR ANALYSIS ===")
    for note in sorted(report['notes']):
        print(f"• {note}")
    
    return analyzer

def get_recommendations_for_note(analyzer, note_name):
    """Get detailed recommendations for a specific note"""
    if note_name not in analyzer.notes:
        print(f"Note '{note_name}' not found in Coding folder")
        available = list(analyzer.notes.keys())
        print(f"Available notes: {', '.join(available[:5])}{'...' if len(available) > 5 else ''}")
        return
    
    recommendations = analyzer.get_note_recommendations(note_name)
    
    print(f"\n=== RECOMMENDATIONS FOR '{note_name}' ===")
    
    # Note info
    info = recommendations['note_info']
    print(f"\n📊 Note Stats:")
    print(f"   Words: {info['word_count']}")
    print(f"   Current Links: {info['current_links']}")
    print(f"   Headings: {info['headings']}")
    print(f"   Code Blocks: {info['code_blocks']}")
    
    if info['topics']:
        print(f"   Topics: {', '.join([f'{cat}:{item}' for cat, item in info['topics'][:5]])}")
    
    # Link suggestions
    if recommendations['link_suggestions']:
        print(f"\n🔗 LINK SUGGESTIONS ({len(recommendations['link_suggestions'])}):")
        for i, suggestion in enumerate(recommendations['link_suggestions'][:5], 1):
            print(f"\n{i}. Link to: [[{suggestion.target_note}]]")
            print(f"   Confidence: {suggestion.confidence:.1%}")
            print(f"   Mentions: {suggestion.mention_count}")
            if suggestion.context_snippets:
                print(f"   Context: \"{suggestion.context_snippets[0][:100]}...\"")
    
    # Structure suggestions
    if recommendations['structure_suggestions']:
        print(f"\n🏗️ STRUCTURE SUGGESTIONS ({len(recommendations['structure_suggestions'])}):")
        for i, suggestion in enumerate(recommendations['structure_suggestions'], 1):
            print(f"\n{i}. {suggestion.description}")
            if suggestion.examples:
                print(f"   Examples: {', '.join(suggestion.examples[:3])}")


# Main execution
if __name__ == "__main__":
    vault_path = "/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault"
    
    # Analyze the Coding folder
    analyzer = analyze_coding_folder(vault_path)
    
    if analyzer and analyzer.notes:
        print(f"\n" + "="*50)
        print("To get recommendations for a specific note, run:")
        print("get_recommendations_for_note(analyzer, 'YourNoteName')")
        print(f"="*50)
        
        # Example: analyze the first note
        first_note = list(analyzer.notes.keys())[0]
        print(f"\nExample analysis for '{first_note}':")
        get_recommendations_for_note(analyzer, first_note)