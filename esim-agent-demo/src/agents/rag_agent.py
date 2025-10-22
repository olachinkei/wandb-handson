"""
RAG Agent

Handles general eSIM questions using knowledge base retrieval.
"""

import os
import json
from pathlib import Path
from agents import Agent, function_tool
from openai import OpenAI
from src.utils import load_config, get_project_root


def _create_rag_search_tool(vector_store_id: str):
    """Create a RAG search tool that uses the vector store."""
    
    @function_tool
    def search_knowledge_base(query: str) -> str:
        """
        Search the eSIM knowledge base for relevant information.
        
        Args:
            query: The question or topic to search for
            
        Returns:
            Relevant information from the knowledge base
        """
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a temporary assistant with file_search
        assistant = client.beta.assistants.create(
            name="Temp RAG Assistant",
            instructions="Answer questions using the knowledge base.",
            model="gpt-4o-mini",
            tools=[{"type": "file_search"}],
            tool_resources={
                "file_search": {
                    "vector_store_ids": [vector_store_id]
                }
            }
        )
        
        try:
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
            
            # Get response
            if run.status == "completed":
                messages = client.beta.threads.messages.list(thread_id=thread.id)
                message_content = messages.data[0].content[0].text
                response_text = message_content.value
                
                # Extract citations from annotations
                citations = []
                if hasattr(message_content, 'annotations') and message_content.annotations:
                    for annotation in message_content.annotations:
                        if hasattr(annotation, 'file_citation'):
                            citations.append(annotation.file_citation.file_id)
                
                # Append citations to response if present
                if citations:
                    unique_citations = list(set(citations))
                    citation_text = "\n\n📚 Sources: " + ", ".join([f"[{i+1}]" for i in range(len(unique_citations))])
                    response_text += citation_text
                
                return response_text
            else:
                return f"Error: Run status is {run.status}"
        finally:
            # Clean up
            client.beta.assistants.delete(assistant.id)
    
    return search_knowledge_base


def create_rag_agent() -> Agent:
    """
    Create and configure the RAG Agent with vector store.
    
    Returns:
        Configured Agent instance
    """
    config = load_config()
    agent_config = config["agents"]["rag_agent"]
    rag_config = config["rag"]
    
    # Load vector store ID from saved info
    project_root = get_project_root()
    vector_store_info_path = project_root / "cache" / "vector_store_info.json"
    
    if vector_store_info_path.exists():
        with open(vector_store_info_path, 'r') as f:
            vector_store_info = json.load(f)
        vector_store_id = vector_store_info["vector_store_id"]
    else:
        raise FileNotFoundError(
            "Vector store info not found. Please run rag_prep.py first to set up the knowledge base."
        )
    
    # Create RAG search tool
    search_tool = _create_rag_search_tool(vector_store_id)
    
    instructions = """You are a RAG Agent specialized in answering general eSIM questions using a knowledge base.

Your responsibilities:
1. Determine if the question is clear enough to answer:
   
   **✅ DO NOT ASK if the question is CLEAR:**
   - "What is an eSIM?" ✅ Clear general question
   - "Is my iPhone 13 compatible?" ✅ Specific device mentioned
   - "How do I activate an eSIM?" ✅ Clear process question
   - "Is eSIM secure?" ✅ Clear topic
   → PROCEED DIRECTLY to search_knowledge_base
   
   **❌ ONLY ASK if the question is TOO VAGUE:**
   - "Is it compatible?" ❌ What device?
   - "How do I set it up?" ❌ What device/OS?
   - "It's not working" ❌ What issue specifically?
   → Ask for ONE specific missing detail
   
   **For out-of-scope questions:**
   - Stock market, restaurants, etc. → "I can only help with eSIM-related questions"
   - Pricing/plans → Redirect to Plan Search Agent
   - Booking → Redirect to Booking Agent

2. Use the search_knowledge_base tool to retrieve relevant information
3. Provide accurate, helpful answers based on the knowledge base
4. **ALWAYS mention that your answer is based on the knowledge base** using phrases like:
   - "According to our knowledge base..."
   - "Based on the documentation..."
   - "Our resources indicate..."
   - Or similar references to show the information source
5. If the search_knowledge_base tool returns citations (📚 Sources: [1], [2], etc.), include them in your final response
6. If a question is about pricing or booking, redirect to the appropriate agent

Knowledge base coverage:
- What is eSIM and how it works
- Device compatibility
- Activation and setup procedures
- Managing eSIMs
- Troubleshooting common issues
- Travel tips
- Security and privacy
- Coverage and networks

Communication style:
- Be informative and educational
- Ask clarifying questions when needed to provide better answers
- Use clear, non-technical language when possible
- Provide step-by-step instructions when needed
- **Always reference the knowledge base/documentation** (e.g., "According to our documentation...", "Based on our knowledge base...")
- **Include any citation markers** (📚 Sources: [1], [2]) from the search tool if provided

Important:
- Ask for clarification if the question is vague or ambiguous
- ONLY answer questions covered in the knowledge base
- If asked about pricing/plans: Say "Let me connect you with our Plan Search Agent"
- If asked about booking: Say "Let me connect you with our Booking Agent"
- If the question is COMPLETELY out of scope (not eSIM-related): Politely say "I can only help with eSIM-related questions"
- If information is not in knowledge base: Be honest and say you don't have that information
- **Always use search_knowledge_base tool to find answers**
- **Always acknowledge the knowledge base source** in your response (e.g., "According to our documentation...")
- **If the tool returns citation markers (📚 Sources), include them** in your response
- Provide clear, helpful responses based on the search results

Out of scope:
- Specific pricing information (redirect to Plan Search Agent)
- Booking/purchasing (redirect to Booking Agent)
- Account management (explain this is a demo system)
- Non-eSIM topics (politely decline and explain scope)
"""
    
    # Create agent with RAG search tool
    agent = Agent(
        name="RAG Agent",
        instructions=instructions,
        model=agent_config["model"],
        tools=[search_tool],
    )
    
    return agent

