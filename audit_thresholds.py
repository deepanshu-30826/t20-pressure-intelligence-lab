import duckdb
import pandas as pd
import numpy as np

con = duckdb.connect()

print("=== SAMPLE SIZE THRESHOLD SENSITIVITY AUDIT ===")
dp_path = "data/processed/delivery_pressure.parquet"

# Check Batters at thresholds: 40, 60, 100, 150 pressure balls
for min_p_balls in [40, 60, 100, 150]:
    b_df = con.execute(f"""
        WITH b_agg AS (
            SELECT 
                striker_id,
                striker_name,
                count(DISTINCT match_id) as total_matches,
                count(DISTINCT CASE WHEN is_high_batting_pressure THEN match_id END) as p_matches,
                sum(is_batter_ball) as total_balls,
                sum(CASE WHEN is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as p_balls,
                sum(batter_runs) as total_runs,
                sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as p_runs
            FROM '{dp_path}'
            WHERE is_primary_competition = TRUE
            GROUP BY striker_id, striker_name
        )
        SELECT count(*) as count_eligible
        FROM b_agg
        WHERE total_balls >= 100 AND p_balls >= {min_p_balls} AND p_matches >= 5
    """).fetchone()[0]
    print(f"Batters eligible at min {min_p_balls} pressure balls: {b_df} players")

# Check Bowlers at thresholds: 40, 60, 100, 150 pressure balls
for min_p_balls in [40, 60, 100, 150]:
    bw_df = con.execute(f"""
        WITH bw_agg AS (
            SELECT 
                bowler_id,
                bowler_name,
                count(DISTINCT match_id) as total_matches,
                count(DISTINCT CASE WHEN is_high_bowling_pressure THEN match_id END) as p_matches,
                sum(is_legal_ball) as total_balls,
                sum(CASE WHEN is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as p_balls
            FROM '{dp_path}'
            WHERE is_primary_competition = TRUE
            GROUP BY bowler_id, bowler_name
        )
        SELECT count(*) as count_eligible
        FROM bw_agg
        WHERE total_balls >= 120 AND p_balls >= {min_p_balls} AND p_matches >= 5
    """).fetchone()[0]
    print(f"Bowlers eligible at min {min_p_balls} pressure balls: {bw_df} players")
