import duckdb
import pandas as pd
import numpy as np
import os
import json

conn = duckdb.connect()

dp_path = 'data/processed/delivery_pressure.parquet'

print("=== COMPUTING ROLE-ADJUSTED PERFORMANCE AND MATCH CONSISTENCY ===")

# 1. Batting Role & Phase Benchmarks Map
bench_b = conn.execute(f"""
    SELECT 
        CASE 
            WHEN batting_order BETWEEN 1 AND 3 THEN 'Top'
            WHEN batting_order BETWEEN 4 AND 5 THEN 'Mid'
            WHEN batting_order BETWEEN 6 AND 7 THEN 'Fin'
            ELSE 'Tail'
        END as pos,
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'PP'
            WHEN overid BETWEEN 7 AND 15 THEN 'MID'
            ELSE 'DTH'
        END as ph,
        avg(batter_runs) * 100.0 as bench_sr
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
    GROUP BY pos, ph
""").df()
bench_b_map = dict(zip(zip(bench_b['pos'], bench_b['ph']), bench_b['bench_sr']))
overall_bench_sr = 139.98

# 2. Bowling Phase Benchmarks Map
bench_bw = conn.execute(f"""
    SELECT 
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'PP'
            WHEN overid BETWEEN 7 AND 15 THEN 'MID'
            ELSE 'DTH'
        END as ph,
        avg(bowler_runs_conceded) * 6.0 as bench_econ,
        sum(case when is_bowler_wicket then 1 else 0 end) * 100.0 / count(*) as bench_pwr
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
    GROUP BY ph
""").df()
bench_bw_map = dict(zip(bench_bw['ph'], bench_bw['bench_econ']))
overall_bench_econ = 8.40

# -------------------------------------------------------------
# 1. BATTER CALCULATIONS
# -------------------------------------------------------------
print("Calculating batter role-adjusted baselines & match consistency...")

# Delivery level tagging for batters
b_delivs = conn.execute(f"""
    SELECT 
        match_id, striker_id as player_id, striker_name as player_name,
        is_high_batting_pressure, is_batter_ball, batter_runs, is_four, is_six,
        CASE 
            WHEN batting_order BETWEEN 1 AND 3 THEN 'Top'
            WHEN batting_order BETWEEN 4 AND 5 THEN 'Mid'
            WHEN batting_order BETWEEN 6 AND 7 THEN 'Fin'
            ELSE 'Tail'
        END as pos,
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'PP'
            WHEN overid BETWEEN 7 AND 15 THEN 'MID'
            ELSE 'DTH'
        END as ph
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
""").df()

# Add benchmark SR per delivery
b_delivs['expected_sr'] = b_delivs.apply(lambda r: bench_b_map.get((r['pos'], r['ph']), overall_bench_sr), axis=1)

# Overall and pressure metrics per player
b_player_summary = []
for pid, group in b_delivs.groupby('player_id'):
    pname = group['player_name'].iloc[0]
    total_matches = group['match_id'].nunique()
    overall_balls = len(group)
    overall_runs = group['batter_runs'].sum()
    overall_fours = group['is_four'].sum()
    overall_sixes = group['is_six'].sum()
    overall_dots = (group['batter_runs'] == 0).sum()
    overall_sr = (overall_runs * 100.0) / overall_balls
    overall_boundary_pct = ((overall_fours + overall_sixes) * 100.0) / overall_balls
    overall_dot_pct = (overall_dots * 100.0) / overall_balls

    # Pressure subset
    p_group = group[group['is_high_batting_pressure'] == True]
    p_balls = len(p_group)
    p_matches = p_group['match_id'].nunique()
    
    if p_balls == 0:
        continue
        
    p_runs = p_group['batter_runs'].sum()
    p_fours = p_group['is_four'].sum()
    p_sixes = p_group['is_six'].sum()
    p_dots = (p_group['batter_runs'] == 0).sum()
    p_sr = (p_runs * 100.0) / p_balls
    p_boundary_pct = ((p_fours + p_sixes) * 100.0) / p_balls
    p_dot_pct = (p_dots * 100.0) / p_balls
    
    # Expected role-phase baseline SR under pressure
    expected_baseline_sr = p_group['expected_sr'].mean()
    
    # Role-adjusted metrics
    role_adj_psr = p_sr - expected_baseline_sr + overall_bench_sr
    role_lift = p_sr - expected_baseline_sr
    shrunk_lift = role_lift * (p_balls / (p_balls + 40.0))
    boundary_gain = p_boundary_pct - overall_boundary_pct
    dot_reduction = overall_dot_pct - p_dot_pct

    # Match-level consistency (matches with >= 5 pressure balls)
    match_evals = []
    for mid, m_group in p_group.groupby('match_id'):
        if len(m_group) >= 5:
            m_sr = (m_group['batter_runs'].sum() * 100.0) / len(m_group)
            m_expected = m_group['expected_sr'].mean()
            match_evals.append(1 if m_sr >= m_expected else 0)
            
    qual_matches = len(match_evals)
    consistency_pct = (sum(match_evals) * 100.0 / qual_matches) if qual_matches > 0 else 0.0

    b_player_summary.append({
        "player_id": pid,
        "player_name": pname,
        "total_matches": total_matches,
        "overall_balls_faced": overall_balls,
        "overall_strike_rate": round(overall_sr, 2),
        "pressure_balls_faced": p_balls,
        "pressure_matches": p_matches,
        "pressure_strike_rate": round(p_sr, 2),
        "expected_baseline_sr": round(expected_baseline_sr, 2),
        "role_adjusted_psr": round(role_adj_psr, 2),
        "role_lift": round(role_lift, 2),
        "shrunk_sr_lift": round(shrunk_lift, 2),
        "boundary_gain": round(boundary_gain, 2),
        "dot_reduction": round(dot_reduction, 2),
        "qualifying_matches": qual_matches,
        "match_consistency_pct": round(consistency_pct, 1)
    })

b_df_pool = pd.DataFrame(b_player_summary)

# -------------------------------------------------------------
# 2. BOWLER CALCULATIONS
# -------------------------------------------------------------
print("Calculating bowler phase-adjusted baselines & match consistency...")

bw_delivs = conn.execute(f"""
    SELECT 
        match_id, bowler_id as player_id, bowler_name as player_name,
        is_high_bowling_pressure, is_legal_ball, bowler_runs_conceded,
        is_four, is_six, is_bowler_wicket,
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'PP'
            WHEN overid BETWEEN 7 AND 15 THEN 'MID'
            ELSE 'DTH'
        END as ph
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
""").df()

bw_delivs['expected_econ'] = bw_delivs['ph'].map(bench_bw_map)

bw_player_summary = []
for pid, group in bw_delivs.groupby('player_id'):
    pname = group['player_name'].iloc[0]
    total_matches = group['match_id'].nunique()
    overall_balls = len(group)
    overall_runs = group['bowler_runs_conceded'].sum()
    overall_fours = group['is_four'].sum()
    overall_sixes = group['is_six'].sum()
    overall_dots = (group['bowler_runs_conceded'] == 0).sum()
    overall_econ = (overall_runs * 6.0) / overall_balls
    overall_boundary_pct = ((overall_fours + overall_sixes) * 100.0) / overall_balls
    overall_dot_pct = (overall_dots * 100.0) / overall_balls

    p_group = group[group['is_high_bowling_pressure'] == True]
    p_balls = len(p_group)
    p_matches = p_group['match_id'].nunique()
    
    if p_balls == 0:
        continue
        
    p_runs = p_group['bowler_runs_conceded'].sum()
    p_wkts = p_group['is_bowler_wicket'].sum()
    p_fours = p_group['is_four'].sum()
    p_sixes = p_group['is_six'].sum()
    p_dots = (p_group['bowler_runs_conceded'] == 0).sum()
    p_econ = (p_runs * 6.0) / p_balls
    p_wkt_rate = (p_wkts * 100.0) / p_balls
    p_boundary_pct = ((p_fours + p_sixes) * 100.0) / p_balls
    p_dot_pct = (p_dots * 100.0) / p_balls
    
    expected_baseline_econ = p_group['expected_econ'].mean()
    
    role_adj_pecon = p_econ - expected_baseline_econ + overall_bench_econ
    role_lift = expected_baseline_econ - p_econ # positive is better
    shrunk_lift = role_lift * (p_balls / (p_balls + 40.0))
    boundary_suppression = overall_boundary_pct - p_boundary_pct
    dot_gain = p_dot_pct - overall_dot_pct

    # Match-level consistency (matches with >= 6 legal pressure balls)
    match_evals = []
    for mid, m_group in p_group.groupby('match_id'):
        if len(m_group) >= 6:
            m_econ = (m_group['bowler_runs_conceded'].sum() * 6.0) / len(m_group)
            m_expected = m_group['expected_econ'].mean()
            match_evals.append(1 if m_econ <= m_expected else 0)
            
    qual_matches = len(match_evals)
    consistency_pct = (sum(match_evals) * 100.0 / qual_matches) if qual_matches > 0 else 0.0

    bw_player_summary.append({
        "player_id": pid,
        "player_name": pname,
        "total_matches": total_matches,
        "overall_legal_balls": overall_balls,
        "overall_economy": round(overall_econ, 2),
        "pressure_legal_balls": p_balls,
        "pressure_matches": p_matches,
        "pressure_economy": round(p_econ, 2),
        "expected_baseline_econ": round(expected_baseline_econ, 2),
        "role_adjusted_pecon": round(role_adj_pecon, 2),
        "role_lift": round(role_lift, 2),
        "shrunk_econ_lift": round(shrunk_lift, 2),
        "pressure_wicket_rate": round(p_wkt_rate, 2),
        "boundary_suppression": round(boundary_suppression, 2),
        "dot_gain": round(dot_gain, 2),
        "qualifying_matches": qual_matches,
        "match_consistency_pct": round(consistency_pct, 1)
    })

bw_df_pool = pd.DataFrame(bw_player_summary)

print(f"Generated candidate pools: {len(b_df_pool)} batters, {len(bw_df_pool)} bowlers.")

# -------------------------------------------------------------
# 3. COMPOSITE RATING STANDARDIZATION & RANKING
# -------------------------------------------------------------
print("\nStandardizing metrics across eligible pool (>=100 pressure balls, >=10 matches)...")

# Batters Eligible
b_eligible = b_df_pool[
    (b_df_pool['overall_balls_faced'] >= 100) & 
    (b_df_pool['pressure_balls_faced'] >= 100) & 
    (b_df_pool['pressure_matches'] >= 10)
].copy()

def z_score(series):
    return (series - series.mean()) / (series.std() + 1e-6)

b_eligible['z_role_psr'] = z_score(b_eligible['role_adjusted_psr'])
b_eligible['z_shrunk_lift'] = z_score(b_eligible['shrunk_sr_lift'])
b_eligible['z_boundary'] = z_score(b_eligible['boundary_gain'])
b_eligible['z_dot'] = z_score(b_eligible['dot_reduction'])
b_eligible['z_consistency'] = z_score(b_eligible['match_consistency_pct'])

# Raw composite (weights: 30%, 35%, 15%, 10%, 10%)
raw_b = (
    0.30 * b_eligible['z_role_psr'] + 
    0.35 * b_eligible['z_shrunk_lift'] + 
    0.15 * b_eligible['z_boundary'] + 
    0.10 * b_eligible['z_dot'] + 
    0.10 * b_eligible['z_consistency']
)
b_eligible['composite_pressure_rating'] = (50.0 + 12.0 * raw_b).clip(0, 100).round(2)
b_eligible = b_eligible.sort_values('composite_pressure_rating', ascending=False).reset_index(drop=True)
b_eligible['rank'] = b_eligible.index + 1

# Bowlers Eligible
bw_eligible = bw_df_pool[
    (bw_df_pool['overall_legal_balls'] >= 120) & 
    (bw_df_pool['pressure_legal_balls'] >= 100) & 
    (bw_df_pool['pressure_matches'] >= 10)
].copy()

# For economy, lower is better, so z-score is inverted
bw_eligible['z_role_pecon'] = (bw_eligible['role_adjusted_pecon'].mean() - bw_eligible['role_adjusted_pecon']) / (bw_eligible['role_adjusted_pecon'].std() + 1e-6)
bw_eligible['z_shrunk_lift'] = z_score(bw_eligible['shrunk_econ_lift'])
bw_eligible['z_pwr'] = z_score(bw_eligible['pressure_wicket_rate'])
bw_eligible['z_boundary'] = z_score(bw_eligible['boundary_suppression'])
bw_eligible['z_dot'] = z_score(bw_eligible['dot_gain'])
bw_eligible['z_consistency'] = z_score(bw_eligible['match_consistency_pct'])

# Raw composite (weights: 25%, 30%, 20%, 10%, 5%, 10%)
raw_bw = (
    0.25 * bw_eligible['z_role_pecon'] + 
    0.30 * bw_eligible['z_shrunk_lift'] + 
    0.20 * bw_eligible['z_pwr'] + 
    0.10 * bw_eligible['z_boundary'] + 
    0.05 * bw_eligible['z_dot'] + 
    0.10 * bw_eligible['z_consistency']
)
bw_eligible['composite_pressure_rating'] = (50.0 + 12.0 * raw_bw).clip(0, 100).round(2)
bw_eligible = bw_eligible.sort_values('composite_pressure_rating', ascending=False).reset_index(drop=True)
bw_eligible['rank'] = bw_eligible.index + 1

print("\n=== REFINED TOP 10 BATTERS (ROLE-ADJUSTED + MATCH CONSISTENCY) ===")
print(b_eligible[['rank', 'player_name', 'composite_pressure_rating', 'pressure_strike_rate', 'expected_baseline_sr', 'role_adjusted_psr', 'shrunk_sr_lift', 'pressure_balls_faced', 'pressure_matches', 'match_consistency_pct', 'qualifying_matches']].head(10).to_string(index=False))

print("\n=== REFINED TOP 10 BOWLERS (PHASE-ADJUSTED + MATCH CONSISTENCY) ===")
print(bw_eligible[['rank', 'player_name', 'composite_pressure_rating', 'pressure_economy', 'expected_baseline_econ', 'role_adjusted_pecon', 'shrunk_econ_lift', 'pressure_legal_balls', 'pressure_matches', 'match_consistency_pct', 'qualifying_matches']].head(10).to_string(index=False))
