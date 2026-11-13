import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("================================================================================")
print("             SENSITIVITY ANALYSIS: FORMAT ADJUSTMENT FACTOR                     ")
print("================================================================================")

# 1. Batters Sensitivity
b_eligible = conn.execute("""
    SELECT *
    FROM 'data/processed/ranked_batters.parquet'
    WHERE overall_balls_faced >= 100 AND pressure_balls_faced >= 40 AND pressure_matches >= 5
""").df()

# Compute rating without format factor (format_factor = 1.0)
raw_b_score = (
    0.35 * b_eligible['z_pressure_sr'] + 
    0.35 * b_eligible['z_shrunk_lift'] + 
    0.15 * (b_eligible['pressure_boundary_gain'] / 10.0) + 
    0.15 * (b_eligible['pressure_dot_reduction'] / 10.0)
)

b_eligible['rating_no_format'] = (
    50.0 + 12.0 * raw_b_score * b_eligible['sample_reliability_weight'] * b_eligible['match_consistency_factor'] * 1.0
).clip(0, 100).round(2)

b_sorted_no_fmt = b_eligible.sort_values('rating_no_format', ascending=False).reset_index(drop=True)
b_sorted_no_fmt['rank_no_format'] = b_sorted_no_fmt.index + 1

# Merge back with official ranking
b_comp = b_eligible[['player_id', 'player_name', 'composite_pressure_rating', 'rank', 'format_factor', 'format_contribution']].merge(
    b_sorted_no_fmt[['player_id', 'rating_no_format', 'rank_no_format']], on='player_id'
)

print("\n--- Top 10 Batters Sensitivity to Format Factor ---")
top10_b = b_comp.sort_values('rank').head(10)
top10_b['rank_delta'] = top10_b['rank'] - top10_b['rank_no_format']
print(top10_b[['rank', 'player_name', 'composite_pressure_rating', 'rank_no_format', 'rating_no_format', 'rank_delta', 'format_factor', 'format_contribution']].to_string(index=False))

# 2. Bowlers Sensitivity
bw_eligible = conn.execute("""
    SELECT *
    FROM 'data/processed/ranked_bowlers.parquet'
    WHERE overall_legal_balls >= 120 AND pressure_legal_balls >= 40 AND pressure_matches >= 5
""").df()

raw_bw_score = (
    0.35 * bw_eligible['z_pressure_econ'] + 
    0.30 * (bw_eligible['shrunk_econ_lift'] / 1.5) + 
    0.20 * bw_eligible['z_pressure_wickets'] + 
    0.10 * (bw_eligible['boundary_suppression'] / 5.0) + 
    0.05 * (bw_eligible['pressure_dot_gain'] / 5.0)
)

bw_eligible['rating_no_format'] = (
    50.0 + 12.0 * raw_bw_score * bw_eligible['sample_reliability_weight'] * bw_eligible['match_consistency_factor'] * 1.0
).clip(0, 100).round(2)

bw_sorted_no_fmt = bw_eligible.sort_values('rating_no_format', ascending=False).reset_index(drop=True)
bw_sorted_no_fmt['rank_no_format'] = bw_sorted_no_fmt.index + 1

bw_comp = bw_eligible[['player_id', 'player_name', 'composite_pressure_rating', 'rank', 'format_factor', 'format_contribution']].merge(
    bw_sorted_no_fmt[['player_id', 'rating_no_format', 'rank_no_format']], on='player_id'
)

print("\n--- Top 10 Bowlers Sensitivity to Format Factor ---")
top10_bw = bw_comp.sort_values('rank').head(10)
top10_bw['rank_delta'] = top10_bw['rank'] - top10_bw['rank_no_format']
print(top10_bw[['rank', 'player_name', 'composite_pressure_rating', 'rank_no_format', 'rating_no_format', 'rank_delta', 'format_factor', 'format_contribution']].to_string(index=False))
