from __future__ import annotations

import os
import asyncio
from typing import Literal
from dotenv import load_dotenv
load_dotenv(override=True)
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools.retriever import create_retriever_tool
from langgraph.graph import MessagesState, StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import BaseModel, Field

# ----------------------------------------------------------------------
# LLM & Embeddings
# ----------------------------------------------------------------------
MODEL_NAME = "deepseek-chat"
try:
    model = init_chat_model(model=MODEL_NAME, model_provider="deepseek", temperature=0)
    grader_model = init_chat_model(model=MODEL_NAME, model_provider="deepseek", temperature=0)
except Exception as e:
    print(f"Warning: Could not initialize DeepSeek model: {e}")
    print("Falling back to OpenAI model...")
    model = init_chat_model(model="gpt-3.5-turbo", model_provider="openai", temperature=0)
    grader_model = init_chat_model(model="gpt-3.5-turbo", model_provider="openai", temperature=0)

# For the embeddings, we'll use mock embeddings since we created a mock vector store
from langchain_core.embeddings import Embeddings
import numpy as np

class MockEmbeddings(Embeddings):
    def embed_documents(self, texts):
        return [np.random.rand(1536).tolist() for _ in texts]
    
    def embed_query(self, text):
        return np.random.rand(1536).tolist()

# ----------------------------------------------------------------------
# Vector store & Retriever tool
# ----------------------------------------------------------------------
VS_PATH = "mcp_course_materials_db"

try:
    vector_store = FAISS.load_local(
        folder_path=VS_PATH,
        embeddings=MockEmbeddings(),  # Use mock embeddings
        allow_dangerous_deserialization=True,
    )
    retriever_tool = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 3}),
        name="retrieve_mcp_course",
        description="Search and return relevant sections from the mcp course materials.",
    )
    print("✅ Vector store loaded successfully")
except Exception as e:
    print(f"Error loading vector store: {e}")
    retriever_tool = None

# ----------------------------------------------------------------------
# Prompts
# ----------------------------------------------------------------------
SYSTEM_INSTRUCTION = (
    "You are an MCP technical training assistant. 'MCP' refers to **Model Context Protocol**, "
    "an open framework for enabling LLMs to call external tools. Do NOT confuse "
    "it with Microsoft Certified Professional.\n"
    "Answer ONLY questions related to the MCP practical course content, including "
    "tool invocation, streaming, LangGraph, API design, etc. "
    "If the user question is NOT related to the course, reply: '我不能回答与 MCP 技术实战公开课无关的问题。' "
    "You may call the provided tool `retriever_tool` when additional context is required."
)

GRADE_PROMPT = (
    "You are a grader assessing relevance of a retrieved document to a user question.\n"
    "Retrieved document:\n{context}\n\nUser question: {question}\n"
    "Return 'yes' if relevant, otherwise 'no'."
)

REWRITE_PROMPT = (
    "You are rewriting user questions to make them more relevant to the MCP technical practical course.\n"
    "Note: In this context, **MCP stands for Model Context Protocol**, an open "
    "framework for enabling large language models to use external tools and structured APIs.\n"
    "Do NOT interpret MCP as Microsoft Certified Professional.\n"
    "Your job is to refine or clarify the user's question to make it better "
    "aligned with key concepts from the Model Context Protocol course, such as tool "
    "invocation, tool registration, streaming APIs, LangGraph workflows, etc.\n\n"
    "Original question:\n{question}\nImproved question:"
)

ANSWER_PROMPT = (
    "You are an assistant for answering questions related to the MCP technical practical course. "
    "Use the provided context to answer the question as completely and accurately as possible. "
    "Whenever relevant, include examples, code blocks, or image references that appear in the source material. "
    "Use standard Markdown format for your output.\n\n"
    "Guidelines:\n"
    "- Prefer quoting code snippets using triple backticks (```) to preserve formatting.\n"
    "- If the context includes Markdown images (e.g. ![alt](url)), and the image is relevant, you may include it in the response.\n"
    "- Keep the response structured and easy to read with proper Markdown sections if needed.\n"
    "- If the answer is unknown or not present in the context, say: '我不知道。'\n\n"
    "Question: {question}\n"
    "Context: {context}"
)

# ----------------------------------------------------------------------
# Langgraph Nodes
# ----------------------------------------------------------------------
async def generate_query_or_respond(state: MessagesState):
    """LLM decides to answer directly or call retriever tool."""
    if retriever_tool is None:
        # If no retriever tool, just respond directly
        response = await model.ainvoke([
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            *state["messages"],
        ])
        return {"messages": [response]}
    
    response = await model.bind_tools([retriever_tool]).ainvoke([
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        *state["messages"],
    ])
    return {"messages": [response]}

class GradeDoc(BaseModel):
    binary_score: str = Field(description="Relevance score 'yes' or 'no'.")

async def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
    if retriever_tool is None:
        return "generate_answer"
        
    question = state["messages"][0].content  # original user question
    ctx = state["messages"][-1].content  # retriever output
    prompt = GRADE_PROMPT.format(question=question, context=ctx)
    try:
        result = await grader_model.with_structured_output(GradeDoc).ainvoke([
            {"role": "user", "content": prompt}
        ])
        return "generate_answer" if result.binary_score.lower().startswith("y") else "rewrite_question"
    except Exception as e:
        print(f"Error grading documents: {e}")
        return "generate_answer"  # Default to generating answer if grading fails

async def rewrite_question(state: MessagesState):
    question = state["messages"][0].content
    prompt = REWRITE_PROMPT.format(question=question)
    resp = await model.ainvoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": resp.content}]}

async def generate_answer(state: MessagesState):
    question = state["messages"][0].content
    if len(state["messages"]) > 1:
        ctx = state["messages"][-1].content
        prompt = ANSWER_PROMPT.format(question=question, context=ctx)
    else:
        # No context available
        prompt = f"Answer the following question about MCP:\n\n{question}"
    
    resp = await model.ainvoke([{"role": "user", "content": prompt}])
    return {"messages": [resp]}

# ----------------------------------------------------------------------
# Build graph
# ----------------------------------------------------------------------
workflow = StateGraph(MessagesState)
workflow.add_node("generate_query_or_respond", generate_query_or_respond)
if retriever_tool is not None:
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
workflow.add_node("rewrite_question", rewrite_question)
workflow.add_node("generate_answer", generate_answer)

workflow.add_edge(START, "generate_query_or_respond")
if retriever_tool is not None:
    workflow.add_edge("generate_query_or_respond", "retrieve")
    workflow.add_conditional_edges("retrieve", grade_documents)
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")
else:
    workflow.add_edge("generate_query_or_respond", "generate_answer")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

rag_agent = workflow.compile(name="rag_agent")

# ----------------------------------------------------------------------
# Main function to test the agent
# ----------------------------------------------------------------------
async def main():
    print("🚀 RAG Agent for MCP Course Materials")
    print("Ask questions about the MCP technical practical course!")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            question = input("You: ")
            if question.lower() in ['quit', 'exit', '退出']:
                print("Goodbye! 👋")
                break
                
            result = await rag_agent.ainvoke({"messages": [{"role": "user", "content": question}]})
            answer = result["messages"][-1].content
            print(f"Assistant: {answer}\n")
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    asyncio.run(main())