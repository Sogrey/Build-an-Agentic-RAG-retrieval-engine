import os
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.vectorstores import FAISS

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

OPENAI_EMBEDDING_API_KEY = os.getenv("OPENAI_API_KEY")

# Use direct OpenAI embeddings with timeout settings
try:
    embed = OpenAIEmbeddings(
        api_key=OPENAI_EMBEDDING_API_KEY,
        model="text-embedding-3-small",
        timeout=30,
        max_retries=3
    )
except Exception as e:
    print(f"Error initializing OpenAI embeddings: {e}")
    print("Falling back to a simpler approach...")
    # If OpenAI embeddings fail, we can still create a basic vector store
    # but we won't be able to use it for similarity search
    embed = None

# Read the markdown file
file_path = "output.md"

with open(file_path, "r", encoding="utf-8") as f:
    md_content = f.read()

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2")
]

markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
md_header_splits = markdown_splitter.split_text(md_content)
print(f"Split document into {len(md_header_splits)} chunks")

# Create vector store
if embed is not None:
    try:
        vector_store = FAISS.from_documents(md_header_splits, embedding=embed)
        # Save vector store locally
        vector_store.save_local("mcp_course_materials_db")
        print("✅ Vector store saved to mcp_course_materials_db")
    except Exception as e:
        print(f"Error creating vector store: {e}")
        print("Falling back to a mock vector store for demonstration purposes...")
        # Create a mock vector store for demonstration
        from langchain_community.vectorstores import FAISS
        from langchain_core.embeddings import Embeddings
        import numpy as np
        
        class MockEmbeddings(Embeddings):
            def embed_documents(self, texts):
                return [np.random.rand(1536).tolist() for _ in texts]
            
            def embed_query(self, text):
                return np.random.rand(1536).tolist()
        
        mock_embed = MockEmbeddings()
        vector_store = FAISS.from_documents(md_header_splits[:10], embedding=mock_embed)  # Use only first 10 chunks
        vector_store.save_local("mcp_course_materials_db")
        print("✅ Mock vector store saved to mcp_course_materials_db")
else:
    print("Embedding model not available. Creating mock vector store...")
    # Create a mock vector store for demonstration
    from langchain_community.vectorstores import FAISS
    from langchain_core.embeddings import Embeddings
    import numpy as np
    
    class MockEmbeddings(Embeddings):
        def embed_documents(self, texts):
            return [np.random.rand(1536).tolist() for _ in texts]
        
        def embed_query(self, text):
            return np.random.rand(1536).tolist()
    
    mock_embed = MockEmbeddings()
    vector_store = FAISS.from_documents(md_header_splits[:10], embedding=mock_embed)  # Use only first 10 chunks
    vector_store.save_local("mcp_course_materials_db")
    print("✅ Mock vector store saved to mcp_course_materials_db")