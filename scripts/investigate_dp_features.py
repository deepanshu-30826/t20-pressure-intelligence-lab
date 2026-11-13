import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("Columns in delivery_pressure.parquet:")
dp_cols = [c[0] for c in conn.execute("DESCRIBE SELECT * FROM 'data/processed/delivery_pressure.parquet'").fetchall()]
print(dp_cols)

# Inspect pressure features
print("\nSample delivery pressure features:")
sample_dp = conn.execute("""
    SELECT 
        match_id, innings, overid, over_ball_num,
        runs_required, balls_remaining, wickets_in_hand, required_run_rate,
        current_par_score, score_differential,
        pressure_score_batting, is_high_batting_pressure,
        pressure_score_bowling, is_high_bowling_pressure
    FROM 'data/processed/delivery_pressure.parquet'
    WHERE is_primary_competition = TRUE AND innings = 2
    LIMIT 10
""").df()
print(sample_dp.to_string())
