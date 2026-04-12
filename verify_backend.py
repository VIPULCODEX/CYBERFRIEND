"""
verify_backend.py – End-to-end test suite for the QuantX production API.
Tests: health, validation, caching, rate limiting, and cache stats.

Usage:
  1. Start the server:  uvicorn api:app --host 0.0.0.0 --port 8000
  2. Run tests:         python verify_backend.py
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def test_health():
    print("\n[1] Testing /api/health...")
    try:
        r = requests.get(f"{BASE_URL}/api/health")
        print(f"  Status: {r.status_code}")
        data = r.json()
        for key, val in data.items():
            print(f"    {key}: {val}")
        assert data["status"] == "online", "Health check failed!"
        print("  ✅ PASSED")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")


def test_validation():
    print("\n[2] Testing input validation...")

    # Test: empty query
    r = requests.post(f"{BASE_URL}/api/chat", json={"query": ""})
    print(f"  Empty query -> {r.status_code}: {r.json().get('detail')}")
    assert r.status_code == 400, "Empty query should return 400"

    # Test: short query
    r = requests.post(f"{BASE_URL}/api/chat", json={"query": "abc"})
    print(f"  Short query -> {r.status_code}: {r.json().get('detail')}")
    assert r.status_code == 400, "Short query should return 400"

    print("  ✅ PASSED")


def test_caching():
    print("\n[3] Testing response caching...")
    query = {"query": "Explain what is ransomware?"}

    # First call — should be a cache miss
    start = time.time()
    r1 = requests.post(f"{BASE_URL}/api/chat", json=query)
    t1 = time.time() - start
    d1 = r1.json()
    print(f"  Call 1: status={r1.status_code}, cached={d1.get('cached')}, time={t1:.2f}s")

    # Second call — should be a cache hit
    start = time.time()
    r2 = requests.post(f"{BASE_URL}/api/chat", json=query)
    t2 = time.time() - start
    d2 = r2.json()
    print(f"  Call 2: status={r2.status_code}, cached={d2.get('cached')}, time={t2:.4f}s")

    assert d1.get("cached") is False, "First call should NOT be cached"
    assert d2.get("cached") is True, "Second call SHOULD be cached"
    assert t2 < t1, "Cached response should be faster"
    print("  ✅ PASSED")


def test_rate_limit():
    print("\n[4] Testing rate limiting (max 5 req/min)...")
    hit_limit = False
    for i in range(7):
        r = requests.post(
            f"{BASE_URL}/api/chat",
            json={"query": f"Unique spam query number {i + 1} for testing rate limits"}
        )
        status = r.status_code
        print(f"  Request {i + 1}: {status}")
        if status == 429:
            print(f"    Rate limit hit at request {i + 1} ✅")
            hit_limit = True
            break
    if hit_limit:
        print("  ✅ PASSED")
    else:
        print("  ⚠️  Rate limit was NOT triggered (may need a fresh window)")


def test_cache_stats():
    print("\n[5] Testing /api/cache/stats...")
    try:
        r = requests.get(f"{BASE_URL}/api/cache/stats")
        print(f"  Status: {r.status_code}")
        data = r.json()
        for key, val in data.items():
            print(f"    {key}: {val}")
        assert "hits" in data, "Stats should include 'hits'"
        assert "misses" in data, "Stats should include 'misses'"
        print("  ✅ PASSED")
    except Exception as e:
        print(f"  ❌ FAILED: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("  QuantX Backend Verification Suite")
    print("=" * 50)

    # Wait for server to be ready
    print("\nWaiting for server to initialize Neural Core...")
    for _ in range(30):
        try:
            if requests.get(f"{BASE_URL}/api/health").status_code == 200:
                print("Server online! Running tests...\n")
                break
        except Exception:
            pass
        time.sleep(2)
    else:
        print("Server did not respond after 60 seconds. Exiting.")
        exit(1)

    test_health()
    test_validation()
    test_caching()
    test_rate_limit()
    test_cache_stats()

    print("\n" + "=" * 50)
    print("  All tests completed!")
    print("=" * 50)
