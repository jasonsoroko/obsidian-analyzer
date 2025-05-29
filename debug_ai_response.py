import openai
from obsidian_analyzer.analyzer import CodingFolderAnalyzer

analyzer = CodingFolderAnalyzer('/Users/jasonsoroko/Documents/Obsidian/Obsidian Vault/Obsidian Vault')
analyzer.coding_folder = analyzer.vault_path / 'Coding'
analyzer.load_coding_notes()

notes_list = list(analyzer.notes.items())
source_name, source_data = notes_list[0]
target_name, target_data = notes_list[1]

prompt = f"""Analyze these two Obsidian notes and determine if they should be linked based on semantic relationships.

Note 1: "{source_name}"
Content preview: {source_data['content'][:400]}...

Note 2: "{target_name}" 
Content preview: {target_data['content'][:400]}...

Respond in JSON format:
{{
    "should_link": true,
    "relationship_type": "related_concept",
    "explanation": "Both notes discuss similar topics",
    "confidence": 0.8,
    "suggested_context": "Consider linking when discussing overlapping concepts"
}}"""

client = openai.OpenAI()
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    max_tokens=300
)

print("Raw AI Response:")
print(response.choices[0].message.content)
print("\n" + "="*50)

try:
    import json
    result = json.loads(response.choices[0].message.content)
    print("✅ JSON Parse Success:")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"❌ JSON Parse Error: {e}")
