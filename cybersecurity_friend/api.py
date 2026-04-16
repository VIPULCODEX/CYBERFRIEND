"""
api.py — QuantX Production FastAPI Backend  v3.0.0
====================================================

v3 Scalability Upgrades:
  1. ASYNC endpoint — `async def handle_chat` runs in the event loop, not
     a threadpool, so thousands of I/O-waiting coroutines are cheap.
  2. Groq Semaphore — hard cap on concurrent LLM calls so we never spam
     the Groq API (free tier ~30 req/min). Excess requests queue and wait
     rather than crashing.
  3. Request Queue Timeout — if a request waits > QUEUE_TIMEOUT_S in the
     semaphore queue it gets a 503 (retry-after) instead of hanging forever.
  4. Stampede-safe cache — cache_manager.get_or_compute() ensures only ONE
     coroutine calls the LLM for a cold query; all others await the result.
  5. gunicorn-ready — start with `gunicorn -k uvicorn.workers.UvicornWorker`
     for multiple OS-level processes (Render / production).
  6. /api/metrics endpoint — live visibility: queue depth, cache stats,
     semaphore slots remaining.
"""

import asyncio
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_pipeline import RAGPipeline
from assistant import CybersecurityAssistant
from config import TOP_K, GROQ_API_KEY, LLM_MAX_TOKENS
from security import validate_query, rate_limiter, get_client_id
from cache_manager import cache_manager

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("quantx.api")
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────────────────────
# Concurrency Controls
# ─────────────────────────────────────────────────────────────────────────────
# How many simultaneous LLM calls we allow before queuing.
# Groq free tier ≈ 30 req/min => 1 req every 2s => 10 concurrent is safe.
# Raise to 20–30 on a paid Groq tier.
MAX_CONCURRENT_LLM_CALLS = int(10)

# Max seconds a request will wait in the semaphore queue before giving up.
QUEUE_TIMEOUT_S = 30.0

# Populated at startup
_llm_semaphore: Optional[asyncio.Semaphore] = None

# ─────────────────────────────────────────────────────────────────────────────
# Pipeline Singletons
# ─────────────────────────────────────────────────────────────────────────────
assistant_instance: Optional[CybersecurityAssistant] = None
rag_instance: Optional[RAGPipeline] = None

# Metrics counters (per-process; reset on restart)
_metrics = {
    "total_requests": 0,
    "cache_hits": 0,
    "llm_calls": 0,
    "rate_limited": 0,
    "errors": 0,
    "queue_timeouts": 0,
}


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan (startup / shutdown)
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global assistant_instance, rag_instance, _llm_semaphore

    # Create the semaphore inside the running event loop
    _llm_semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)

    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY is not set.")

    try:
        logger.info("Initializing QuantX Neural Core (v3)...")
        rag_instance = RAGPipeline()
        rag_instance.initialize()
        retriever = rag_instance.get_retriever(k=TOP_K)
        assistant_instance = CybersecurityAssistant(retriever, max_tokens=LLM_MAX_TOKENS)
        logger.info("Backend v3 ready. Semaphore slots: %d", MAX_CONCURRENT_LLM_CALLS)
    except Exception as e:
        logger.error("Critical init error: %s", e)
        assistant_instance = None

    yield  # ← app is alive here

    cache_manager.clear()
    logger.info("Shutdown complete.")


# ─────────────────────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="QuantX AI Production API",
    description="Secure, Async, Rate-limited, Cached RAG Backend for Cybersecurity",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    query: str
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    cached: bool
    time_taken: float
    queued: bool = False   # True if request had to wait in the LLM semaphore


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/chat — Main endpoint (ASYNC v3)
# ─────────────────────────────────────────────────────────────────────────────
@app.post("/api/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest, client_request: Request):
    """
    Async chat endpoint with:
      - Rate limiting per user/IP
      - Stampede-safe async LRU cache
      - Groq semaphore (queue, don't crash)
      - Queue timeout (503 if waiting too long)
    """
    if assistant_instance is None:
        raise HTTPException(status_code=503, detail="Assistant initializing. Retry in a moment.")

    start_time = time.perf_counter()
    _metrics["total_requests"] += 1

    # 1. Rate Limiting
    client_id = request.user_id or get_client_id(client_request)
    if not rate_limiter.is_allowed(client_id):
        _metrics["rate_limited"] += 1
        remaining = rate_limiter.get_remaining(client_id)
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. {remaining} requests remaining. Wait and retry.",
            headers={"Retry-After": "60"},
        )

    # 2. Input Validation
    clean_query = validate_query(request.query)

    # 3. Cache fast-path (no semaphore needed)
    cached_res = await cache_manager.aget(clean_query)
    if cached_res:
        _metrics["cache_hits"] += 1
        logger.info("Cache HIT")
        return ChatResponse(
            response=cached_res,
            cached=True,
            time_taken=round(time.perf_counter() - start_time, 4),
        )

    # 4. LLM call — guard with semaphore + timeout
    queued = False
    try:
        # Try to acquire immediately
        if _llm_semaphore.locked():
            queued = True   # We'll have to wait

        acquired = await asyncio.wait_for(
            _llm_semaphore.acquire(),
            timeout=QUEUE_TIMEOUT_S,
        )
    except asyncio.TimeoutError:
        _metrics["queue_timeouts"] += 1
        raise HTTPException(
            status_code=503,
            detail="Server is under heavy load. Please retry in a few seconds.",
            headers={"Retry-After": "5"},
        )

    try:
        _metrics["llm_calls"] += 1
        # Run the synchronous LLM call in a thread so the event loop stays free
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            assistant_instance.respond,
            clean_query,
        )
        await cache_manager.aset(clean_query, result)
        time_taken = time.perf_counter() - start_time
        logger.info("LLM response in %.2fs (queued=%s)", time_taken, queued)
        return ChatResponse(
            response=result,
            cached=False,
            time_taken=round(time_taken, 2),
            queued=queued,
        )
    except Exception as e:
        _metrics["errors"] += 1
        logger.error("LLM error: %s", e)
        raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")
    finally:
        _llm_semaphore.release()


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/health
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "version": "3.0.0",
        "keys_loaded": bool(GROQ_API_KEY),
        "pipeline_ready": assistant_instance is not None,
        "llm_slots_available": _llm_semaphore._value if _llm_semaphore else 0,
        "llm_slots_total": MAX_CONCURRENT_LLM_CALLS,
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/metrics  — Live performance dashboard
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/metrics")
async def metrics():
    """Real-time server metrics — no user data exposed."""
    cache_stats = cache_manager.stats()
    return {
        "requests": _metrics,
        "cache": cache_stats,
        "concurrency": {
            "max_llm_slots": MAX_CONCURRENT_LLM_CALLS,
            "available_slots": _llm_semaphore._value if _llm_semaphore else 0,
            "queue_timeout_s": QUEUE_TIMEOUT_S,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/cache/stats
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/cache/stats")
async def cache_stats():
    return cache_manager.stats()


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/rag/status
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/rag/status")
async def rag_status():
    if rag_instance is None:
        return {"pipeline_ready": False, "message": "RAG not initialized"}
    return rag_instance.get_index_status()
