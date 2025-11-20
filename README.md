# 📚 AI 个人知识库助手 (AI Knowledge Base Assistant)

这是一个基于 RAG (检索增强生成) 技术的智能问答系统。

它允许用户上传 PDF 技术文档（如操作手册、API 文档），并使用 AI 进行精准问答。

项目完全使用 Python 开发，前端采用 Streamlit，后端集成 ChromaDB 向量数据库。

## ✨ 主要功能

- **📂 文档上传**：支持上传 PDF 格式的技术文档。
- **🧹 智能清洗**：自动提取文本，并进行智能切片 (Chunking)。
- **🧠 向量检索**：使用 ChromaDB 本地向量库，支持持久化存储。
- **🤖 AI 问答**：集成阿里云通义千问 (Qwen-Max) 大模型，基于文档内容生成回答。
- **💬 上下文记忆**：支持多轮对话，AI 能记住之前的聊天内容。

## 🛠️ 技术栈

- **语言**：Python 3.8+
- **界面**：Streamlit
- **大模型**：Qwen-Max (阿里云百炼)
- **向量库**：ChromaDB
- **PDF 解析**：pypdf

## 🚀 快速开始

### 1. 克隆仓库

```
git clone [https://github.com/MisayaHN/AI-Knowledge-Base-Assistant.git](https://github.com/MisayaHN/AI-Knowledge-Base-Assistant.git)
cd AI-Knowledge-Base-Assistant
```

### 2. 安装依赖

建议使用虚拟环境运行：

```
pip install -r requirements.txt
```

### 3. 配置 API Key

本项目使用阿里云百炼 API。

启动后在网页左侧边栏输入 API Key，或通过环境变量配置。

### 4. 运行应用

```
streamlit run app.py
```

应用启动后，浏览器将自动打开 `http://localhost:8501`。

## 📝 使用指南

1. 在左侧边栏输入你的 **API Key**。
2. 点击 **Browse files** 上传 PDF 文件。
3. 点击 **“开始处理入库”** 按钮，等待向量化完成。
4. 在底部的聊天框中提问，例如：“手册里关于智能评阅讲了什么？”。

**Author:** MisayaHN