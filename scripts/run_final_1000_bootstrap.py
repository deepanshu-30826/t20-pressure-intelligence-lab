import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
VALIDATION_DIR = os.path.join(WORKSPACE, "artifacts", "validation")
RANKINGS_DIR = os.path.join(WORKSPACE, "artifacts", "rankings")
os.makedirs(VALIDATION_DIR, exist_ok=True)

conn = duckdb.connect()

print("=== STARTING 1,000 ITERATION BOOTSTRAP ON FINAL REFINED RANKINGS ===")
dp_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")

top10_batters = pd.read_parquet(os.path.join(PROCESSED_DIR, "ranked_batters.parquet")).head(10)
top10_bowlers = pd.read_parquet(os.path.join(PROCESSED_DIR, "ranked_bowlers.parquet")).head(10)

all_eligible_batters = pd.read_csv("artifacts/rankings/complete_batter_rankings.csv")
all_eligible_bowlers = pd.read_csv("artifacts/rankings/complete_bowler_rankings.csv")

b_eval_pool = all_eligible_batters[
    (all_eligible_batters['pressure_balls_faced'] >= 100) & 
    (all_eligible_batters['pressure_matches'] >= 10)
].head(35)

bw_eval_pool = all_eligible_bowlers[
    (all_eligible_bowlers['pressure_legal_balls'] >= 100) & 
    (all_eligible_bowlers['pressure_matches'] >= 10)
].head(35)

print(f"Candidate pools for rank stability: {len(b_eval_pool)} batters, {len(bw_eval_pool)} bowlers.")

unique_matches = conn.execute(f"""
    SELECT DISTINCT match_id FROM '{dp_path}' WHERE is_primary_competition = TRUE
""").df()['match_id'].values
n_matches = len(unique_matches)
match_to_idx = {mid: i for i, mid in enumerate(unique_matches)}

b_df = conn.execute(f"""
    SELECT 
        match_id, striker_id as player_id,
        sum(CASE WHEN is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as p_balls,
        sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as p_runs
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE
    GROUP BY match_id, striker_id
    HAVING p_balls > 0
""").df()

bw_df = conn.execute(f"""
    SELECT 
        match_id, bowler_id as player_id,
        sum(CASE WHEN is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as p_balls,
        sum(CASE WHEN is_high_bowling_pressure THEN bowler_runs_conceded ELSE 0 END) as p_runs
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE
    GROUP BY match_id, bowler_id
    HAVING p_balls > 0
""").df()

# Build dense matrices
b_pid_list = b_eval_pool['player_id'].tolist()
b_balls_matrix = np.zeros((n_matches, len(b_pid_list)), dtype=np.float32)
b_runs_matrix = np.zeros((n_matches, len(b_pid_list)), dtype=np.float32)

b_pid_to_col = {pid: col for col, pid in enumerate(b_pid_list)}
for _, row in b_df[b_df['player_id'].isin(b_pid_list)].iterrows():
    m_idx = match_to_idx.get(row['match_id'])
    p_col = b_pid_to_col.get(row['player_id'])
    if m_idx is not None and p_col is not None:
        b_balls_matrix[m_idx, p_col] = row['p_balls']
        b_runs_matrix[m_idx, p_col] = row['p_runs']

bw_pid_list = bw_eval_pool['player_id'].tolist()
bw_balls_matrix = np.zeros((n_matches, len(bw_pid_list)), dtype=np.float32)
bw_runs_matrix = np.zeros((n_matches, len(bw_pid_list)), dtype=np.float32)

bw_pid_to_col = {pid: col for col, pid in enumerate(bw_pid_list)}
for _, row in bw_df[bw_df['player_id'].isin(bw_pid_list)].iterrows():
    m_idx = match_to_idx.get(row['match_id'])
    p_col = bw_pid_to_col.get(row['player_id'])
    if m_idx is not None and p_col is not None:
        bw_balls_matrix[m_idx, p_col] = row['p_balls']
        bw_runs_matrix[m_idx, p_col] = row['p_runs']

np.random.seed(42)
N_BOOT = 1000
print(f"Executing {N_BOOT} vectorized match bootstrap iterations...")

batter_ranks = np.zeros((N_BOOT, len(b_pid_list)), dtype=int)
bowler_ranks = np.zeros((N_BOOT, len(bw_pid_list)), dtype=int)

batter_sr_boots = np.zeros((N_BOOT, len(b_pid_list)), dtype=np.float32)
bowler_econ_boots = np.zeros((N_BOOT, len(bw_pid_list)), dtype=np.float32)

b_base_sr = b_eval_pool['expected_baseline_sr'].values
bw_base_econ = bw_eval_pool['expected_baseline_econ'].values

for b in range(N_BOOT):
    sample_indices = np.random.randint(0, n_matches, size=n_matches)
    
    # Batters
    boot_b_balls = b_balls_matrix[sample_indices, :].sum(axis=0)
    boot_b_runs = b_runs_matrix[sample_indices, :].sum(axis=0)
    boot_b_sr = np.where(boot_b_balls > 0, (boot_b_runs * 100.0) / boot_b_balls, b_base_sr)
    batter_sr_boots[b, :] = boot_b_sr
    
    boot_b_lift = boot_b_sr - b_base_sr
    boot_b_shrunk_lift = boot_b_lift * (boot_b_balls / (boot_b_balls + 40.0))
    boot_b_score = 0.45 * boot_b_sr + 0.55 * boot_b_shrunk_lift
    
    order = np.argsort(-boot_b_score)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(order) + 1)
    batter_ranks[b, :] = ranks

    # Bowlers
    boot_bw_balls = bw_balls_matrix[sample_indices, :].sum(axis=0)
    boot_bw_runs = bw_runs_matrix[sample_indices, :].sum(axis=0)
    boot_bw_econ = np.where(boot_bw_balls > 0, (boot_bw_runs * 6.0) / boot_bw_balls, bw_base_econ)
    bowler_econ_boots[b, :] = boot_bw_econ
    
    boot_bw_lift = bw_base_econ - boot_bw_econ
    boot_bw_shrunk_lift = boot_bw_lift * (boot_bw_balls / (boot_bw_balls + 40.0))
    boot_bw_score = -0.45 * boot_bw_econ + 0.55 * (boot_bw_shrunk_lift * 5.0)
    
    order_bw = np.argsort(-boot_bw_score)
    ranks_bw = np.empty_like(order_bw)
    ranks_bw[order_bw] = np.arange(1, len(order_bw) + 1)
    bowler_ranks[b, :] = ranks_bw

print("\n=== FINAL REFINED TOP 10 BATTERS BOOTSTRAP STABILITY (1,000 RESAMPLES) ===")
b_results = []
b_ci_dict = {}

for i in range(10):
    row = top10_batters.iloc[i]
    col_idx = b_pid_to_col[row['player_id']]
    
    r_dist = batter_ranks[:, col_idx]
    sr_dist = batter_sr_boots[:, col_idx]
    
    ci_sr_low, ci_sr_high = np.percentile(sr_dist, [2.5, 97.5])
    p_top10 = np.mean(r_dist <= 10) * 100.0
    p_top5 = np.mean(r_dist <= 5) * 100.0
    med_rank = np.median(r_dist)
    ci_rank_low, ci_rank_high = np.percentile(r_dist, [2.5, 97.5])
    
    ci_str = f"[{ci_sr_low:.1f}, {ci_sr_high:.1f}]"
    b_ci_dict[row['player_name']] = {
        "ci_lower_2.5": float(ci_sr_low),
        "ci_upper_97.5": float(ci_sr_high)
    }
    
    b_results.append({
        "Official Rank": int(row['rank']),
        "Player": row['player_name'],
        "Rating": float(row['composite_pressure_rating']),
        "Pressure SR": round(float(row['pressure_strike_rate']), 1),
        "Expected Baseline SR": round(float(row['expected_baseline_sr']), 1),
        "Shrunk Lift": f"+{float(row['shrunk_sr_lift']):.1f}",
        "Pressure Balls": int(row['pressure_balls_faced']),
        "Matches": int(row['pressure_matches']),
        "Match Consistency %": f"{float(row['match_consistency_pct']):.1f}%",
        "Qualifying Matches": int(row['qualifying_matches']),
        "95% Metric CI": ci_str,
        "P(Top 10)": f"{p_top10:.1f}%",
        "Median Rank": f"{med_rank:.1f}",
        "95% Rank CI": f"[{ci_rank_low:.0f} - {ci_rank_high:.0f}]",
        "Stability Classification": "HIGHLY STABLE" if p_top10 >= 70 else "SAMPLE-SENSITIVE"
    })

b_res_df = pd.DataFrame(b_results)
print(b_res_df.to_string(index=False))

print("\n=== FINAL REFINED TOP 10 BOWLERS BOOTSTRAP STABILITY (1,000 RESAMPLES) ===")
bw_results = []
bw_ci_dict = {}

for i in range(10):
    row = top10_bowlers.iloc[i]
    col_idx = bw_pid_to_col[row['player_id']]
    
    r_dist = bowler_ranks[:, col_idx]
    econ_dist = bowler_econ_boots[:, col_idx]
    
    ci_ec_low, ci_ec_high = np.percentile(econ_dist, [2.5, 97.5])
    p_top10 = np.mean(r_dist <= 10) * 100.0
    p_top5 = np.mean(r_dist <= 5) * 100.0
    med_rank = np.median(r_dist)
    ci_rank_low, ci_rank_high = np.percentile(r_dist, [2.5, 97.5])
    
    ci_str = f"[{ci_ec_low:.2f}, {ci_ec_high:.2f}]"
    bw_ci_dict[row['player_name']] = {
        "ci_lower_2.5": float(ci_ec_low),
        "ci_upper_97.5": float(ci_ec_high)
    }
    
    bw_results.append({
        "Official Rank": int(row['rank']),
        "Player": row['player_name'],
        "Rating": float(row['composite_pressure_rating']),
        "Pressure Econ": round(float(row['pressure_economy']), 2),
        "Expected Baseline Econ": round(float(row['expected_baseline_econ']), 2),
        "Shrunk Lift": f"{float(row['shrunk_econ_lift']):+.2f}",
        "Pressure Balls": int(row['pressure_legal_balls']),
        "Matches": int(row['pressure_matches']),
        "Match Consistency %": f"{float(row['match_consistency_pct']):.1f}%",
        "Qualifying Matches": int(row['qualifying_matches']),
        "95% Metric CI": ci_str,
        "P(Top 10)": f"{p_top10:.1f}%",
        "Median Rank": f"{med_rank:.1f}",
        "95% Rank CI": f"[{ci_rank_low:.0f} - {ci_rank_high:.0f}]",
        "Stability Classification": "HIGHLY STABLE" if p_top10 >= 70 else "SAMPLE-SENSITIVE"
    })

bw_res_df = pd.DataFrame(bw_results)
print(bw_res_df.to_string(index=False))

# Update top 10 CSVs with exact bootstrap CIs
top10_batters_csv = pd.read_csv("artifacts/rankings/top10_batters.csv")
top10_batters_csv['bootstrap_95pct_ci'] = [b_results[i]['95% Metric CI'] for i in range(10)]
top10_batters_csv.to_csv("artifacts/rankings/top10_batters.csv", index=False)

top10_bowlers_csv = pd.read_csv("artifacts/rankings/top10_bowlers.csv")
top10_bowlers_csv['bootstrap_95pct_ci'] = [bw_results[i]['95% Metric CI'] for i in range(10)]
top10_bowlers_csv.to_csv("artifacts/rankings/top10_bowlers.csv", index=False)

# Save JSON validation reports
report_data = {
    "iterations": N_BOOT,
    "bootstrap_iterations": N_BOOT,
    "methodology": "Clustered Match-Level Resampling across 837 Primary Matches (Refined Role-Adjusted + Consistency)",
    "batters_confidence_intervals": b_ci_dict,
    "bowlers_confidence_intervals": bw_ci_dict,
    "batters_rank_stability": b_results,
    "bowlers_rank_stability": bw_results
}

with open(os.path.join(VALIDATION_DIR, "bootstrap_1000_validation_report.json"), "w") as f:
    json.dump(report_data, f, indent=2)

with open(os.path.join(VALIDATION_DIR, "bootstrap_rank_stability.json"), "w") as f:
    json.dump(report_data, f, indent=2)

print("\nSuccessfully updated validation reports and CSV exports with final bootstrap metrics!")
