# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
load_test_200.py - QuantX Cybersecurity Assistant
==================================================
Stress-tests the FastAPI backend with 200 simultaneous virtual users.

Key Design Decisions:
  - Each user gets a UNIQUE user_id so the 5-req/min rate limiter
    treats them as separate clients (mirrors real-world behaviour).
  - Users are dispatched in configurable WAVE_SIZE batches (default 50)
    to avoid crushing a local machine.
  - Detailed stats: per-wave results + overall P50/P75/P90/P99 latencies.
  - Color-coded terminal output (ANSI) for instant pass/fail visibility.
  - Works against local (127.0.0.1) or a remote URL via --url flag.

Usage:
  python load_test_200.py                    # local, 200 users
  python load_test_200.py --url https://...  # remote endpoint
  python load_test_200.py --users 50         # quick smoke test
"""

import asyncio
import argparse
import time
import uuid
import statistics
import httpx

# ─── ANSI colour helpers ───────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    return f"{GREEN}[OK]  {msg}{RESET}"
def warn(msg):  return f"{YELLOW}[WARN] {msg}{RESET}"
def err(msg):   return f"{RED}[ERR] {msg}{RESET}"
def info(msg):  return f"{CYAN}{msg}{RESET}"
def bold(msg):  return f"{BOLD}{msg}{RESET}"

# ─── Default config ────────────────────────────────────────────────────────────
DEFAULT_URL        = "http://127.0.0.1:8000/api/chat"
TOTAL_USERS        = 200
WAVE_SIZE          = 50        # concurrent users dispatched per wave
REQUEST_TIMEOUT_S  = 60.0      # generous timeout — LLM calls can be slow
QUERY              = "What is phishing and how do I protect my system?"
HEALTH_URL         = "http://127.0.0.1:8000/api/health"


# ─── Single-user request ──────────────────────────────────────────────────────
async def make_request(
    user_num: int,
    client: httpx.AsyncClient,
    api_url: str,
) -> dict:
    """Fire one POST /api/chat and return a result dict."""
    user_id = f"loadtest-user-{user_num:03d}-{uuid.uuid4().hex[:6]}"
    start = time.perf_counter()
    result = {
        "user_num": user_num,
        "user_id":  user_id,
        "success":  False,
        "status":   None,
        "latency":  None,
        "cached":   False,
        "error":    None,
    }
    try:
        resp = await client.post(
            api_url,
            json={"query": QUERY, "user_id": user_id},
            timeout=REQUEST_TIMEOUT_S,
        )
        result["status"]  = resp.status_code
        result["latency"] = time.perf_counter() - start

        if resp.status_code == 200:
            data = resp.json()
            result["success"] = True
            result["cached"]  = data.get("cached", False)
            tag = ok(f"[User {user_num:>3}] {result['latency']:.2f}s")
            if result["cached"]:
                tag += f"  {YELLOW}(cached){RESET}"
            print(tag)
        elif resp.status_code == 429:
            result["error"] = "Rate limited"
            print(warn(f"[User {user_num:>3}] 429 Rate limited"))
        else:
            result["error"] = f"HTTP {resp.status_code}"
            print(err(f"[User {user_num:>3}] HTTP {resp.status_code}"))

    except httpx.TimeoutException:
        result["latency"] = time.perf_counter() - start
        result["error"]   = "Timeout"
        print(err(f"[User {user_num:>3}] TIMEOUT after {result['latency']:.1f}s"))
    except Exception as exc:
        result["latency"] = time.perf_counter() - start
        result["error"]   = str(exc)
        print(err(f"[User {user_num:>3}] ERROR — {exc}"))

    return result


# ─── Health check ─────────────────────────────────────────────────────────────
async def health_check(url: str) -> bool:
    health_url = url.replace("/api/chat", "/api/health")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(health_url, timeout=10.0)
            data = resp.json()
            print(info(f"  Health: {data}"))
            return resp.status_code == 200 and data.get("pipeline_ready", False)
    except Exception as exc:
        print(err(f"  Health check failed: {exc}"))
        return False


# ─── Percentile helper ────────────────────────────────────────────────────────
def percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    data_sorted = sorted(data)
    idx = int(len(data_sorted) * pct / 100)
    idx = min(idx, len(data_sorted) - 1)
    return data_sorted[idx]


# ─── Wave dispatcher ──────────────────────────────────────────────────────────
async def run_wave(
    wave_num: int,
    user_start: int,
    wave_size: int,
    client: httpx.AsyncClient,
    api_url: str,
) -> list[dict]:
    print(bold(f"\n  Wave {wave_num} — Users {user_start}–{user_start + wave_size - 1}"))
    tasks = [
        make_request(user_start + i, client, api_url)
        for i in range(wave_size)
    ]
    wave_start = time.perf_counter()
    results = await asyncio.gather(*tasks)
    wave_time = time.perf_counter() - wave_start
    successes = [r for r in results if r["success"]]
    print(info(f"  Wave {wave_num} done in {wave_time:.2f}s | {len(successes)}/{wave_size} succeeded"))
    return list(results)


# ─── Main ─────────────────────────────────────────────────────────────────────
async def main(api_url: str, total_users: int, wave_size: int):
    print(bold(f"\n{'='*60}"))
    print(bold(f"  QuantX — 200-User Load Test"))
    print(bold(f"{'='*60}"))
    print(info(f"  Target  : {api_url}"))
    print(info(f"  Users   : {total_users}"))
    print(info(f"  Waves   : {(total_users + wave_size - 1) // wave_size} × {wave_size} concurrent"))
    print(info(f"  Query   : \"{QUERY[:60]}...\""))

    # Pre-flight health check
    print(bold("\n[ Pre-flight Health Check ]"))
    healthy = await health_check(api_url)
    if not healthy:
        print(warn("Backend may not be ready — proceeding anyway...\n"))
    else:
        print(ok("Backend is healthy and pipeline is ready.\n"))

    # Dispatch waves
    all_results: list[dict] = []
    test_start = time.perf_counter()

    print(bold("[ Dispatching Users ]"))
    # Shared AsyncClient with connection limits suitable for 200 users
    limits = httpx.Limits(max_connections=300, max_keepalive_connections=100)
    async with httpx.AsyncClient(limits=limits) as client:
        wave_num   = 1
        user_start = 1
        remaining  = total_users

        while remaining > 0:
            current_wave = min(wave_size, remaining)
            wave_results = await run_wave(wave_num, user_start, current_wave, client, api_url)
            all_results.extend(wave_results)
            remaining  -= current_wave
            user_start += current_wave
            wave_num   += 1
            if remaining > 0:
                await asyncio.sleep(0.3)   # tiny pause between waves

    total_time = time.perf_counter() - test_start

    # ─── Aggregate results ────────────────────────────────────────────────────
    successes  = [r for r in all_results if r["success"]]
    failures   = [r for r in all_results if not r["success"]]
    timeouts   = [r for r in failures if r["error"] == "Timeout"]
    rate_lim   = [r for r in failures if r["error"] == "Rate limited"]
    cached     = [r for r in successes if r["cached"]]
    latencies  = [r["latency"] for r in successes if r["latency"] is not None]
    all_lat    = [r["latency"] for r in all_results if r["latency"] is not None]

    print(bold(f"\n{'='*60}"))
    print(bold(f"  LOAD TEST RESULTS — {total_users} Users"))
    print(bold(f"{'='*60}"))

    # Pass/fail counts
    success_rate = len(successes) / total_users * 100
    if success_rate >= 95:
        rate_label = ok(f"{success_rate:.1f}%")
    elif success_rate >= 80:
        rate_label = warn(f"{success_rate:.1f}%")
    else:
        rate_label = err(f"{success_rate:.1f}%")

    print(f"\n  {'Total users':<28}: {total_users}")
    print(f"  {'Successful (200 OK)':<28}: {GREEN}{len(successes)}{RESET}")
    print(f"  {'Failed':<28}: {RED}{len(failures)}{RESET}")
    print(f"    {'  Rate limited (429)':<26}: {len(rate_lim)}")
    print(f"    {'  Timed out':<26}: {len(timeouts)}")
    print(f"    {'  Other errors':<26}: {len(failures) - len(rate_lim) - len(timeouts)}")
    print(f"  {'Cached responses':<28}: {YELLOW}{len(cached)}{RESET}")
    print(f"  {'Success rate':<28}: {rate_label}")
    print(f"  {'Total wall-clock time':<28}: {total_time:.2f}s")
    print(f"  {'Throughput':<28}: {total_users / total_time:.1f} req/s")

    if latencies:
        print(bold(f"\n  Latency (successful requests only):"))
        print(f"  {'Min':<28}: {min(latencies):.2f}s")
        print(f"  {'Max':<28}: {max(latencies):.2f}s")
        print(f"  {'Mean':<28}: {statistics.mean(latencies):.2f}s")
        print(f"  {'Median (P50)':<28}: {percentile(latencies, 50):.2f}s")
        print(f"  {'P75':<28}: {percentile(latencies, 75):.2f}s")
        print(f"  {'P90':<28}: {percentile(latencies, 90):.2f}s")
        print(f"  {'P99':<28}: {percentile(latencies, 99):.2f}s")
        if len(latencies) > 1:
            print(f"  {'Std-dev':<28}: {statistics.stdev(latencies):.2f}s")

    if failures:
        print(bold(f"\n  Error Breakdown:"))
        error_counts: dict[str, int] = {}
        for r in failures:
            key = r["error"] or "Unknown"
            error_counts[key] = error_counts.get(key, 0) + 1
        for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1]):
            print(f"  {error_type:<35}: {count}")

    # ─── Verdict ──────────────────────────────────────────────────────────────
    print(bold(f"\n{'='*60}"))
    if success_rate >= 95:
        print(ok(f"  VERDICT: PASS — backend handled {total_users} users with {success_rate:.1f}% success rate"))
    elif success_rate >= 80:
        print(warn(f"  VERDICT: PARTIAL — {success_rate:.1f}% success. Investigate failures above."))
    else:
        print(err(f"  VERDICT: FAIL — only {success_rate:.1f}% succeeded. Backend needs review."))
    print(bold(f"{'='*60}\n"))


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QuantX 200-User Load Test")
    parser.add_argument(
        "--url", default=DEFAULT_URL,
        help=f"API chat endpoint (default: {DEFAULT_URL})"
    )
    parser.add_argument(
        "--users", type=int, default=TOTAL_USERS,
        help=f"Total virtual users to simulate (default: {TOTAL_USERS})"
    )
    parser.add_argument(
        "--wave", type=int, default=WAVE_SIZE,
        help=f"Users dispatched per concurrent wave (default: {WAVE_SIZE})"
    )
    args = parser.parse_args()

    asyncio.run(main(args.url, args.users, args.wave))
