import urllib.request
import json

top10_batters = [
    (1, 37052, "Naman Dhir"),
    (2, 23311, "Jacob Bethell"),
    (3, 1699, "Suryakumar Yadav"),
    (4, 49003, "Hasan Nawaz"),
    (5, 5039, "Rajat Patidar"),
    (6, 3647, "Shreyas Iyer"),
    (7, 2101, "Quinton de Kock"),
    (8, 8238, "Sameer Rizvi"),
    (9, 2984, "Sikandar Raza"),
    (10, 8182, "Donovan Ferreira"),
]

top10_bowlers = [
    (1, 5979, "Abrar Ahmed"),
    (2, 781, "Sunil Narine"),
    (3, 3720, "Craig Young"),
    (4, 2933, "Jasprit Bumrah"),
    (5, 6450, "Mujeeb Ur Rahman"),
    (6, 2687, "Roston Chase"),
    (7, 2382, "Jamie Overton"),
    (8, 2417, "Akeal Hosein"),
    (9, 8661, "Matheesha Pathirana"),
    (10, 7699, "Abbas Afridi"),
]

def verify_profiles():
    print("=== VERIFYING ALL 20 CANDIDATE PLAYER PROFILE ENDPOINTS ===")
    
    all_ok = True
    print("\n--- BATTERS (10) ---")
    for rank, pid, name in top10_batters:
        url = f"http://127.0.0.1:8000/api/players/{pid}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            returned_name = data.get('name')
            has_batting = data.get('batting_profile') is not None
            p_rating = data['batting_profile']['composite_pressure_rating'] if has_batting else None
            status = "PASS" if returned_name == name and has_batting else "FAIL"
            if status == "FAIL":
                all_ok = False
            print(f"[{status}] Rank {rank:2d}: ID {pid:5d} -> API Name: '{returned_name}' (Expected: '{name}'), Rating: {p_rating}")
            
    print("\n--- BOWLERS (10) ---")
    for rank, pid, name in top10_bowlers:
        url = f"http://127.0.0.1:8000/api/players/{pid}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            returned_name = data.get('name')
            has_bowling = data.get('bowling_profile') is not None
            p_rating = data['bowling_profile']['composite_pressure_rating'] if has_bowling else None
            status = "PASS" if returned_name == name and has_bowling else "FAIL"
            if status == "FAIL":
                all_ok = False
            print(f"[{status}] Rank {rank:2d}: ID {pid:5d} -> API Name: '{returned_name}' (Expected: '{name}'), Rating: {p_rating}")

    # Also test through Next.js proxy
    print("\n--- TESTING THROUGH NEXT.JS PROXY (http://localhost:3000/api/players/...) ---")
    proxy_test_ids = [37052, 49003, 5039, 8238, 8182, 5979, 781, 2933]
    for pid in proxy_test_ids:
        url = f"http://localhost:3000/api/players/{pid}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"[PASS] Proxy PID {pid}: '{data.get('name')}'")

    print("\n=======================================================")
    if all_ok:
        print("ALL 20 PLAYER PROFILE ENDPOINTS RESOLVED 100% CORRECTLY!")
    else:
        print("SOME ENDPOINTS FAILED!")
        exit(1)

if __name__ == '__main__':
    verify_profiles()
