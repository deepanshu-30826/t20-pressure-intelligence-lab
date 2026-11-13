import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("================================================================================")
print("     INVESTIGATION 1: SCOREBOARD RECONSTRUCTION ERROR & PRESSURE SENSITIVITY     ")
print("================================================================================")

# 1. Measure delivery-level score discrepancy
# In matches.csv, we have result, target, and revised_target
# Let's inspect the distribution of total recorded runs vs target across all 2nd innings
inn2_stats = conn.execute("""
    WITH inn2_totals AS (
        SELECT 
            match_id,
            sum(total_delivery_runs) as recorded_inn2_runs,
            count(*) as total_inn2_balls
        FROM 'data/processed/ball_by_ball.parquet'
        WHERE innings = 2 AND is_primary_competition = TRUE
        GROUP BY match_id
    ),
    inn1_totals AS (
        SELECT 
            match_id,
            sum(total_delivery_runs) as recorded_inn1_runs
        FROM 'data/processed/ball_by_ball.parquet'
        WHERE innings = 1 AND is_primary_competition = TRUE
        GROUP BY match_id
    )
    SELECT 
        m.match_id, m.comp_id, m.result, m.revised_target,
        i1.recorded_inn1_runs,
        i2.recorded_inn2_runs,
        CASE 
            WHEN m.revised_target IS NOT NULL AND m.revised_target > 0 THEN m.revised_target
            ELSE i1.recorded_inn1_runs + 1
        END as true_target,
        i2.total_inn2_balls
    FROM 'matches.csv' m
    JOIN inn1_totals i1 ON m.match_id = i1.match_id
    JOIN inn2_totals i2 ON m.match_id = i2.match_id
    WHERE m.result IS NOT NULL
""").df()

print(f"Total Primary 2nd Innings evaluated: {len(inn2_stats)}")

# Let's see how much pressure classification is affected if RRR is calculated with recorded vs shifted score
# Let's check delivery_pressure.parquet
dp_stats = conn.execute("""
    SELECT 
        count(*) as total_primary_deliveries,
        sum(case when is_high_batting_pressure then 1 else 0 end) as high_bat_pressure_deliveries,
        sum(case when is_high_bowling_pressure then 1 else 0 end) as high_bowl_pressure_deliveries,
        avg(pressure_score_batting) as mean_bat_pressure,
        avg(pressure_score_bowling) as mean_bowl_pressure
    FROM 'data/processed/delivery_pressure.parquet'
    WHERE is_primary_competition = TRUE
""").df()
print("\nCurrent Pressure Classification Baseline:")
print(dp_stats.to_string())

# Test sensitivity: What if pressure was purely context-based (Overs 15-20, or wickets in hand <= 4, or par deficit)?
# Compare current model vs context-based alternative
context_comparison = conn.execute("""
    SELECT 
        corr(pressure_score_batting, 
             CASE 
                WHEN overid >= 16 THEN 70.0 + (10 - wickets_in_hand)*2.0 
                WHEN overid >= 11 THEN 50.0 + (10 - wickets_in_hand)*2.0
                ELSE 35.0 + (10 - wickets_in_hand)*2.0
             END) as corr_with_context_heuristic,
        count(*) as total_deliveries
    FROM 'data/processed/delivery_pressure.parquet'
    WHERE is_primary_competition = TRUE
""").df()
print("\nCorrelation of Current Pressure Model with Pure Match-Context Heuristic:")
print(context_comparison.to_string())
