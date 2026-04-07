"""
rag_pipeline.py – Handles document loading, chunking, embedding, and FAISS index management.
Supports both PDF and TXT files inside the data/ directory.
"""

import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP,
    FAISS_INDEX_PATH, DATA_DIR, TOP_K
)


class RAGPipeline:
    """
    Manages the full RAG pipeline:
    - Load documents (PDF/TXT)
    - Split into chunks
    - Embed with HuggingFace
    - Store/load with FAISS
    """

    def __init__(self):
        print("[*] Loading embedding model (this may take a moment)...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}  # CPU-only
        )
        self.vector_store = None

    # ──────────────────────────────────────
    # Document Loading
    # ──────────────────────────────────────
    def load_documents(self):
        """Load all .pdf and .txt files from the data/ directory."""
        documents = []

        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            print(f"[+] Created '{DATA_DIR}/' directory. Please add your PDF/TXT files there.")
            return documents

        files_found = [f for f in os.listdir(DATA_DIR) if f.endswith((".pdf", ".txt"))]
        if not files_found:
            print(f"[!] No PDF or TXT files found in '{DATA_DIR}/'.")
            return documents

        for filename in files_found:
            filepath = os.path.join(DATA_DIR, filename)
            try:
                if filename.endswith(".pdf"):
                    loader = PyPDFLoader(filepath)
                    documents.extend(loader.load())
                    print(f"  [OK] Loaded PDF: {filename}")
                elif filename.endswith(".txt"):
                    loader = TextLoader(filepath, encoding="utf-8")
                    documents.extend(loader.load())
                    print(f"  [OK] Loaded TXT: {filename}")
            except Exception as e:
                print(f"  [!] Skipped {filename} - Error: {e}")

        print(f"  [i] Total pages/sections loaded: {len(documents)}")
        return documents

    # ──────────────────────────────────────
    # Index Building
    # ──────────────────────────────────────
    def build_index(self):
        """Load documents, chunk them, embed, and save FAISS index."""
        print("\n[*] Loading documents from data/...")
        documents = self.load_documents()

        if not documents:
            raise ValueError(
                "No documents loaded. Add PDF or TXT files to the 'data/' folder.\n"
                "See the README for required resources."
            )

        print(f"\n[*] Splitting into chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP
        )
        chunks = splitter.split_documents(documents)
        print(f"  [+] Created {len(chunks)} chunks.")

        print("\n[*] Building FAISS vector store...")
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)

        # Save to disk for reuse
        os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
        self.vector_store.save_local(FAISS_INDEX_PATH)
        print(f"  [OK] Index saved to '{FAISS_INDEX_PATH}/'")

        return self.vector_store

    # ──────────────────────────────────────
    # Index Loading
    # ──────────────────────────────────────
    def load_index(self) -> bool:
        """Load existing FAISS index from disk. Returns True if successful."""
        index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
        if os.path.exists(index_file):
            print("[*] Loading existing FAISS index from disk...")
            self.vector_store = FAISS.load_local(
                FAISS_INDEX_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("  [OK] FAISS index loaded successfully.")
            return True
        return False

    # ──────────────────────────────────────
    # Smart Initialization
    # ──────────────────────────────────────
    def initialize(self):
        """
        Smart init: load existing index if available, else build from documents.
        Call this at startup.
        """
        if not self.load_index():
            print("[i] No saved index found. Building new index from documents...")
            self.build_index()

    # ──────────────────────────────────────
    # Retriever
    # ──────────────────────────────────────
    def get_retriever(self, k: int = TOP_K):
        """Return a retriever that fetches top-k relevant chunks."""
        if self.vector_store is None:
            raise ValueError("Vector store not ready. Call initialize() first.")
        return self.vector_store.as_retriever(search_kwargs={"k": k})
