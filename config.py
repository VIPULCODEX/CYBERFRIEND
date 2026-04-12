"""
config.py – Central configuration for QuantX AI Assistant
All API keys are read from .env file using python-dotenv
"""

import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# ─────────────────────────────────────────
# API Keys (loaded from .env)
# ─────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
NEWS_API_KEY   = os.getenv("NEWS_API_KEY", "")

# ─────────────────────────────────────────
# LLM Settings (Groq + Llama)
# ─────────────────────────────────────────
LLM_MODEL       = "llama-3.3-70b-versatile"  # Fast on Groq free tier
LLM_TEMPERATURE = 0.3                        # Lower = more factual
LLM_MAX_TOKENS  = 250                        # Keep responses concise

# ─────────────────────────────────────────
# Embedding Settings
# ─────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # CPU-friendly

# ─────────────────────────────────────────
# RAG / Chunking Settings
# ─────────────────────────────────────────
CHUNK_SIZE    = 500
CHUNK_OVERLAP = 100
TOP_K         = 3   # Number of chunks to retrieve

# ─────────────────────────────────────────
# File Paths
# ─────────────────────────────────────────
DATA_DIR         = "data"          # Put your PDF/TXT files here
FAISS_INDEX_PATH = "faiss_index"  # Auto-created when index is built

# ─────────────────────────────────────────
# Cache Settings
# ─────────────────────────────────────────
CACHE_TTL        = 3600           # Cache TTL in seconds (1 hour)
CACHE_MAX_SIZE   = 1000           # Max cached responses

# ─────────────────────────────────────────
# Rate Limiting Settings
# ─────────────────────────────────────────
RATE_LIMIT_MAX   = 5              # Max requests per window
RATE_LIMIT_WINDOW = 60            # Window in seconds

# ─────────────────────────────────────────
# News API Settings
# ─────────────────────────────────────────
NEWS_QUERY          = "cybersecurity attack hack breach"
NEWS_PAGE_SIZE      = 5
NEWS_TRIGGER_WORDS  = [
    "today", "recent", "latest", "news",
    "happened", "incident", "breach", "current", "now"
]
