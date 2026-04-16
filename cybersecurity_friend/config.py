"""
config.py – Central configuration for QuantX AI Assistant
All API keys are read from .env file using python-dotenv
"""

import os
from dotenv import load_dotenv

# Resolve all project paths relative to this file so startup works from any CWD.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))  # Load local .env file

# ─────────────────────────────────────────
# API Keys (loaded from .env)
# ─────────────────────────────────────────
_single = os.getenv("GROQ_API_KEY", "").strip()
_raw_keys = os.getenv("GROQ_API_KEYS", "").strip()

GROQ_API_KEY_LIST = []
if _single:
    GROQ_API_KEY_LIST.append(_single)

if _raw_keys:
    # Add keys that are not already the single key
    GROQ_API_KEY_LIST.extend([
        k.strip() for k in _raw_keys.split(",") 
        if k.strip() and k.strip() != _single
    ])

# Fallback for older code that strictly requires a single key reference
GROQ_API_KEY = GROQ_API_KEY_LIST[0] if GROQ_API_KEY_LIST else ""

NEWS_API_KEY   = os.getenv("NEWS_API_KEY", "")

# ─────────────────────────────────────────
# LLM Settings (Groq + Llama)
# ─────────────────────────────────────────
LLM_MODEL       = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
LLM_TEMPERATURE = 0.3                        # Lower = more factual
LLM_MAX_TOKENS  = 250                        # Keep responses concise

# ─────────────────────────────────────────
# Embedding Settings
# ─────────────────────────────────────────
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # CPU-friendly

# ─────────────────────────────────────────
# RAG / Chunking Settings
# ─────────────────────────────────────────
# i3 + 8GB RAM friendly defaults
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", "380"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "70"))
TOP_K         = int(os.getenv("TOP_K", "2"))   # Number of chunks to retrieve

# ─────────────────────────────────────────
# File Paths
# ─────────────────────────────────────────
DATA_DIR         = os.path.join(BASE_DIR, "data")         # Put your PDF/TXT files here
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")  # Auto-created when index is built

# Hybrid multi-index RAG directories
WARM_DATA_DIR = os.path.join(BASE_DIR, "data_warm")
HOT_DATA_DIR = os.path.join(BASE_DIR, "data_hot")
FAISS_WARM_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index_warm")
FAISS_HOT_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index_hot")

# Weighted retrieval priorities (hot > warm > static by default)
RAG_WEIGHT_STATIC = float(os.getenv("RAG_WEIGHT_STATIC", "1.0"))
RAG_WEIGHT_WARM = float(os.getenv("RAG_WEIGHT_WARM", "1.12"))
RAG_WEIGHT_HOT = float(os.getenv("RAG_WEIGHT_HOT", "1.28"))

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
