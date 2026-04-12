"""
main.py - Entry point for Cybersecurity Friend AI Assistant
Run: python main.py
"""

import os
import sys

# Fix Windows console encoding (supports special characters)
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ─────────────────────────────────────────────────────
# Load .env FIRST before any other imports
# ─────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────────────
# Validate required configuration
# ─────────────────────────────────────────────────────
from config import GROQ_API_KEY, NEWS_API_KEY, TOP_K

if not GROQ_API_KEY:
    print("\n[X] ERROR: GROQ_API_KEY is missing!")
    print("    Create a .env file with: GROQ_API_KEY=your_key_here")
    print("    Get your key at: https://console.groq.com/keys\n")
    sys.exit(1)

if not NEWS_API_KEY:
    print("⚠️  WARNING: NEWS_API_KEY not set. Real-time news features will be disabled.")
    print("   Get a free key at: https://newsapi.org/\n")

# ─────────────────────────────────────────────────────
# Import core modules
# ─────────────────────────────────────────────────────
from rag_pipeline import RAGPipeline
from assistant import CybersecurityAssistant


# ─────────────────────────────────────────────────────
# CLI Banner
# ─────────────────────────────────────────────────────
BANNER = """
+----------------------------------------------------------+
|   [*]  Cybersecurity Friend - AI Assistant  [*]          |
|   Powered by RAG + Gemini + HuggingFace + NewsAPI        |
+----------------------------------------------------------+
|  Commands:                                               |
|    Type your question and press Enter                    |
|    'rebuild' -> Rebuild knowledge base index             |
|    'help'    -> Show example queries                     |
|    'exit'    -> Quit                                     |
+----------------------------------------------------------+
"""

HELP_TEXT = """
Example Queries You Can Try:
  -------------------------------------------------
  General Knowledge:
    > "What is phishing?"
    > "How does ransomware work?"
    > "What is a man-in-the-middle attack?"
    > "Explain SQL injection"

  Scenario-Based (Get Attack Type + Actions):
    > "I clicked on a suspicious link in an email, what should I do?"
    > "My computer is running very slowly and I see unknown processes"
    > "I got an email saying I won a prize and need to login"
    > "Someone is asking for my OTP over the phone"

  Real-Time News:
    > "What happened recently in cybersecurity?"
    > "Show me the latest cyber incidents"
    > "Any recent data breach news?"
  -------------------------------------------------
"""


# ─────────────────────────────────────────────────────
# Main CLI Loop
# ─────────────────────────────────────────────────────
def main():
    print(BANNER)

    # Step 1: Initialize RAG pipeline
    rag = RAGPipeline()
    try:
        rag.initialize()
    except ValueError as e:
        print(f"\n❌ Knowledge Base Error: {e}")
        print_resource_guide()
        sys.exit(1)

    # Step 2: Create assistant
    retriever = rag.get_retriever(k=TOP_K)
    assistant = CybersecurityAssistant(retriever)

    print("\n[OK] Assistant is ready! Ask me anything about cybersecurity.")
    print("   Type 'help' to see example queries.\n")

    # Step 3: Query loop
    while True:
        try:
            user_input = input("You: ").strip()

            # Handle empty input
            if not user_input:
                continue

            # ── Built-in Commands ──
            if user_input.lower() in ("exit", "quit", "bye", "q"):
                print("\nGoodbye! Stay safe online!\n")
                break

            elif user_input.lower() == "help":
                print(HELP_TEXT)
                continue

            elif user_input.lower() == "rebuild":
                print("\n🔨 Rebuilding knowledge base index from data/...")
                try:
                    rag.build_index()
                    retriever = rag.get_retriever(k=TOP_K)
                    assistant = CybersecurityAssistant(retriever)
                    print("✅ Index rebuilt and assistant updated!\n")
                except ValueError as e:
                    print(f"❌ {e}\n")
                continue

            # ── Main Query ──
            print("\n[...] Processing your query...\n")
            response = assistant.respond(user_input)

            # Pretty output
            print("=" * 62)
            print("[ASSISTANT] Response:")
            print("=" * 62)
            print(response)
            print("=" * 62 + "\n")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Stay secure!\n")
            break
        except Exception as e:
            print(f"\n⚠️  Unexpected error: {str(e)}")
            print("   Try again or type 'exit' to quit.\n")


# ─────────────────────────────────────────────────────
# Resource Guide (shown when data/ is empty)
# ─────────────────────────────────────────────────────
def print_resource_guide():
    print("""
📌 RESOURCES YOU NEED TO PROVIDE
══════════════════════════════════════════════════════
1. Add cybersecurity documents to the 'data/' folder.
   Supported formats: PDF (.pdf) or plain text (.txt)

   Recommended FREE resources:
   ┌─────────────────────────────────────────────────┐
   │ • NIST Cybersecurity Framework (PDF)            │
   │   https://nvlpubs.nist.gov/nistpubs/CSWP/...   │
   │                                                 │
   │ • OWASP Top 10 (PDF)                           │
   │   https://owasp.org/Top10/                     │
   │                                                 │
   │ • Cybersecurity & Infrastructure (CISA)        │
   │   https://www.cisa.gov/resources-tools         │
   │                                                 │
   │ • Your own cybersecurity notes / slides (TXT)  │
   └─────────────────────────────────────────────────┘

   ✅ TIP: A sample knowledge base file is included as:
      data/cybersecurity_kb.txt
      This will work out of the box for demo purposes!

2. Create a .env file in the project root:
   ┌─────────────────────────────────┐
   │ GOOGLE_API_KEY=your_key_here   │
   │ NEWS_API_KEY=your_key_here     │
   └─────────────────────────────────┘
══════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    main()
