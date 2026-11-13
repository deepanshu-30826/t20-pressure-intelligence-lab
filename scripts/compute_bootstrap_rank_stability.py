import duckdb
import numpy as np
import pandas as pd
import json

conn = duckdb.connect()

print("Loading match-level aggregates...")
dp_path = 'data/processed/delivery_pressure.parquet'

# 1. Batters match-level table for all eligible candidates (overall balls >= 100, pressure balls >= 40, matches >= 5)
eligible_batters = conn.execute("""
    SELECT player_id, player_name, pressure_balls_faced, pressure_matches, overall_strike_rate, composite_pressure_rating, rank
    FROM 'data/processed/ranked_batters.parquet'
    WHERE overall_balls_faced >= 100 AND pressure_balls_faced >= 40 AND pressure_matches >= 5
    ORDER BY composite_pressure_rating DESC
""").df()

# 2. Bowlers match-level table
eligible_bowlers = conn.execute("""
    SELECT player_id, player_name, pressure_legal_balls, pressure_matches, overall_economy, composite_pressure_rating, rank
    FROM 'data/processed/ranked_bowlers.parquet'
    WHERE overall_legal_balls >= 120 AND pressure_legal_balls >= 40 AND pressure_matches >= 5
    ORDER BY composite_pressure_rating DESC
""").df()

print(f"Eligible candidate pool: {len(eligible_batters)} batters, {len(eligible_bowlers)} bowlers.")

# Get primary match list
unique_matches = conn.execute(f"""
    SELECT DISTINCT match_id FROM '{dp_path}' WHERE is_primary_competition = TRUE
""").df()['match_id'].values
n_matches = len(unique_matches)
match_to_idx = {mid: i for i, mid in enumerate(unique_matches)}

# Extract batter match matrices
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

# Extract bowler match matrices
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

top_n_eval = 25

eval_batters = eligible_batters.head(top_n_eval)
b_pid_list = eval_batters['player_id'].tolist()
b_balls_matrix = np.zeros((n_matches, len(b_pid_list)), dtype=np.float32)
b_runs_matrix = np.zeros((n_matches, len(b_pid_list)), dtype=np.float32)

b_pid_to_col = {pid: col for col, pid in enumerate(b_pid_list)}
for _, row in b_df[b_df['player_id'].isin(b_pid_list)].iterrows():
    m_idx = match_to_idx.get(row['match_id'])
    p_col = b_pid_to_col.get(row['player_id'])
    if m_idx is not None and p_col is not None:
        b_balls_matrix[m_idx, p_col] = row['p_balls']
        b_runs_matrix[m_idx, p_col] = row['p_runs']

eval_bowlers = eligible_bowlers.head(top_n_eval)
bw_pid_list = eval_bowlers['player_id'].tolist()
bw_balls_matrix = np.zeros((n_matches, len(bw_pid_list)), dtype=np.float32)
bw_runs_matrix = np.zeros((n_matches, len(bw_pid_list)), dtype=np.float32)

bw_pid_to_col = {pid: col for col, pid in enumerate(bw_pid_list)}
for _, row in bw_df[bw_df['player_id'].isin(bw_pid_list)].iterrows():
    m_idx = match_to_idx.get(row['match_id'])
    p_col = bw_pid_to_col.get(row['player_id'])
    if m_idx is not None and p_col is not None:
        bw_balls_matrix[m_idx, p_col] = row['p_balls']
        bw_runs_matrix[m_idx, p_col] = row['p_runs']

# Run 1,000 Match-level Bootstraps
np.random.seed(42)
N_BOOT = 1000
print(f"Executing {N_BOOT} vectorized match bootstrap iterations...")

batter_ranks = np.zeros((N_BOOT, len(b_pid_list)), dtype=int)
bowler_ranks = np.zeros((N_BOOT, len(bw_pid_list)), dtype=int)

b_base_sr = eval_batters['overall_strike_rate'].values
bw_base_econ = eval_bowlers['overall_economy'].values

for b in range(N_BOOT):
    sample_indices = np.random.randint(0, n_matches, size=n_matches)
    
    # Batters
    boot_b_balls = b_balls_matrix[sample_indices, :].sum(axis=0)
    boot_b_runs = b_runs_matrix[sample_indices, :].sum(axis=0)
    boot_b_sr = np.where(boot_b_balls > 0, (boot_b_runs * 100.0) / boot_b_balls, b_base_sr)
    boot_b_lift = boot_b_sr - b_base_sr
    boot_b_shrunk_lift = boot_b_lift * (boot_b_balls / (boot_b_balls + 40.0))
    boot_b_score = 0.5 * boot_b_sr + 0.5 * boot_b_shrunk_lift
    
    order = np.argsort(-boot_b_score)
    ranks = np.empty_like(order)
    ranks[order] = np.arange(1, len(order) + 1)
    batter_ranks[b, :] = ranks

    # Bowlers
    boot_bw_balls = bw_balls_matrix[sample_indices, :].sum(axis=0)
    boot_bw_runs = bw_runs_matrix[sample_indices, :].sum(axis=0)
    boot_bw_econ = np.where(boot_bw_balls > 0, (boot_bw_runs * 6.0) / boot_bw_balls, bw_base_econ)
    boot_bw_lift = bw_base_econ - boot_bw_econ
    boot_bw_shrunk_lift = boot_bw_lift * (boot_bw_balls / (boot_bw_balls + 40.0))
    boot_bw_score = -0.5 * boot_bw_econ + 0.5 * (boot_bw_shrunk_lift * 10.0)
    
    order_bw = np.argsort(-boot_bw_score)
    ranks_bw = np.empty_like(order_bw)
    ranks_bw[order_bw] = np.arange(1, len(order_bw) + 1)
    bowler_ranks[b, :] = ranks_bw

print("\n=== TOP 10 BATTERS RANK STABILITY (1,000 MATCH RESAMPLES) ===")
b_results = []
for i, pid in enumerate(b_pid_list[:10]):
    row = eval_batters.iloc[i]
    r_dist = batter_ranks[:, i]
    p_top5 = np.mean(r_dist <= 5) * 100.0
    p_top10 = np.mean(r_dist <= 10) * 100.0
    p_top15 = np.mean(r_dist <= 15) * 100.0
    med_rank = np.median(r_dist)
    q25, q75 = np.percentile(r_dist, [25, 75])
    ci_lower, ci_upper = np.percentile(r_dist, [2.5, 97.5])
    
    b_results.append({
        "Official Rank": int(row['rank']),
        "Player": row['player_name'],
        "Rating": float(row['composite_pressure_rating']),
        "P(Top 10)": f"{p_top10:.1f}%",
        "P(Top 5)": f"{p_top5:.1f}%",
        "Median Rank": f"{med_rank:.1f}",
        "IQR": f"[{q25:.0f} - {q75:.0f}]",
        "95% Rank CI": f"[{ci_lower:.0f} - {ci_upper:.0f}]",
        "Stability Tier": "ULTRA STABLE" if p_top10 >= 90 else ("HIGHLY STABLE" if p_top10 >= 75 else "MODERATE")
    })

b_res_df = pd.DataFrame(b_results)
print(b_res_df.to_string(index=False))

print("\n=== TOP 10 BOWLERS RANK STABILITY (1,000 MATCH RESAMPLES) ===")
bw_results = []
for i, pid in enumerate(bw_pid_list[:10]):
    row = eval_bowlers.iloc[i]
    r_dist = bowler_ranks[:, i]
    p_top5 = np.mean(r_dist <= 5) * 100.0
    p_top10 = np.mean(r_dist <= 10) * 100.0
    p_top15 = np.mean(r_dist <= 15) * 100.0
    med_rank = np.median(r_dist)
    q25, q75 = np.percentile(r_dist, [25, 75])
    ci_lower, ci_upper = np.percentile(r_dist, [2.5, 97.5])
    
    bw_results.append({
        "Official Rank": int(row['rank']),
        "Player": row['player_name'],
        "Rating": float(row['composite_pressure_rating']),
        "P(Top 10)": f"{p_top10:.1f}%",
        "P(Top 5)": f"{p_top5:.1f}%",
        "Median Rank": f"{med_rank:.1f}",
        "IQR": f"[{q25:.0f} - {q75:.0f}]",
        "95% Rank CI": f"[{ci_lower:.0f} - {ci_upper:.0f}]",
        "Stability Tier": "ULTRA STABLE" if p_top10 >= 90 else ("HIGHLY STABLE" if p_top10 >= 75 else "MODERATE")
    })

bw_res_df = pd.DataFrame(bw_results)
print(bw_res_df.to_string(index=False))

# Save json artifact
with open('artifacts/validation/bootstrap_rank_stability.json', 'w') as f:
    json.dump({
        "n_iterations": N_BOOT,
        "method": "Match-level clustered bootstrap with full candidate pool resampling",
        "batters": b_results,
        "bowlers": bw_results
    }, f, indent=2)
print("\nSaved artifacts/validation/bootstrap_rank_stability.json successfully.")
