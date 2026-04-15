"""
rag_pipeline.py - Hybrid multi-index RAG pipeline.

Indexes:
- static: general knowledge base (existing data/)
- warm: curated standards/knowledge (monthly refresh)
- hot: recent vulnerabilities/threat intel (daily refresh)
"""

import os
from typing import List, Optional, Tuple

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from config import (
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    FAISS_INDEX_PATH,
    DATA_DIR,
    TOP_K,
    WARM_DATA_DIR,
    HOT_DATA_DIR,
    FAISS_WARM_INDEX_PATH,
    FAISS_HOT_INDEX_PATH,
    RAG_WEIGHT_STATIC,
    RAG_WEIGHT_WARM,
    RAG_WEIGHT_HOT,
)


class HybridRetriever:
    """Merges ranked results from static/warm/hot indices with tier weighting."""

    def __init__(self, stores: List[Tuple[str, FAISS, float]], k: int):
        self.stores = stores
        self.k = k
        self.search_kwargs = {"k": k}

    def similarity_search_with_score(self, query: str, k: Optional[int] = None):
        limit = k or self.k
        merged: List[Tuple[Document, float]] = []

        for tier_name, store, weight in self.stores:
            if store is None:
                continue
            tier_hits = store.similarity_search_with_score(query, k=max(limit, 2))
            for doc, score in tier_hits:
                doc.metadata = doc.metadata or {}
                doc.metadata["tier"] = tier_name
                # Lower score is better for L2 distance; divide by weight to prefer hot/warm
                merged.append((doc, score / max(weight, 0.01)))

        dedup = {}
        for doc, score in merged:
            key = (doc.page_content[:300], doc.metadata.get("source", ""))
            if key not in dedup or score < dedup[key][1]:
                dedup[key] = (doc, score)

        ranked = sorted(dedup.values(), key=lambda item: item[1])
        return ranked[:limit]

    def get_relevant_documents(self, query: str):
        return [doc for doc, _ in self.similarity_search_with_score(query, k=self.k)]


class RAGPipeline:
    """Builds/loads static+warm+hot FAISS stores and returns a hybrid retriever."""

    def __init__(self):
        print("[*] Loading embedding model (CPU-safe mode)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
        )
        self.vector_store: Optional[FAISS] = None
        self.static_store: Optional[FAISS] = None
        self.warm_store: Optional[FAISS] = None
        self.hot_store: Optional[FAISS] = None

    def _load_documents_from_dir(self, directory: str, tier: str) -> List[Document]:
        documents: List[Document] = []
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            return documents

        files_found = [f for f in os.listdir(directory) if f.endswith((".pdf", ".txt"))]
        for filename in files_found:
            filepath = os.path.join(directory, filename)
            try:
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(filepath)
                    docs = loader.load()
                else:
                    loader = TextLoader(filepath, encoding="utf-8")
                    docs = loader.load()

                for d in docs:
                    d.metadata = d.metadata or {}
                    d.metadata["tier"] = tier
                    d.metadata["source_file"] = filename
                documents.extend(docs)
                print(f"  [OK] {tier} loaded: {filename}")
            except Exception as e:
                print(f"  [!] Skipped {filename} ({tier}) - Error: {e}")
        return documents

    def _split_docs(self, documents: List[Document]) -> List[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        return splitter.split_documents(documents)

    def _build_store(self, documents: List[Document], index_path: str, tier: str) -> Optional[FAISS]:
        if not documents:
            return None
        chunks = self._split_docs(documents)
        print(f"  [+] {tier}: {len(chunks)} chunks")
        store = FAISS.from_documents(chunks, self.embeddings)
        os.makedirs(index_path, exist_ok=True)
        store.save_local(index_path)
        print(f"  [OK] {tier} index saved: {index_path}")
        return store

    def _load_store(self, index_path: str, tier: str) -> Optional[FAISS]:
        index_file = os.path.join(index_path, "index.faiss")
        if not os.path.exists(index_file):
            return None
        print(f"[*] Loading existing {tier} index...")
        return FAISS.load_local(
            index_path,
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def build_index(self):
        """Backward-compatible static index build."""
        static_docs = self._load_documents_from_dir(DATA_DIR, tier="static")
        if not static_docs:
            raise ValueError(
                "No documents loaded in data/. Add PDF/TXT files to 'data/' and retry."
            )
        self.static_store = self._build_store(static_docs, FAISS_INDEX_PATH, tier="static")
        self.vector_store = self.static_store
        return self.static_store

    def build_all_indexes(self):
        """Build static, warm, and hot indexes from their directories."""
        print("\n[*] Building hybrid indices...")
        static_docs = self._load_documents_from_dir(DATA_DIR, tier="static")
        warm_docs = self._load_documents_from_dir(WARM_DATA_DIR, tier="warm")
        hot_docs = self._load_documents_from_dir(HOT_DATA_DIR, tier="hot")

        if not static_docs and not warm_docs and not hot_docs:
            raise ValueError(
                "No documents found across data/, data_warm/, data_hot/."
            )

        self.static_store = self._build_store(static_docs, FAISS_INDEX_PATH, tier="static")
        self.warm_store = self._build_store(warm_docs, FAISS_WARM_INDEX_PATH, tier="warm")
        self.hot_store = self._build_store(hot_docs, FAISS_HOT_INDEX_PATH, tier="hot")
        self.vector_store = self.static_store or self.warm_store or self.hot_store
        return self.vector_store

    def load_index(self) -> bool:
        """Backward-compatible static load."""
        self.static_store = self._load_store(FAISS_INDEX_PATH, tier="static")
        self.vector_store = self.static_store
        return self.static_store is not None

    def load_all_indexes(self) -> bool:
        self.static_store = self._load_store(FAISS_INDEX_PATH, tier="static")
        self.warm_store = self._load_store(FAISS_WARM_INDEX_PATH, tier="warm")
        self.hot_store = self._load_store(FAISS_HOT_INDEX_PATH, tier="hot")
        self.vector_store = self.static_store or self.warm_store or self.hot_store
        return self.vector_store is not None

    def initialize(self):
        """Load existing hybrid indices, else build from available tier directories."""
        if self.load_all_indexes():
            print("[OK] Hybrid indices loaded.")
            return
        print("[i] No saved indices found. Building hybrid indices...")
        self.build_all_indexes()

    def get_retriever(self, k: int = TOP_K):
        if self.vector_store is None:
            raise ValueError("Vector store not ready. Call initialize() first.")
        stores = [
            ("hot", self.hot_store, RAG_WEIGHT_HOT),
            ("warm", self.warm_store, RAG_WEIGHT_WARM),
            ("static", self.static_store, RAG_WEIGHT_STATIC),
        ]
        available = [(name, store, wt) for name, store, wt in stores if store is not None]
        return HybridRetriever(available, k=k)
