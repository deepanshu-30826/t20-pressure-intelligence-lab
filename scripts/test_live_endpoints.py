import urllib.request
import json
import sys

endpoints = [
    ("Backend Root / Overview", "http://127.0.0.1:8000/api/overview"),
    ("Backend Top Batters", "http://127.0.0.1:8000/api/rankings/batters?limit=10"),
    ("Backend Top Bowlers", "http://127.0.0.1:8000/api/rankings/bowlers?limit=10"),
    ("Backend Batter Detail (Buttler)", "http://127.0.0.1:8000/api/players/813"),
    ("Backend Bowler Detail (Zampa)", "http://127.0.0.1:8000/api/players/2636"),
    ("Frontend UI Home", "http://localhost:3000/")
]

print("=== VERIFYING PRODUCTION HTTP ENDPOINTS ===")
all_pass = True

for name, url in endpoints:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'AuditBot/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.getcode()
            body = response.read()
            if status == 200:
                print(f"[PASS] {name}: HTTP {status} (Bytes received: {len(body)})")
                if "json" in url or "api" in url:
                    data = json.loads(body.decode('utf-8'))
                    if "rankings/batters" in url:
                        print(f"       Top 1 Batter: {data[0]['player_name']} (Rating: {data[0]['composite_pressure_rating']})")
                    elif "rankings/bowlers" in url:
                        print(f"       Top 1 Bowler: {data[0]['player_name']} (Rating: {data[0]['composite_pressure_rating']})")
                    elif "overview" in url:
                        print(f"       Overview matches: {data['total_matches']}, deliveries: {data['total_deliveries']}")
            else:
                print(f"[FAIL] {name}: HTTP {status}")
                all_pass = False
    except Exception as e:
        print(f"[FAIL] {name}: Exception: {e}")
        all_pass = False

if all_pass:
    print("\nALL HTTP ENDPOINTS VERIFIED AND PASSING!")
else:
    print("\nSOME HTTP ENDPOINTS FAILED!")
    sys.exit(1)
