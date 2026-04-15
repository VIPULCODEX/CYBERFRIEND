"""
Rebuild all hybrid RAG indices (static + warm + hot).
"""

from rag_pipeline import RAGPipeline


def main():
    rag = RAGPipeline()
    rag.build_all_indexes()
    print("[OK] Hybrid index rebuild completed.")


if __name__ == "__main__":
    main()
