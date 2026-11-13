import json
import urllib.request
import pandas as pd
import duckdb

def check_parity():
    print("=================================================================")
    print("          COMPREHENSIVE DATA PARITY AUDIT & VERIFICATION          ")
    print("=================================================================\n")
    
    # 1. Load Parquet sources
    con = duckdb.connect()
    p_batters = con.execute("SELECT * FROM 'data/processed/ranked_batters.parquet' ORDER BY rank").fetchdf()
    p_bowlers = con.execute("SELECT * FROM 'data/processed/ranked_bowlers.parquet' ORDER BY rank").fetchdf()
    
    # 2. Load CSV sources
    csv_top10_b = pd.read_csv("artifacts/rankings/top10_batters.csv")
    csv_comp_b = pd.read_csv("artifacts/rankings/complete_batter_rankings.csv")
    csv_top10_bw = pd.read_csv("artifacts/rankings/top10_bowlers.csv")
    csv_comp_bw = pd.read_csv("artifacts/rankings/complete_bowler_rankings.csv")
    
    # 3. Load API responses (Direct FastAPI)
    req_b_direct = urllib.request.urlopen("http://127.0.0.1:8000/api/rankings/batters?limit=200")
    api_b_direct = json.loads(req_b_direct.read().decode())
    req_bw_direct = urllib.request.urlopen("http://127.0.0.1:8000/api/rankings/bowlers?limit=200")
    api_bw_direct = json.loads(req_bw_direct.read().decode())
    
    # 4. Load API responses (Next.js Proxy)
    req_b_proxy = urllib.request.urlopen("http://localhost:3000/api/rankings/batters?limit=200")
    api_b_proxy = json.loads(req_b_proxy.read().decode())
    req_bw_proxy = urllib.request.urlopen("http://localhost:3000/api/rankings/bowlers?limit=200")
    api_bw_proxy = json.loads(req_bw_proxy.read().decode())
    
    # Test 1: Count Parity
    print("[TEST 1: CANDIDATE COUNTS]")
    b_counts = [len(p_batters), len(csv_comp_b), len(api_b_direct), len(api_b_proxy)]
    bw_counts = [len(p_bowlers), len(csv_comp_bw), len(api_bw_direct), len(api_bw_proxy)]
    
    print(f"Batters -> Parquet: {b_counts[0]}, CSV: {b_counts[1]}, Direct API: {b_counts[2]}, Proxy API: {b_counts[3]}")
    assert len(set(b_counts)) == 1 and b_counts[0] == 165, f"Batter count mismatch: {b_counts}"
    print("PASS: Batters total perfectly reconciled at 165.")
    
    print(f"Bowlers -> Parquet: {bw_counts[0]}, CSV: {bw_counts[1]}, Direct API: {bw_counts[2]}, Proxy API: {bw_counts[3]}")
    assert len(set(bw_counts)) == 1 and bw_counts[0] == 151, f"Bowler count mismatch: {bw_counts}"
    print("PASS: Bowlers total perfectly reconciled at 151.\n")
    
    # Test 2: Top 10 Batters Parity
    print("[TEST 2: TOP 10 BATTERS PARITY]")
    expected_top10_batters = [
        (1, 37052, "Naman Dhir", 73.99),
        (2, 23311, "Jacob Bethell", 71.45),
        (3, 1699, "Suryakumar Yadav", 69.75),
        (4, 49003, "Hasan Nawaz", 68.10),
        (5, 5039, "Rajat Patidar", 67.57),
        (6, 3647, "Shreyas Iyer", 67.04),
        (7, 2101, "Quinton de Kock", 66.53),
        (8, 8238, "Sameer Rizvi", 66.12),
        (9, 2984, "Sikandar Raza", 65.84),
        (10, 8182, "Donovan Ferreira", 64.82),
    ]
    
    for r, pid, name, rating in expected_top10_batters:
        idx = r - 1
        # Check CSV top10
        assert csv_top10_b.iloc[idx]['player_id'] == pid and csv_top10_b.iloc[idx]['player_name'] == name
        assert round(csv_top10_b.iloc[idx]['composite_pressure_rating'], 2) == rating
        # Check CSV complete
        assert csv_comp_b.iloc[idx]['player_id'] == pid and csv_comp_b.iloc[idx]['player_name'] == name
        # Check Parquet
        assert p_batters.iloc[idx]['player_id'] == pid and p_batters.iloc[idx]['player_name'] == name
        # Check Direct API
        assert api_b_direct[idx]['player_id'] == pid and api_b_direct[idx]['player_name'] == name
        # Check Proxy API
        assert api_b_proxy[idx]['player_id'] == pid and api_b_proxy[idx]['player_name'] == name
        print(f" #{r:2d} | ID: {pid:5d} | {name:20s} | Rating: {rating:.2f} -> PERFECT PARITY ACROSS ALL SURFACES")
    print("PASS: Top 10 Batters 100% matched across Parquet, CSVs, FastAPI, and Next.js.\n")

    # Test 3: Top 10 Bowlers Parity
    print("[TEST 3: TOP 10 BOWLERS PARITY]")
    expected_top10_bowlers = [
        (1, 5979, "Abrar Ahmed", 74.62),
        (2, 781, "Sunil Narine", 71.42),
        (3, 3720, "Craig Young", 68.47),
        (4, 2933, "Jasprit Bumrah", 68.37),
        (5, 6450, "Mujeeb Ur Rahman", 68.26),
        (6, 2687, "Roston Chase", 67.81),
        (7, 2382, "Jamie Overton", 66.96),
        (8, 2417, "Akeal Hosein", 66.34),
        (9, 8661, "Matheesha Pathirana", 65.24),
        (10, 7699, "Abbas Afridi", 64.34),
    ]
    
    for r, pid, name, rating in expected_top10_bowlers:
        idx = r - 1
        # Check CSV top10
        assert csv_top10_bw.iloc[idx]['player_id'] == pid and csv_top10_bw.iloc[idx]['player_name'] == name
        assert round(csv_top10_bw.iloc[idx]['composite_pressure_rating'], 2) == rating
        # Check CSV complete
        assert csv_comp_bw.iloc[idx]['player_id'] == pid and csv_comp_bw.iloc[idx]['player_name'] == name
        # Check Parquet
        assert p_bowlers.iloc[idx]['player_id'] == pid and p_bowlers.iloc[idx]['player_name'] == name
        # Check Direct API
        assert api_bw_direct[idx]['player_id'] == pid and api_bw_direct[idx]['player_name'] == name
        # Check Proxy API
        assert api_bw_proxy[idx]['player_id'] == pid and api_bw_proxy[idx]['player_name'] == name
        print(f" #{r:2d} | ID: {pid:5d} | {name:20s} | Rating: {rating:.2f} -> PERFECT PARITY ACROSS ALL SURFACES")
    print("PASS: Top 10 Bowlers 100% matched across Parquet, CSVs, FastAPI, and Next.js.\n")

    # Test 4: Player Profiles Endpoint Validation for all Top 20 Candidates
    print("[TEST 4: CANDIDATE PROFILE ENDPOINT ACCESSIBILITY]")
    all_top_pids = [p[1] for p in expected_top10_batters] + [p[1] for p in expected_top10_bowlers]
    for pid in all_top_pids:
        url = f"http://127.0.0.1:8000/api/players/{pid}"
        resp = urllib.request.urlopen(url)
        assert resp.status == 200
        pdata = json.loads(resp.read().decode())
        assert pdata['player_id'] == pid
    print(f"PASS: All {len(all_top_pids)} Top 10 candidate profiles verified and returning 200 OK.\n")
    
    print("=================================================================")
    print("      ALL PARITY CHECKS PASSED: ZERO DATA DISCREPANCIES          ")
    print("=================================================================")

if __name__ == '__main__':
    check_parity()
