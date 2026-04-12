# 🛡 QuantX AI — Cybersecurity Intelligence Assistant

QuantX is a premium, production-ready AI assistant designed for real-time threat intelligence, vulnerability analysis, and cybersecurity education. It uses a **RAG (Retrieval-Augmented Generation)** pipeline to provide grounded answers based on local knowledge bases.

## 🚀 Key Features

- **Intelligence Dashboard**: Premium Cyberpunk-themed Streamlit UI with glassmorphism and micro-animations.
- **RAG Pipeline**: FAISS-powered local knowledge retrieval using `all-MiniLM-L6-v2` embeddings.
- **Production API**: FastAPI backend with rate limiting, response caching, and strict security validation.
- **Threat Visualization**: Real-time threat level monitoring and system vulnerability analysis.
- **Security News**: Live cybersecurity incident fetching via NewsAPI.
- **Privacy First**: No user query data is permanently logged or stored.

## 🛠 Tech Stack

- **Backend**: FastAPI, Uvicorn, LangChain
- **Frontend**: Streamlit, Custom CSS
- **Vector DB**: FAISS
- **AI Brain**: Groq (Llama 3.3 70B)
- **Security**: Python-dotenv, RateLimiter, ResponseCache

## ⚙️ Setup Instructions

### 1. Prerequisites
- Python 3.10+
- Git

### 2. Installation
```bash
git clone <your-repo-url>
cd cybersecurity_friend
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_key_here
NEWS_API_KEY=your_newsapi_key_here
```

### 4. Running the Project

**Start the Backend (API):**
```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

**Start the Mobile-Ready UI (Streamlit):**
```bash
streamlit run app.py
```

## 📈 Architecture

1. **User** interacts via Streamlit or Flutter Client.
2. **FastAPI** handles requests, validates input, and checks the **Response Cache**.
3. **RAG Pipeline** embeds the query and retrieves context from the **Local Knowledge Base**.
4. **Groq LLM** generates the final response using the context.
5. **Rate Limiter** ensures service stability (5 requests/min per user).

---
*Developed for high-stakes cybersecurity intelligence.*
