# 🧠 FinAI: Contextual RAG Ledger
> **Autonomous Financial Categorization System with Self-Correcting Memory**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![AI](https://img.shields.io/badge/AI-Phi--3%20%2B%20SBERT-green)
![Status](https://img.shields.io/badge/Status-Hackathon%20Ready-success)

## 📋 Overview

**FinAI** is not just a transaction tracker; it is an intelligent, **Self-Learning Financial System** powered by **Retrieval-Augmented Generation (RAG)**.

Unlike traditional classifiers that rely on static keyword rules, FinAI uses a local **Vector Database** to remember *how* you categorized past transactions. It retrieves similar past examples (Few-Shot Learning) to instruct the LLM, ensuring that if you categorize "Starbucks" as "Fuel" once, the system learns that logic forever without retraining.

---

## ✨ Key Features

- **🧠 Few-Shot RAG Engine**: Retrieves the top 10 semantically similar past transactions to inform the LLM's decision.
- **🔄 Self-Correcting Loop**: When you edit a category in the UI, the system updates its Vector Index instantly. The AI learns from your corrections in real-time.
- **⚡ Local GPU Acceleration**: Optimized for **NVIDIA RTX 4050**, utilizing local embedding models (SBERT) and quantized LLMs (Phi-3) for zero-latency privacy.
- **🧹 Auto-Garbage Collection**: Automatically removes unused categories from the database and configuration files to keep the taxonomy clean.
- **📊 Interactive Dashboard**: A white-themed, professional UI with real-time analytics, editable grids, and spending visualization.
- **🤖 AI Wealth Manager**: Generates personalized financial advice reports based on your actual spending patterns using GenAI.

---

## 🛠️ Architecture

```mermaid
flowchart LR
    User[User Input] --> Embed[SBERT Embedding]
    Embed --> VectorDB[(Vector Context)]
    VectorDB -->|Top 10 Examples| Prompt[Dynamic Prompt]
    Prompt --> LLM[Phi-3 Mini]
    LLM -->|JSON Label| DB[(MySQL Ledger)]
    DB <--> Dashboard[Streamlit UI]
