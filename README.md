# Obsidian Analyzer

Obsidian Analyzer is a toolkit for inspecting and improving the structure of an Obsidian vault. It can analyze note collections, automatically insert links, and even leverage AI modules for deeper insights.

## Installation

This project requires **Python >=3.8**. Install dependencies with:

```bash
pip install -r requirements.txt
```

Or install the package in editable mode:

```bash
pip install -e .
```

## Major Features

- **`CodingFolderAnalyzer`** – Analyze notes in your `Coding` folder and get link and structure suggestions.
- **`AutoLinker`** – Automatically insert `[[wikilinks]]` based on suggestions. Supports backups and `dry_run` mode so you can preview changes safely.
- **`MultiVaultAnalyzer`** – Perform cross-folder analysis of an entire vault and export a Markdown report.
- **AI-powered tools** – `AISemanticLinker` discovers semantic connections between notes, while `ContentGapAnalyzer` highlights missing knowledge areas.

## Example Usage

Run the examples to see the analyzer in action:

```bash
python examples/basic_usage.py
```

```bash
python examples/multi_folder_example.py
```

## Running Tests

Use `pytest` to run the test suite:

```bash
pytest
```

## License

This project is licensed under the MIT License.
