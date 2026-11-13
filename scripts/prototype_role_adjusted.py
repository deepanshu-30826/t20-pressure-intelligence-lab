import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("================================================================================")
print("     ROLE-ADJUSTED PERFORMANCE & MATCH CONSISTENCY ENGINE PROTOTYPE            ")
print("================================================================================")

dp_path = 'data/processed/delivery_pressure.parquet'

# 1. Compute Phase & Role Baselines across all primary data
print("1. Computing benchmarks by batting role & phase...")
batter_benchmarks = conn.execute(f"""
    SELECT 
        CASE 
            WHEN batting_order BETWEEN 1 AND 3 THEN 'Top Order (1-3)'
            WHEN batting_order BETWEEN 4 AND 5 THEN 'Middle Order (4-5)'
            WHEN batting_order BETWEEN 6 AND 7 THEN 'Finishers (6-7)'
            ELSE 'Tail (8+)'
        END as position_band,
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'Powerplay (1-6)'
            WHEN overid BETWEEN 7 AND 15 THEN 'Middle (7-15)'
            ELSE 'Death (16-20)'
        END as phase,
        count(*) as total_balls,
        avg(batter_runs) * 100.0 as benchmark_sr
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
    GROUP BY position_band, phase
""").df()
print(batter_benchmarks)

print("\n2. Computing benchmarks by bowling phase...")
bowler_benchmarks = conn.execute(f"""
    SELECT 
        CASE 
            WHEN overid BETWEEN 1 AND 6 THEN 'Powerplay (1-6)'
            WHEN overid BETWEEN 7 AND 15 THEN 'Middle (7-15)'
            ELSE 'Death (16-20)'
        END as phase,
        count(*) as total_balls,
        avg(bowler_runs_conceded) * 6.0 as benchmark_econ,
        sum(case when is_bowler_wicket then 1 else 0 end) * 100.0 / count(*) as benchmark_wicket_rate
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
    GROUP BY phase
""").df()
print(bowler_benchmarks)

# Overall benchmarks
overall_benchmark_sr = conn.execute(f"""
    SELECT avg(batter_runs) * 100.0 FROM '{dp_path}' 
    WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
""").fetchone()[0]

overall_benchmark_econ = conn.execute(f"""
    SELECT avg(bowler_runs_conceded) * 6.0 FROM '{dp_path}' 
    WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
""").fetchone()[0]

print(f"\nOverall Primary Benchmark SR: {overall_benchmark_sr:.2f}")
print(f"Overall Primary Benchmark Economy: {overall_benchmark_econ:.2f}")
