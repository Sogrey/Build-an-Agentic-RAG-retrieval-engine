#!/usr/bin/env python3
"""
Entry point for running the RAG agent with images.
This script provides a convenient way to start the RAG agent application.
"""

import sys
import os
import asyncio

# Add the current directory to Python path to import rag_agent
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point for the RAG agent application."""
    try:
        # Import the rag_agent module
        from rag_agent import main as rag_agent_main
        
        print("🚀 Starting RAG Agent for MCP Course Materials")
        print("=" * 60)
        
        # Run the RAG agent
        asyncio.run(rag_agent_main())
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running the RAG agent: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()