import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("================================================================================")
print("             EXHAUSTIVE AUDIT OF TOP 10 BATTERS PROFILES & METRICS              ")
print("================================================================================")
b_df = conn.execute("""
    SELECT 
        rank, player_id, player_name,
        composite_pressure_rating as rating,
        pressure_balls_faced as p_balls,
        pressure_matches as p_matches,
        pressure_strike_rate as p_sr,
        overall_strike_rate as base_sr,
        raw_sr_lift,
        shrunk_sr_lift,
        sample_reliability_weight as w_sample,
        match_consistency_factor as w_match,
        format_factor as w_format,
        confidence_level,
        bootstrap_95pct_ci as ci_sr,
        format_contribution
    FROM 'data/processed/ranked_batters.parquet'
    WHERE rank <= 10
    ORDER BY rank
""").df()
print(b_df.to_string(index=False))

print("\n================================================================================")
print("             EXHAUSTIVE AUDIT OF TOP 10 BOWLERS PROFILES & METRICS              ")
print("================================================================================")
bw_df = conn.execute("""
    SELECT 
        rank, player_id, player_name,
        composite_pressure_rating as rating,
        pressure_legal_balls as p_balls,
        pressure_matches as p_matches,
        pressure_economy as p_econ,
        overall_economy as base_econ,
        raw_econ_lift,
        shrunk_econ_lift,
        sample_reliability_weight as w_sample,
        match_consistency_factor as w_match,
        format_factor as w_format,
        confidence_level,
        bootstrap_95pct_ci as ci_econ,
        format_contribution
    FROM 'data/processed/ranked_bowlers.parquet'
    WHERE rank <= 10
    ORDER BY rank
""").df()
print(bw_df.to_string(index=False))

# Check parity with CSV files
print("\n--- Verifying CSV Parity ---")
csv_b = pd.read_csv('artifacts/rankings/top10_batters.csv')
csv_bw = pd.read_csv('artifacts/rankings/top10_bowlers.csv')

b_match = np.all(csv_b['player_name'].values == b_df['player_name'].values) and \
          np.allclose(csv_b['composite_pressure_rating'].values, b_df['rating'].values)
bw_match = np.all(csv_bw['player_name'].values == bw_df['player_name'].values) and \
           np.allclose(csv_bw['composite_pressure_rating'].values, bw_df['rating'].values)

print(f"Top 10 Batters CSV matches Parquet exactly: {b_match}")
print(f"Top 10 Bowlers CSV matches Parquet exactly: {bw_match}")
