"""
RAG Preparation Script for eSIM Agent Demo

This script prepares the knowledge base for RAG by:
1. Creating an OpenAI Vector Store
2. Uploading knowledge base files
3. Testing retrieval functionality
"""

import os
import sys
from pathlib import Path
from typing import List

from openai import OpenAI
from dotenv import load_dotenv

from src.utils import load_config, get_project_root, setup_logging


def initialize_client() -> OpenAI:
    """
    Initialize OpenAI client.
    
    Returns:
        OpenAI client instance
        
    Raises:
        ValueError: If API key is not set
    """
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file."
        )
    
    return OpenAI(api_key=api_key)


def get_knowledge_base_files(config: dict) -> List[Path]:
    """
    Get list of knowledge base files to upload.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of file paths
    """
    project_root = get_project_root()
    rag_config = config['rag']['file_store']
    
    docs_dir = project_root / rag_config['directory']
    file_extensions = rag_config['file_extensions']
    excluded_files = rag_config['excluded_files']
    
    if not docs_dir.exists():
        raise FileNotFoundError(f"Documentation directory not found: {docs_dir}")
    
    files = []
    for ext in file_extensions:
        for file_path in docs_dir.glob(f"*{ext}"):
            if file_path.name not in excluded_files:
                files.append(file_path)
    
    return sorted(files)


def create_vector_store(client: OpenAI, config: dict) -> str:
    """
    Create a new Vector Store or retrieve existing one.
    
    Args:
        client: OpenAI client
        config: Configuration dictionary
        
    Returns:
        Vector store ID
    """
    store_name = config['rag']['vector_store']['name']
    
    print(f"\n🔍 Checking for existing vector store: {store_name}")
    
    # List existing vector stores
    vector_stores = client.vector_stores.list()
    
    for store in vector_stores.data:
        if store.name == store_name:
            print(f"✅ Found existing vector store: {store.id}")
            return store.id
    
    # Create new vector store if not found
    print(f"📦 Creating new vector store: {store_name}")
    vector_store = client.vector_stores.create(
        name=store_name,
        expires_after={
            "anchor": "last_active_at",
            "days": 365  # Store expires after 1 year of inactivity
        }
    )
    
    print(f"✅ Created vector store: {vector_store.id}")
    return vector_store.id


def upload_files(client: OpenAI, vector_store_id: str, file_paths: List[Path]) -> List[str]:
    """
    Upload files to the vector store.
    
    Args:
        client: OpenAI client
        vector_store_id: Vector store ID
        file_paths: List of file paths to upload
        
    Returns:
        List of uploaded file IDs
    """
    print(f"\n📤 Uploading {len(file_paths)} files to vector store...")
    
    file_ids = []
    
    for file_path in file_paths:
        print(f"  - Uploading: {file_path.name}...", end=" ")
        
        try:
            # Upload file to OpenAI
            with open(file_path, 'rb') as f:
                file = client.files.create(
                    file=f,
                    purpose='assistants'
                )
            
            # Add file to vector store
            client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file.id
            )
            
            file_ids.append(file.id)
            print(f"✅ ({file.id})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print(f"\n✅ Successfully uploaded {len(file_ids)}/{len(file_paths)} files")
    return file_ids


def wait_for_processing(client: OpenAI, vector_store_id: str, timeout: int = 300):
    """
    Wait for vector store to finish processing files.
    
    Args:
        client: OpenAI client
        vector_store_id: Vector store ID
        timeout: Maximum wait time in seconds
    """
    import time
    
    print(f"\n⏳ Waiting for vector store to process files...")
    
    start_time = time.time()
    
    while True:
        vector_store = client.vector_stores.retrieve(vector_store_id)
        status = vector_store.status
        file_counts = vector_store.file_counts
        
        print(f"  Status: {status} | "
              f"Completed: {file_counts.completed}/{file_counts.total} | "
              f"Processing: {file_counts.in_progress} | "
              f"Failed: {file_counts.failed}")
        
        if status == "completed":
            print("✅ Vector store processing completed!")
            break
        
        if status == "failed":
            print("❌ Vector store processing failed!")
            break
        
        if time.time() - start_time > timeout:
            print(f"⚠️  Timeout after {timeout} seconds")
            break
        
        time.sleep(5)


def test_retrieval(client: OpenAI, vector_store_id: str):
    """
    Test retrieval functionality with sample queries.
    
    Args:
        client: OpenAI client
        vector_store_id: Vector store ID
    """
    print("\n🧪 Testing retrieval functionality...")
    
    test_queries = [
        "What is an eSIM?",
        "Which iPhone models support eSIM?",
        "How do I activate an eSIM on Android?",
        "What should I do if my eSIM is not working?",
    ]
    
    # Create a temporary assistant for testing
    assistant = client.beta.assistants.create(
        name="eSIM Test Assistant",
        instructions="You are a helpful assistant that answers questions about eSIM technology.",
        model="gpt-4o",
        tools=[{"type": "file_search"}],
        tool_resources={
            "file_search": {
                "vector_store_ids": [vector_store_id]
            }
        }
    )
    
    try:
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            
            # Create thread and run
            thread = client.beta.threads.create()
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=query
            )
            
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=assistant.id
            )
            
            if run.status == 'completed':
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                response = messages.data[0].content[0].text.value
                print(f"✅ Response: {response[:200]}...")
            else:
                print(f"❌ Run status: {run.status}")
    
    finally:
        # Clean up test assistant
        client.beta.assistants.delete(assistant.id)
        print("\n🧹 Cleaned up test assistant")


def save_vector_store_info(vector_store_id: str, file_ids: List[str]):
    """
    Save vector store information to a file.
    
    Args:
        vector_store_id: Vector store ID
        file_ids: List of uploaded file IDs
    """
    import json
    
    project_root = get_project_root()
    info_file = project_root / "cache" / "vector_store_info.json"
    
    info = {
        "vector_store_id": vector_store_id,
        "file_ids": file_ids,
        "created_at": "2025-10-13",
        "file_count": len(file_ids)
    }
    
    with open(info_file, 'w') as f:
        json.dump(info, f, indent=2)
    
    print(f"\n💾 Saved vector store info to: {info_file}")


def main():
    """Main execution function."""
    print("=" * 60)
    print("🚀 eSIM Agent Demo - RAG Preparation")
    print("=" * 60)
    
    try:
        # Setup
        setup_logging()
        config = load_config()
        client = initialize_client()
        
        # Get knowledge base files
        print("\n📚 Loading knowledge base files...")
        file_paths = get_knowledge_base_files(config)
        print(f"✅ Found {len(file_paths)} files:")
        for fp in file_paths:
            print(f"  - {fp.name}")
        
        # Create or retrieve vector store
        vector_store_id = create_vector_store(client, config)
        
        # Upload files
        file_ids = upload_files(client, vector_store_id, file_paths)
        
        # Wait for processing
        wait_for_processing(client, vector_store_id)
        
        # Test retrieval
        test_retrieval(client, vector_store_id)
        
        # Save information
        save_vector_store_info(vector_store_id, file_ids)
        
        print("\n" + "=" * 60)
        print("✅ RAG Preparation Complete!")
        print("=" * 60)
        print(f"\nVector Store ID: {vector_store_id}")
        print(f"Files Uploaded: {len(file_ids)}")
        print(f"\nNext steps:")
        print("  1. Use this vector_store_id in your RAG agent")
        print("  2. Test with demo.py")
        print("  3. Run evaluations")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

