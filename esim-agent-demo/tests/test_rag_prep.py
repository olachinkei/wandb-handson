"""
Unit tests for RAG preparation functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.utils import load_config, get_project_root


class TestRAGPreparation:
    """Test RAG preparation functions."""
    
    def test_get_knowledge_base_files(self):
        """Test knowledge base file discovery."""
        # Import here to avoid issues if module not yet importable
        import sys
        sys.path.insert(0, str(get_project_root()))
        from rag_prep import get_knowledge_base_files
        
        config = load_config()
        files = get_knowledge_base_files(config)
        
        # Should find markdown files
        assert len(files) > 0
        
        # All should be .md files
        for file in files:
            assert file.suffix == '.md'
            assert file.exists()
        
        # Should not include excluded files
        excluded = config['rag']['file_store']['excluded_files']
        for file in files:
            assert file.name not in excluded
    
    def test_knowledge_base_files_structure(self):
        """Test that knowledge base files exist and are readable."""
        project_root = get_project_root()
        docs_dir = project_root / "database" / "RAG_docs"
        
        assert docs_dir.exists()
        assert docs_dir.is_dir()
        
        # Check for expected files
        expected_files = [
            "what_is_esim.md",
            "device_compatibility.md",
            "activation_setup.md",
            "managing_esims.md",
            "troubleshooting.md",
            "travel_tips.md",
            "security_privacy.md",
            "faq.md",
            "coverage_networks.md"
        ]
        
        for filename in expected_files:
            file_path = docs_dir / filename
            assert file_path.exists(), f"{filename} not found"
            
            # Check file is not empty
            assert file_path.stat().st_size > 0, f"{filename} is empty"


class TestVectorStoreConfig:
    """Test vector store configuration."""
    
    def test_vector_store_config_exists(self):
        """Test vector store configuration is properly set."""
        config = load_config()
        
        assert 'rag' in config
        assert 'vector_store' in config['rag']
        assert 'embeddings' in config['rag']
        assert 'file_store' in config['rag']
        
        # Check vector store settings
        vs_config = config['rag']['vector_store']
        assert 'name' in vs_config
        assert 'chunk_size' in vs_config
        assert 'chunk_overlap' in vs_config
        
        # Check embeddings settings
        emb_config = config['rag']['embeddings']
        assert 'model' in emb_config
        assert 'dimensions' in emb_config
    
    def test_file_store_config(self):
        """Test file store configuration."""
        config = load_config()
        fs_config = config['rag']['file_store']
        
        assert 'directory' in fs_config
        assert 'file_extensions' in fs_config
        assert 'excluded_files' in fs_config
        
        # Verify directory exists
        project_root = get_project_root()
        docs_dir = project_root / fs_config['directory']
        assert docs_dir.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

