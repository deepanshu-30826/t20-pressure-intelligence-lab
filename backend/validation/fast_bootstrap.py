"""
Vectorized, high-speed 1,000 Iteration Match Bootstrap.
Pre-computes match-level player vectors to run 1,000 bootstrap resamples in seconds.
Produces rigorous 95% Confidence Intervals for pressure SR and pressure Economy.
"""

import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
VALIDATION_DIR = os.path.join(WORKSPACE, "artifacts", "validation")
os.makedirs(VALIDATION_DIR, exist_ok=True)

con = duckdb.connect()

def run_fast_1000_bootstrap():
    print("=== STARTING VECTORIZED 1,000 ITERATION BOOTSTRAP VALIDATION ===")
    dp_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    
    # 1. Batters match-level table
    print("1. Extracting match-level matrices...")
    b_matrix = con.execute(f"""
        SELECT 
            match_id, 
            striker_id, 
            any_value(striker_name) as striker_name,
            sum(CASE WHEN is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as p_balls,
            sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as p_runs
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE
        GROUP BY match_id, striker_id
        HAVING p_balls > 0
    """).fetchdf()
    
    # 2. Bowlers match-level table
    bw_matrix = con.execute(f"""
        SELECT 
            match_id, 
            bowler_id, 
            any_value(bowler_name) as bowler_name,
            sum(CASE WHEN is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as p_balls,
            sum(CASE WHEN is_high_bowling_pressure THEN bowler_runs_conceded ELSE 0 END) as p_runs
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE
        GROUP BY match_id, bowler_id
        HAVING p_balls > 0
    """).fetchdf()

    unique_matches = con.execute(f"SELECT DISTINCT match_id FROM '{dp_path}' WHERE is_primary_competition = TRUE").fetchdf()['match_id'].values
    n_matches = len(unique_matches)
    match_to_idx = {mid: i for i, mid in enumerate(unique_matches)}
    
    print(f"   Indexed {n_matches} primary competition matches.")
    
    # Top 10 Batters to evaluate
    top_batters = [813, 1699, 1077, 6725, 20702, 796, 4986, 37052, 2984, 8101]
    # Top 10 Bowlers to evaluate
    top_bowlers = [2636, 7967, 781, 5979, 3298, 2417, 4219, 2382, 1107, 6256]

    print("2. Pre-building sparse match-by-player arrays...")
    b_match_indices = b_matrix['match_id'].map(match_to_idx).values
    b_pids = b_matrix['striker_id'].values
    b_pballs = b_matrix['p_balls'].values
    b_pruns = b_matrix['p_runs'].values

    bw_match_indices = bw_matrix['match_id'].map(match_to_idx).values
    bw_pids = bw_matrix['bowler_id'].values
    bw_pballs = bw_matrix['p_balls'].values
    bw_pruns = bw_matrix['p_runs'].values

    # Pre-filter matrices for the top candidates
    b_sub_dict = {}
    for pid in top_batters:
        mask = (b_pids == pid)
        b_sub_dict[pid] = {
            "name": b_matrix.loc[mask, 'striker_name'].iloc[0],
            "matches": b_match_indices[mask],
            "balls": b_pballs[mask],
            "runs": b_pruns[mask]
        }

    bw_sub_dict = {}
    for pid in top_bowlers:
        mask = (bw_pids == pid)
        bw_sub_dict[pid] = {
            "name": bw_matrix.loc[mask, 'bowler_name'].iloc[0],
            "matches": bw_match_indices[mask],
            "balls": bw_pballs[mask],
            "runs": bw_pruns[mask]
        }

    print("3. Executing 1,000 vectorized bootstrap resamples...")
    np.random.seed(42)
    N_BOOTSTRAP = 1000
    # Shape: (1000, n_matches) with integer counts of times each match was drawn
    bootstrap_counts = np.random.multinomial(n_matches, np.ones(n_matches)/n_matches, size=N_BOOTSTRAP)

    # Compute bootstrap SR for each batter across all 1000 iterations simultaneously
    batter_bootstrap_results = {}
    for pid in top_batters:
        data = b_sub_dict[pid]
        # weights shape: (1000, len(data['matches']))
        weights = bootstrap_counts[:, data['matches']]
        tot_balls = np.dot(weights, data['balls'])
        tot_runs = np.dot(weights, data['runs'])
        srs = np.where(tot_balls > 0, (tot_runs * 100.0) / tot_balls, np.nan)
        srs = srs[~np.isnan(srs)]
        
        batter_bootstrap_results[data['name']] = {
            "player_id": pid,
            "mean_sr": float(np.mean(srs)),
            "std_error": float(np.std(srs)),
            "ci_lower_2.5": float(np.percentile(srs, 2.5)),
            "ci_upper_97.5": float(np.percentile(srs, 97.5))
        }

    # Compute bootstrap Economy for each bowler across all 1000 iterations simultaneously
    bowler_bootstrap_results = {}
    for pid in top_bowlers:
        data = bw_sub_dict[pid]
        weights = bootstrap_counts[:, data['matches']]
        tot_balls = np.dot(weights, data['balls'])
        tot_runs = np.dot(weights, data['runs'])
        econs = np.where(tot_balls > 0, (tot_runs * 6.0) / tot_balls, np.nan)
        econs = econs[~np.isnan(econs)]
        
        bowler_bootstrap_results[data['name']] = {
            "player_id": pid,
            "mean_econ": float(np.mean(econs)),
            "std_error": float(np.std(econs)),
            "ci_lower_2.5": float(np.percentile(econs, 2.5)),
            "ci_upper_97.5": float(np.percentile(econs, 97.5))
        }

    print("\n--- BATTER 95% CONFIDENCE INTERVALS (1,000 VECTORIZED BOOTSTRAP RUNS) ---")
    for name, res in batter_bootstrap_results.items():
        print(f"{name:20s}: Mean SR = {res['mean_sr']:.1f} | 95% CI [{res['ci_lower_2.5']:.1f}, {res['ci_upper_97.5']:.1f}] | SE = {res['std_error']:.2f}")

    print("\n--- BOWLER 95% CONFIDENCE INTERVALS (1,000 VECTORIZED BOOTSTRAP RUNS) ---")
    for name, res in bowler_bootstrap_results.items():
        print(f"{name:20s}: Mean Econ = {res['mean_econ']:.2f} | 95% CI [{res['ci_lower_2.5']:.2f}, {res['ci_upper_97.5']:.2f}] | SE = {res['std_error']:.2f}")

    output_file = os.path.join(VALIDATION_DIR, "bootstrap_1000_validation_report.json")
    with open(output_file, "w") as f:
        json.dump({
            "iterations": N_BOOTSTRAP,
            "resampling_unit": "match_id (avoids intra-match delivery leakage)",
            "batters_confidence_intervals": batter_bootstrap_results,
            "bowlers_confidence_intervals": bowler_bootstrap_results
        }, f, indent=2)

    print(f"\nSaved 1,000 iteration bootstrap report to {output_file}")
    print("=== VECTORIZED BOOTSTRAP COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_fast_1000_bootstrap()
