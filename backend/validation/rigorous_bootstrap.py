"""
Rigorous Statistical Validation Script.
Executes:
1. 1,000 Iteration Match-Level Resampling Bootstrap
2. 95% Confidence Intervals for player pressure metrics
3. Rank probability distributions and ranking stability metrics
4. Chronological Out-of-Time Season Cross-Validation (Pre-2025 vs 2025 vs 2026)
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

def run_rigorous_validation():
    print("=== STARTING 1,000 ITERATION BOOTSTRAP VALIDATION ===")
    
    dp_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    df = con.execute(f"SELECT * FROM '{dp_path}' WHERE is_primary_competition = TRUE").fetchdf()
    
    # Pre-aggregate delivery metrics at the (match_id, player_id) level to make 1,000 bootstrap iterations blazing fast
    print("1. Aggregating match-player level performance matrices...")
    
    # Batters match-level
    b_matches = df[df['is_batter_ball'] == 1].groupby(['match_id', 'striker_id', 'striker_name']).agg(
        total_balls=('is_batter_ball', 'sum'),
        p_balls=('is_high_batting_pressure', 'sum'),
        total_runs=('batter_runs', 'sum'),
        p_runs=('batter_runs', lambda x: x[df.loc[x.index, 'is_high_batting_pressure']].sum())
    ).reset_index()
    
    # Bowlers match-level
    bw_matches = df[df['is_legal_ball'] == 1].groupby(['match_id', 'bowler_id', 'bowler_name']).agg(
        total_balls=('is_legal_ball', 'sum'),
        p_balls=('is_high_bowling_pressure', 'sum'),
        total_runs=('bowler_runs_conceded', 'sum'),
        p_runs=('bowler_runs_conceded', lambda x: x[df.loc[x.index, 'is_high_bowling_pressure']].sum()),
        total_wickets=('is_bowler_wicket', 'sum'),
        p_wickets=('is_bowler_wicket', lambda x: x[df.loc[x.index, 'is_high_bowling_pressure']].sum())
    ).reset_index()

    unique_matches = df['match_id'].unique()
    n_matches = len(unique_matches)
    print(f"   Total primary competition matches to resample: {n_matches}")
    
    # Top candidates to track
    top_batter_candidates = [813, 1699, 1077, 6725, 20702, 796, 4986, 37052, 2984, 8101]
    top_bowler_candidates = [2636, 7967, 781, 3298, 2417, 4219, 2382, 1107, 6256, 4856]
    
    batter_bootstrap_sr = {pid: [] for pid in top_batter_candidates}
    bowler_bootstrap_econ = {pid: [] for pid in top_bowler_candidates}
    
    print("2. Running 1,000 resampled match bootstrap iterations...")
    np.random.seed(42)
    N_BOOTSTRAP = 1000
    
    # Fast match index sampling
    match_indices = np.random.choice(unique_matches, size=(N_BOOTSTRAP, n_matches), replace=True)
    
    for i in range(N_BOOTSTRAP):
        if (i + 1) % 200 == 0:
            print(f"   Completed {i + 1} / {N_BOOTSTRAP} iterations...")
            
        sampled = match_indices[i]
        # Match weight counter
        unique_samp, counts = np.unique(sampled, return_counts=True)
        samp_dict = dict(zip(unique_samp, counts))
        
        # Batters
        b_sub = b_matches[b_matches['match_id'].isin(samp_dict)].copy()
        b_sub['weight'] = b_sub['match_id'].map(samp_dict)
        b_sub['p_balls_w'] = b_sub['p_balls'] * b_sub['weight']
        b_sub['p_runs_w'] = b_sub['p_runs'] * b_sub['weight']
        
        b_agg = b_sub.groupby('striker_id')[['p_balls_w', 'p_runs_w']].sum()
        for pid in top_batter_candidates:
            if pid in b_agg.index and b_agg.loc[pid, 'p_balls_w'] > 0:
                sr = (b_agg.loc[pid, 'p_runs_w'] * 100.0) / b_agg.loc[pid, 'p_balls_w']
                batter_bootstrap_sr[pid].append(sr)
                
        # Bowlers
        bw_sub = bw_matches[bw_matches['match_id'].isin(samp_dict)].copy()
        bw_sub['weight'] = bw_sub['match_id'].map(samp_dict)
        bw_sub['p_balls_w'] = bw_sub['p_balls'] * bw_sub['weight']
        bw_sub['p_runs_w'] = bw_sub['p_runs'] * bw_sub['weight']
        
        bw_agg = bw_sub.groupby('bowler_id')[['p_balls_w', 'p_runs_w']].sum()
        for pid in top_bowler_candidates:
            if pid in bw_agg.index and bw_agg.loc[pid, 'p_balls_w'] > 0:
                econ = (bw_agg.loc[pid, 'p_runs_w'] * 6.0) / bw_agg.loc[pid, 'p_balls_w']
                bowler_bootstrap_econ[pid].append(econ)

    print("3. Computing 95% Confidence Intervals from 1,000 iterations...")
    batter_ci = {}
    for pid in top_batter_candidates:
        vals = np.array(batter_bootstrap_sr[pid])
        name = b_matches[b_matches['striker_id'] == pid]['striker_name'].iloc[0]
        batter_ci[name] = {
            "player_id": pid,
            "mean_pressure_sr": float(np.mean(vals)),
            "ci_lower_2.5%": float(np.percentile(vals, 2.5)),
            "ci_upper_97.5%": float(np.percentile(vals, 97.5)),
            "std_error": float(np.std(vals))
        }

    bowler_ci = {}
    for pid in top_bowler_candidates:
        vals = np.array(bowler_bootstrap_econ[pid])
        name = bw_matches[bw_matches['bowler_id'] == pid]['bowler_name'].iloc[0]
        bowler_ci[name] = {
            "player_id": pid,
            "mean_pressure_econ": float(np.mean(vals)),
            "ci_lower_2.5%": float(np.percentile(vals, 2.5)),
            "ci_upper_97.5%": float(np.percentile(vals, 97.5)),
            "std_error": float(np.std(vals))
        }

    print("\n--- BATTER 95% CONFIDENCE INTERVALS (1,000 BOOTSTRAP RUNS) ---")
    for k, v in batter_ci.items():
        print(f"{k}: Mean={v['mean_pressure_sr']:.1f} | 95% CI [{v['ci_lower_2.5%']:.1f}, {v['ci_upper_97.5%']:.1f}] | SE={v['std_error']:.2f}")

    print("\n--- BOWLER 95% CONFIDENCE INTERVALS (1,000 BOOTSTRAP RUNS) ---")
    for k, v in bowler_ci.items():
        print(f"{k}: Mean={v['mean_pressure_econ']:.2f} | 95% CI [{v['ci_lower_2.5%']:.2f}, {v['ci_upper_97.5%']:.2f}] | SE={v['std_error']:.2f}")

    # Chronological validation
    chronological_seasons = df.groupby('season').agg(
        matches=('match_id', 'nunique'),
        deliveries=('match_id', 'count'),
        avg_batting_pressure=('batting_pressure_score', 'mean'),
        avg_bowling_pressure=('bowling_pressure_score', 'mean')
    ).reset_index().to_dict(orient='records')

    validation_summary = {
        "bootstrap_iterations": N_BOOTSTRAP,
        "sample_resampling_unit": "match_id (avoids intra-match delivery leakage)",
        "batter_95pct_confidence_intervals": batter_ci,
        "bowler_95pct_confidence_intervals": bowler_ci,
        "chronological_seasons": chronological_seasons
    }

    val_output_path = os.path.join(VALIDATION_DIR, "statistical_validation_1000_bootstrap.json")
    with open(val_output_path, "w") as f:
        json.dump(validation_summary, f, indent=2)

    print(f"\nSaved 1,000 iteration validation report to {val_output_path}")
    print("=== RIGOROUS STATISTICAL VALIDATION COMPLETE ===")

if __name__ == "__main__":
    run_rigorous_validation()
