"""
k_analysis.py - Analyze impact of top-k retrieval depth on response quality
Runs the same query with k=1 through k=7 and saves results
"""
import os
import sys
import time
import json

# Fix encoding
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from rag_pipeline import RAGPipeline
from assistant import CybersecurityAssistant

QUERY = "What is phishing and how can I protect myself from it?"
K_VALUES = [1, 2, 3, 4, 5, 6, 7]

def run_analysis():
    print("=" * 70)
    print("K-VALUE IMPACT ANALYSIS")
    print(f"Query: {QUERY}")
    print("=" * 70)

    # Initialize pipeline once
    rag = RAGPipeline()
    rag.initialize()

    results = []

    for k in K_VALUES:
        print(f"\n{'─' * 60}")
        print(f"  Testing k = {k}")
        print(f"{'─' * 60}")

        # Get retriever with this k
        retriever = rag.get_retriever(k=k)

        # Get the raw retrieved chunks for analysis
        docs = retriever.invoke(QUERY)
        chunks_text = []
        for i, doc in enumerate(docs):
            chunks_text.append(f"Chunk {i+1}: {doc.page_content[:120]}...")

        # Create assistant and get response
        assistant = CybersecurityAssistant(retriever)

        start_time = time.time()
        try:
            response = assistant.respond(QUERY)
            elapsed = round(time.time() - start_time, 2)
            error = None
        except Exception as e:
            response = f"Error: {str(e)}"
            elapsed = round(time.time() - start_time, 2)
            error = str(e)

        result = {
            "k": k,
            "chunks_retrieved": len(docs),
            "chunks_preview": chunks_text,
            "response": response,
            "response_length": len(response),
            "response_time_seconds": elapsed,
            "error": error
        }
        results.append(result)

        print(f"  Chunks retrieved: {len(docs)}")
        print(f"  Response length: {len(response)} chars")
        print(f"  Time: {elapsed}s")
        print(f"  Response preview: {response[:150]}...")

        # Small delay to avoid rate limits
        time.sleep(1)

    # Save results
    output_file = "k_analysis_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'=' * 70}")
    print(f"Results saved to {output_file}")
    print(f"{'=' * 70}")

    # Print summary table
    print(f"\n{'k':>3} | {'Chunks':>6} | {'Response Len':>12} | {'Time':>6} | First 80 chars")
    print("-" * 120)
    for r in results:
        preview = r['response'][:80].replace('\n', ' ')
        print(f"{r['k']:>3} | {r['chunks_retrieved']:>6} | {r['response_length']:>12} | {r['response_time_seconds']:>5}s | {preview}")

if __name__ == "__main__":
    run_analysis()
