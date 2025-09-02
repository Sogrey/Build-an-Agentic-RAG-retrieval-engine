# Build an Agentic RAG Retrieval Engine Based on Multimodal Markdown Documents

This project implements a Retrieval-Augmented Generation (RAG) agent that can answer questions about MCP (Model Context Protocol) course materials. The system processes PDF documents, extracts both text and images, converts them to Markdown format, and creates a vector store for efficient retrieval.

## Features

- PDF to Markdown conversion with image extraction
- Multimodal RAG agent capable of processing both text and images
- Vector store implementation using FAISS
- LangGraph-based agent architecture
- Support for both DeepSeek and OpenAI models

## Prerequisites

- Python 3.8+
- Required dependencies listed in [requirements.txt](requirements.txt)

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Sogrey/Build-an-Agentic-RAG-retrieval-engine.git
   cd Build-an-Agentic-RAG-retrieval-engine
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables in a `.env` file:
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key
   OPENAI_API_KEY=your_openai_api_key
   LANGSMITH_TRACING=false
   LANGSMITH_API_KEY=your_langsmith_api_key
   LANGSMITH_PROJECT=your_project_name
   ```

## Usage

1. Convert PDF to Markdown:
   ```bash
   python pdf_to_markdown.py
   ```

2. Create vector store:
   ```bash
   python create_vector_store.py
   ```

3. Run the RAG agent:
   ```bash
   python run.py
   ```

## Project Structure

- `pdf_to_markdown.py`: Converts PDF documents to Markdown format with image extraction
- `create_vector_store.py`: Creates a FAISS vector store from the Markdown documents
- `rag_agent.py`: Implements the RAG agent using LangGraph
- `run.py`: Entry point to run the RAG agent
- `requirements.txt`: Project dependencies
- `.env`: Environment variables (not included in repository)
- `.gitignore`: Specifies files and directories to ignore in version control
- `LICENSE`: MIT License file

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.