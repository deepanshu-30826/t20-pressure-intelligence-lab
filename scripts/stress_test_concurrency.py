import concurrent.futures
import urllib.request
import json
import time

URLS = [
    "http://127.0.0.1:8000/api/overview",
    "http://127.0.0.1:8000/api/rankings/batters?limit=200",
    "http://127.0.0.1:8000/api/rankings/bowlers?limit=200",
    "http://127.0.0.1:8000/api/players/37052",
    "http://127.0.0.1:8000/api/players/5979",
    "http://localhost:3000/api/rankings/batters?limit=200",
    "http://localhost:3000/api/rankings/bowlers?limit=200"
]

def fetch_url(url):
    try:
        t0 = time.time()
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            dt = time.time() - t0
            return (url, resp.status, len(data), dt, None)
    except Exception as e:
        return (url, 500, 0, 0, str(e))

def run_stress_test(concurrency=35, total_requests=70):
    print(f"Executing concurrent stress test: {total_requests} requests across {concurrency} threads...")
    requests = [URLS[i % len(URLS)] for i in range(total_requests)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        results = list(executor.map(fetch_url, requests))
        
    successes = [r for r in results if r[1] == 200]
    failures = [r for r in results if r[1] != 200]
    
    print(f"Results: {len(successes)}/{total_requests} Passed (HTTP 200).")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print(f" - {f[0]}: {f[4]}")
        return False
    else:
        avg_time = sum(r[3] for r in results) / len(results)
        print(f"Average response latency: {avg_time*1000:.1f}ms")
        print("ALL CONCURRENT QUERIES EXECUTED WITH ZERO ERRORS.")
        return True

if __name__ == '__main__':
    ok = run_stress_test()
    if not ok:
        exit(1)
