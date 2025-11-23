# 🧠 FinAI: Contextual RAG Ledger
> **Autonomous Financial Categorization System with Self-Correcting Memory**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![MySQL](https://img.shields.io/badge/Database-MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![AI](https://img.shields.io/badge/AI-Phi--3%20%2B%20SBERT-00CC96?style=for-the-badge&logo=nvidia&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Few--Shot%20RAG-orange?style=for-the-badge)

## 📋 Overview

**FinAI** is an intelligent, privacy-focused financial tracking system designed to solve the problem of messy bank transaction data.

Unlike traditional classifiers that rely on static regex rules or rigid supervised learning, FinAI utilizes a **Retrieval-Augmented Generation (RAG)** architecture. It maintains a dynamic Vector Database of your past financial behavior. When a new transaction arrives, the system retrieves semantically similar past examples to instruct a local Large Language Model (Phi-3), ensuring highly accurate, context-aware categorization that adapts to your personal habits instantly.

## ✨ Key Features

* **🧠 Few-Shot RAG Engine**: Utilizes `SentenceTransformers` to retrieve the top 10 semantically similar past transactions, providing "memory" to the LLM without fine-tuning.
* **🔄 Self-Correcting Feedback Loop**: When a user corrects a category in the UI, the system instantly updates the Vector Index. The AI learns from the correction immediately for all future transactions.
* **🔒 Privacy-First Architecture**: Runs entirely locally using **Ollama (Phi-3 Quantized)** and local embeddings on NVIDIA GPUs (RTX 4050 optimized). No financial data leaves the machine.
* **🧹 Smart Taxonomy Management**: Automatically manages categories. If a category becomes unused, the system performs garbage collection to keep the taxonomy clean.
* **📊 Interactive Analytics**: A professional, white-themed dashboard featuring real-time spending distribution, volume metrics, and editable data grids.
* **🤖 AI Wealth Manager**: An integrated advisory module that generates financial health reports and saving tips based on spending patterns.

---

## 🛠️ System Architecture

FinAI employs a hybrid architecture combining Vector Search for retrieval and Generative AI for reasoning.

```mermaid
flowchart TD
    subgraph Input
    A[User Input: 'Uber to Airport']
    end

    subgraph RAG_Engine [The RAG Brain]
    B{Vector Search}
    C[(Vector DB)]
    D[Top 10 Similar Txns]
    E[Prompt Engineering]
    F[LLM Inference (Phi-3)]
    end

    subgraph Persistence
    G[(MySQL Database)]
    end

    subgraph Interface
    H[Streamlit Dashboard]
    end

    A -->|Embedding| B
    B <-->|Semantic Match| C
    B --> D
    D --> E
    E -->|Context + Query| F
    F -->|JSON Label| G
    G <--> H
    H -->|User Correction| G
    G -->|Re-Indexing| C
