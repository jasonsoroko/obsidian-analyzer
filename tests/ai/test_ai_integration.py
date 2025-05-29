"""Integration tests for AI-powered workflows."""

import pytest
from unittest.mock import patch
from pathlib import Path

from obsidian_analyzer import AISemanticLinker, ContentGapAnalyzer
from tests.mocks.mock_openai import MockOpenAIClient


class TestAIIntegration:
    """Test end-to-end AI workflows."""
    
    @pytest.fixture
    def comprehensive_vault(self, tmp_path):
        """Create a comprehensive test vault."""
        vault_path = tmp_path / "comprehensive_vault"
        coding_folder = vault_path / "Coding"
        coding_folder.mkdir(parents=True)
        
        # Create multiple interconnected notes
        notes = {
            "python_fundamentals.md": """
# Python Fundamentals
Core Python concepts and syntax.
Variables, functions, classes, modules.
#python #fundamentals #programming
            """,
            "web_development.md": """
# Web Development with Python
Building web applications using Python frameworks.
Django, Flask, FastAPI for REST APIs.
#python #web #development #api
            """,
            "database_integration.md": """
# Database Integration
Connecting Python applications to databases.
SQLAlchemy, database design, migrations.
#python #database #sql #orm
            """,
            "testing_practices.md": """
# Testing Best Practices
Unit testing, integration testing, TDD.
pytest, mocking, test automation.
#testing #python #automation #quality
            """,
            "deployment_strategies.md": """
# Deployment Strategies
Deploying Python applications to production.
Docker, CI/CD, cloud platforms.
#deployment #devops #python #cloud
            """
        }
        
        for filename, content in notes.items():
            (coding_folder / filename).write_text(content)
        
        return str(vault_path)
    
    @patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI')
    @patch('obsidian_analyzer.content_gap_analyzer.openai.OpenAI')
    def test_complete_ai_analysis_workflow(self, mock_gap_openai, mock_semantic_openai, comprehensive_vault):
        """Test complete AI analysis workflow."""
        
        # Setup mocks
        mock_semantic_openai.return_value = MockOpenAIClient()
        mock_gap_openai.return_value = MockOpenAIClient()
        
        # Step 1: Semantic Analysis
        semantic_linker = AISemanticLinker(comprehensive_vault)
        connections = semantic_linker.analyze_semantic_connections("Coding")
        
        assert isinstance(connections, list)
        
        # Step 2: Content Gap Analysis
        gap_analyzer = ContentGapAnalyzer(comprehensive_vault)
        gaps = gap_analyzer.analyze_content_gaps("Coding")
        
        assert isinstance(gaps, list)
        
        # Step 3: Knowledge Clusters
        clusters = gap_analyzer.create_knowledge_clusters("Coding")
        
        assert isinstance(clusters, list)
        
        # Verify workflow completed without errors
        print(f"Found {len(connections)} semantic connections")
        print(f"Found {len(gaps)} content gaps")
        print(f"Found {len(clusters)} knowledge clusters")
    
    def test_ai_performance_benchmarks(self, comprehensive_vault):
        """Test AI operation performance benchmarks."""
        import time
        
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI') as mock_openai:
            mock_openai.return_value = MockOpenAIClient()
            
            linker = AISemanticLinker(comprehensive_vault)
            
            # Benchmark semantic analysis
            start_time = time.time()
            connections = linker.analyze_semantic_connections("Coding")
            analysis_time = time.time() - start_time
            
            # Should complete within reasonable time (mocked calls should be fast)
            assert analysis_time < 5.0  # 5 seconds max for mocked calls
            
            print(f"Semantic analysis completed in {analysis_time:.2f} seconds")
    
    def test_error_recovery_workflow(self, comprehensive_vault):
        """Test error recovery in AI workflows."""
        
        with patch('obsidian_analyzer.ai_semantic_linker.openai.OpenAI') as mock_openai:
            # Setup client that will fail on first call, succeed on second
            mock_client = MockOpenAIClient()
            call_count = 0
            
            def failing_create(**kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise Exception("First call fails")
                return MockOpenAIClient()._mock_create(**kwargs)
            
            mock_client.chat.completions.create = failing_create
            mock_openai.return_value = mock_client
            
            linker = AISemanticLinker(comprehensive_vault)
            
            # Should handle partial failures gracefully
            connections = linker.analyze_semantic_connections("Coding")
            assert isinstance(connections, list)
