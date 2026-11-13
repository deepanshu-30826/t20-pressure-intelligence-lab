"""
Analytics Engine for Batters and Bowlers.
Computes overall baseline performance, high-pressure performance,
deltas, dot ball %, boundary %, phase breakdowns, and sample diagnostics.
"""

import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")

con = duckdb.connect()

def compute_player_analytics():
    print("=== STARTING PLAYER ANALYTICS ENGINE ===")
    dp_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    
    # 1. BATTER ANALYTICS
    print("1. Computing Batter Analytics...")
    # Filter for Primary Competitions (IPL + T20I) as specified in problem statement
    df_batters = con.execute(f"""
        WITH batter_all AS (
            SELECT 
                striker_id as player_id,
                striker_name as player_name,
                count(DISTINCT match_id) as total_matches,
                count(DISTINCT CASE WHEN is_high_batting_pressure THEN match_id END) as pressure_matches,
                -- Overall stats
                sum(is_batter_ball) as overall_balls_faced,
                sum(batter_runs) as overall_runs,
                sum(CASE WHEN is_four THEN 1 ELSE 0 END) as overall_fours,
                sum(CASE WHEN is_six THEN 1 ELSE 0 END) as overall_sixes,
                sum(CASE WHEN is_batter_ball AND batter_runs = 0 THEN 1 ELSE 0 END) as overall_dot_balls,
                sum(CASE WHEN is_wicket AND dismissed_player_id = striker_id THEN 1 ELSE 0 END) as overall_dismissals,
                -- Pressure stats (batting_pressure_score >= 65)
                sum(CASE WHEN is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as pressure_balls_faced,
                sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as pressure_runs,
                sum(CASE WHEN is_high_batting_pressure AND is_four THEN 1 ELSE 0 END) as pressure_fours,
                sum(CASE WHEN is_high_batting_pressure AND is_six THEN 1 ELSE 0 END) as pressure_sixes,
                sum(CASE WHEN is_high_batting_pressure AND is_batter_ball AND batter_runs = 0 THEN 1 ELSE 0 END) as pressure_dot_balls,
                sum(CASE WHEN is_high_batting_pressure AND is_wicket AND dismissed_player_id = striker_id THEN 1 ELSE 0 END) as pressure_dismissals,
                -- Format contributions
                sum(CASE WHEN competition_tier = 'IPL' THEN is_batter_ball ELSE 0 END) as ipl_balls_faced,
                sum(CASE WHEN competition_tier = 'T20I' THEN is_batter_ball ELSE 0 END) as t20i_balls_faced,
                sum(CASE WHEN competition_tier = 'IPL' AND is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as ipl_pressure_balls,
                sum(CASE WHEN competition_tier = 'T20I' AND is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as t20i_pressure_balls
            FROM '{dp_path}'
            WHERE is_primary_competition = TRUE
            GROUP BY striker_id, striker_name
        )
        SELECT 
            *,
            -- Strike rates
            CASE WHEN overall_balls_faced > 0 THEN (overall_runs * 100.0) / overall_balls_faced ELSE 0.0 END as overall_strike_rate,
            CASE WHEN pressure_balls_faced > 0 THEN (pressure_runs * 100.0) / pressure_balls_faced ELSE 0.0 END as pressure_strike_rate,
            -- Averages
            CASE WHEN overall_dismissals > 0 THEN (overall_runs * 1.0) / overall_dismissals ELSE overall_runs * 1.0 END as overall_average,
            CASE WHEN pressure_dismissals > 0 THEN (pressure_runs * 1.0) / pressure_dismissals ELSE pressure_runs * 1.0 END as pressure_average,
            -- Dot ball %
            CASE WHEN overall_balls_faced > 0 THEN (overall_dot_balls * 100.0) / overall_balls_faced ELSE 0.0 END as overall_dot_pct,
            CASE WHEN pressure_balls_faced > 0 THEN (pressure_dot_balls * 100.0) / pressure_balls_faced ELSE 0.0 END as pressure_dot_pct,
            -- Boundary %
            CASE WHEN overall_balls_faced > 0 THEN ((overall_fours + overall_sixes) * 100.0) / overall_balls_faced ELSE 0.0 END as overall_boundary_pct,
            CASE WHEN pressure_balls_faced > 0 THEN ((pressure_fours + pressure_sixes) * 100.0) / pressure_balls_faced ELSE 0.0 END as pressure_boundary_pct
        FROM batter_all
    """).fetchdf()

    # 2. BOWLER ANALYTICS
    print("2. Computing Bowler Analytics...")
    df_bowlers = con.execute(f"""
        WITH bowler_all AS (
            SELECT 
                bowler_id as player_id,
                bowler_name as player_name,
                count(DISTINCT match_id) as total_matches,
                count(DISTINCT CASE WHEN is_high_bowling_pressure THEN match_id END) as pressure_matches,
                -- Overall stats
                sum(is_legal_ball) as overall_legal_balls,
                sum(bowler_runs_conceded) as overall_runs_conceded,
                sum(CASE WHEN is_bowler_wicket THEN 1 ELSE 0 END) as overall_wickets,
                sum(CASE WHEN is_legal_ball AND bowler_runs_conceded = 0 THEN 1 ELSE 0 END) as overall_dot_balls,
                sum(CASE WHEN is_four OR is_six THEN 1 ELSE 0 END) as overall_boundaries_conceded,
                -- Pressure stats (bowling_pressure_score >= 60)
                sum(CASE WHEN is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as pressure_legal_balls,
                sum(CASE WHEN is_high_bowling_pressure THEN bowler_runs_conceded ELSE 0 END) as pressure_runs_conceded,
                sum(CASE WHEN is_high_bowling_pressure AND is_bowler_wicket THEN 1 ELSE 0 END) as pressure_wickets,
                sum(CASE WHEN is_high_bowling_pressure AND is_legal_ball AND bowler_runs_conceded = 0 THEN 1 ELSE 0 END) as pressure_dot_balls,
                sum(CASE WHEN is_high_bowling_pressure AND (is_four OR is_six) THEN 1 ELSE 0 END) as pressure_boundaries_conceded,
                -- Format contributions
                sum(CASE WHEN competition_tier = 'IPL' THEN is_legal_ball ELSE 0 END) as ipl_legal_balls,
                sum(CASE WHEN competition_tier = 'T20I' THEN is_legal_ball ELSE 0 END) as t20i_legal_balls,
                sum(CASE WHEN competition_tier = 'IPL' AND is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as ipl_pressure_balls,
                sum(CASE WHEN competition_tier = 'T20I' AND is_high_bowling_pressure THEN is_legal_ball ELSE 0 END) as t20i_pressure_balls,
                -- Phase balls
                sum(CASE WHEN innings_phase = 'POWERPLAY' THEN is_legal_ball ELSE 0 END) as pp_balls,
                sum(CASE WHEN innings_phase = 'MIDDLE' THEN is_legal_ball ELSE 0 END) as mid_balls,
                sum(CASE WHEN innings_phase = 'DEATH' THEN is_legal_ball ELSE 0 END) as death_balls,
                any_value(pace_or_spin) as pace_or_spin
            FROM '{dp_path}'
            WHERE is_primary_competition = TRUE
            GROUP BY bowler_id, bowler_name
        )
        SELECT 
            *,
            -- Economy rates
            CASE WHEN overall_legal_balls > 0 THEN (overall_runs_conceded * 6.0) / overall_legal_balls ELSE 0.0 END as overall_economy,
            CASE WHEN pressure_legal_balls > 0 THEN (pressure_runs_conceded * 6.0) / pressure_legal_balls ELSE 0.0 END as pressure_economy,
            -- Strike rates (balls per wicket)
            CASE WHEN overall_wickets > 0 THEN (overall_legal_balls * 1.0) / overall_wickets ELSE 999.0 END as overall_strike_rate,
            CASE WHEN pressure_wickets > 0 THEN (pressure_legal_balls * 1.0) / pressure_wickets ELSE 999.0 END as pressure_strike_rate,
            -- Bowling Average
            CASE WHEN overall_wickets > 0 THEN (overall_runs_conceded * 1.0) / overall_wickets ELSE overall_runs_conceded * 1.0 END as overall_average,
            CASE WHEN pressure_wickets > 0 THEN (pressure_runs_conceded * 1.0) / pressure_wickets ELSE pressure_runs_conceded * 1.0 END as pressure_average,
            -- Dot ball %
            CASE WHEN overall_legal_balls > 0 THEN (overall_dot_balls * 100.0) / overall_legal_balls ELSE 0.0 END as overall_dot_pct,
            CASE WHEN pressure_legal_balls > 0 THEN (pressure_dot_balls * 100.0) / pressure_legal_balls ELSE 0.0 END as pressure_dot_pct,
            -- Boundary Conceded %
            CASE WHEN overall_legal_balls > 0 THEN (overall_boundaries_conceded * 100.0) / overall_legal_balls ELSE 0.0 END as overall_boundary_conceded_pct,
            CASE WHEN pressure_legal_balls > 0 THEN (pressure_boundaries_conceded * 100.0) / pressure_legal_balls ELSE 0.0 END as pressure_boundary_conceded_pct
        FROM bowler_all
    """).fetchdf()

    batters_path = os.path.join(PROCESSED_DIR, "batter_analytics.parquet")
    bowlers_path = os.path.join(PROCESSED_DIR, "bowler_analytics.parquet")
    df_batters.to_parquet(batters_path, index=False)
    df_bowlers.to_parquet(bowlers_path, index=False)
    
    print(f"   -> Saved {len(df_batters)} batters to {batters_path}")
    print(f"   -> Saved {len(df_bowlers)} bowlers to {bowlers_path}")
    print("=== PLAYER ANALYTICS ENGINE COMPLETED ===")

if __name__ == "__main__":
    compute_player_analytics()
