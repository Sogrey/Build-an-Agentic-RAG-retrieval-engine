# 基于多模态Markdown文档构建智能RAG检索引擎

<div align="center">
  <p>
    <a href="./README.zh.md">中文版 README</a> | 
    <a href="./README.md">English README</a>
  </p>
</div>

本项目实现了一个检索增强生成（RAG）代理，能够回答关于MCP（模型上下文协议）课程材料的问题。该系统处理PDF文档，提取文本和图像，将其转换为Markdown格式，并创建向量存储以实现高效检索。

## 功能特点

- 带图像提取的PDF到Markdown转换
- 能够处理文本和图像的多模态RAG代理
- 使用FAISS实现的向量存储
- 基于LangGraph的代理架构
- 支持DeepSeek和OpenAI模型

## 前提条件

- Python 3.8+
- [requirements.txt](requirements.txt)中列出的依赖项

## 安装

1. 克隆仓库：
   ```bash
   git clone git@github.com:Sogrey/Build-an-Agentic-RAG-retrieval-engine.git
   cd Build-an-Agentic-RAG-retrieval-engine
   ```

2. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 在`.env`文件中设置环境变量：
   ```env
   DEEPSEEK_API_KEY=your_deepseek_api_key
   OPENAI_API_KEY=your_openai_api_key
   LANGSMITH_TRACING=false
   LANGSMITH_API_KEY=your_langsmith_api_key
   LANGSMITH_PROJECT=your_project_name
   ```

## 使用方法

1. 将PDF转换为Markdown：
   ```bash
   python pdf_to_markdown.py
   ```

2. 创建向量存储：
   ```bash
   python create_vector_store.py
   ```

3. 运行RAG代理：
   ```bash
   python run.py
   ```

## 项目结构

- `pdf_to_markdown.py`：将PDF文档转换为带图像提取的Markdown格式
- `create_vector_store.py`：从Markdown文档创建FAISS向量存储
- `rag_agent.py`：使用LangGraph实现RAG代理
- `run.py`：运行RAG代理的入口点
- `requirements.txt`：项目依赖
- `.env`：环境变量（不包含在仓库中）
- `.gitignore`：指定在版本控制中忽略的文件和目录
- `LICENSE`：MIT许可证文件

## 许可证

本项目采用MIT许可证 - 详情请见[LICENSE](LICENSE)文件。