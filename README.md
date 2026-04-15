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
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
```

For local edge inference (no cloud LLM), use:
```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:3b-instruct
OLLAMA_BASE_URL=http://localhost:11434
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

## Edge Model + RAG Recommendation

For user-device / edge computing, this stack is recommended:

- **Base local model**: `qwen2.5:7b-instruct` (best quality-speed tradeoff on CPU/GPU laptops)
- **Low-RAM fallback**: `phi3:mini`
- **RAG embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (already used, CPU-friendly)
- **Vector DB**: FAISS CPU (already used)

Fine-tuning strategy (practical and efficient):

1. Start with strong RAG first (domain docs + clean chunking + metadata).
2. Fine-tune only for response style/format using **QLoRA** (4-bit) on 7B model.
3. Train on your incident-response format (Attack Type / Explanation / What to Do / Confidence).
4. Export adapter + merge (or keep LoRA adapter) and serve via Ollama.
5. Keep RAG enabled even after fine-tuning for freshness and factual grounding.

## Hybrid RAG (Static + Warm + Hot)

Folder tiers:
- `data/` -> static foundational knowledge (already present)
- `data_warm/` -> curated standards/techniques (monthly refresh)
- `data_hot/` -> latest intel/vuln data (daily refresh)

Run data ingestion scripts (official sources):
```bash
cd cybersecurity_friend
python data_ingestion/fetch_warm_index_data.py
python data_ingestion/fetch_hot_index_data.py
python data_ingestion/rebuild_hybrid_index.py
```

CPU-first guidance for i3 + 8GB:
- Keep `OLLAMA_MODEL=qwen2.5:3b-instruct` for stable local inference.
- Use `TOP_K=2`, chunk size near 350-400.
- Use 7B model only if latency is acceptable on your machine.

## 📈 Architecture

1. **User** interacts via Streamlit or Flutter Client.
2. **FastAPI** handles requests, validates input, and checks the **Response Cache**.
3. **RAG Pipeline** embeds the query and retrieves context from the **Local Knowledge Base**.
4. **Groq LLM** generates the final response using the context.
5. **Rate Limiter** ensures service stability (5 requests/min per user).

---
*Developed for high-stakes cybersecurity intelligence.*
