"""
api.py – Production-ready FastAPI backend for QuantX Cybersecurity Assistant

Features:
  - Rate limiting (5 req/min per user/IP)
  - Input validation & normalization
  - In-memory response caching with TTL
  - Privacy-safe logging (never logs query content)
  - CORS support for Flutter/web clients
  - Token-limited LLM responses (max_tokens=250)
"""

import time
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from rag_pipeline import RAGPipeline
from assistant import CybersecurityAssistant
from config import TOP_K, GROQ_API_KEY, LLM_MAX_TOKENS
from security import validate_query, rate_limiter, get_client_id
from cache_manager import cache_manager

# ─────────────────────────────────────────────────────
# Privacy-safe logging – only metadata, NEVER user queries
# ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("quantx.api")
logger.setLevel(logging.INFO)  # API module gets INFO for operational visibility


# ─────────────────────────────────────────────────────
# Pipeline Lifecycle (startup / shutdown)
# ─────────────────────────────────────────────────────
assistant_instance: Optional[CybersecurityAssistant] = None
rag_instance: Optional[RAGPipeline] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize RAG pipeline on startup, clean up on shutdown."""
    global assistant_instance, rag_instance

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set. API will fail to generate responses.")

    try:
        logger.info("Initializing QuantX Neural Core...")
        rag_instance = RAGPipeline()
        rag_instance.initialize()
        retriever = rag_instance.get_retriever(k=TOP_K)
        assistant_instance = CybersecurityAssistant(retriever, max_tokens=LLM_MAX_TOKENS)
        logger.info("Backend ready.")
    except Exception as e:
        logger.error("Critical initialization error: %s", e)
        assistant_instance = None

    yield  # App is running

    # Shutdown: clear cache to free memory
    cache_manager.clear()
    logger.info("Shutdown complete. Cache cleared.")


# ─────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────
app = FastAPI(
    title="QuantX AI Production API",
    description="Secure, Rate-limited, and Cached RAG Backend for Cybersecurity",
    version="2.1.0",
    lifespan=lifespan,
)

# CORS – Allow Flutter / web clients to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production to your Flutter app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None  # Optional identifier for rate limiting


class ChatResponse(BaseModel):
    response: str
    cached: bool
    time_taken: float


# ─────────────────────────────────────────────────────
# POST /api/chat – Main chat endpoint
# ─────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
def handle_chat(request: ChatRequest, client_request: Request):
    """
    Production-ready chat endpoint:
    1. Enforce Rate Limiting (5 req/min per user/IP)
    2. Validate & Normalize Input (strip, lowercase, min 5 chars)
    3. Check in-memory Cache (TTL-based)
    4. Call LLM via RAG pipeline (if cache miss)
    5. Return response with performance metrics

    Privacy: No user queries are logged or stored permanently.
    """
    if assistant_instance is None:
        raise HTTPException(
            status_code=503,
            detail="Assistant is not initialized. Try again in a moment.",
        )

    start_time = time.time()

    # 1. Rate Limiting — identify by user_id > IP fallback
    client_id = request.user_id or get_client_id(client_request)
    if not rate_limiter.is_allowed(client_id):
        remaining = rate_limiter.get_remaining(client_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max 5 requests per minute. "
                   f"Remaining: {remaining}. Please wait and try again.",
        )

    # 2. Input Validation & Normalization
    clean_query = validate_query(request.query)

    # 3. Cache Check — return instantly if query was seen before
    cached_res = cache_manager.get(clean_query)
    if cached_res:
        logger.info("Cache HIT — returning cached response.")
        return ChatResponse(
            response=cached_res,
            cached=True,
            time_taken=round(time.time() - start_time, 4),
        )

    # 4. LLM Generation via RAG
    try:
        logger.info("Cache MISS — calling LLM...")
        result = assistant_instance.respond(clean_query)

        # 5. Populate Cache for future identical queries
        cache_manager.set(clean_query, result)

        time_taken = time.time() - start_time
        logger.info("LLM response generated in %.2fs", time_taken)

        return ChatResponse(
            response=result,
            cached=False,
            time_taken=round(time_taken, 2),
        )
    except Exception as e:
        logger.error("LLM error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"LLM Error: {str(e)}",
        )


# ─────────────────────────────────────────────────────
# GET /api/health – Health check
# ─────────────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    """Returns server health status. Useful for monitoring and load balancers."""
    return {
        "status": "online",
        "keys_loaded": bool(GROQ_API_KEY),
        "pipeline_ready": assistant_instance is not None,
        "version": "2.1.0",
    }


# ─────────────────────────────────────────────────────
# GET /api/cache/stats – Cache performance metrics
# ─────────────────────────────────────────────────────
@app.get("/api/cache/stats")
def cache_stats():
    """Returns cache hit/miss stats for monitoring. No user data exposed."""
    return cache_manager.stats()


@app.get("/api/rag/status")
def rag_status():
    """Returns loaded RAG index diagnostics for troubleshooting retrieval issues."""
    if rag_instance is None:
        return {"pipeline_ready": False, "message": "RAG not initialized"}
    return rag_instance.get_index_status()
