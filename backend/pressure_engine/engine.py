"""
Professional T20 Pressure Engine — Final Primary Methodology (Context-Only).
Eliminates dependence on unreliable reconstructed scoreboard fields and multi-run extras drift.
Formula:
  Pressure_context = (0.45 * Resource_Scarcity + 0.35 * Match_Urgency + 0.20 * Wicket_Scarcity) * 100 * M_knockout
Threshold:
  is_high_pressure = pressure_score >= 60.0
"""

import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
AUDIT_DIR = os.path.join(WORKSPACE, "artifacts", "audit")

con = duckdb.connect()

def build_pressure_features():
    print("=== STARTING CONTEXT-ONLY PRESSURE ENGINE COMPUTATION ===")
    
    bbb_path = os.path.join(PROCESSED_DIR, "ball_by_ball.parquet")
    matches_path = os.path.join(PROCESSED_DIR, "matches.parquet")
    
    # 1. Compute cumulative delivery state strictly from legal balls and wickets
    print("1. Computing delivery states from match schedule, legal balls, and wickets...")
    con.execute(f"""
        CREATE OR REPLACE TABLE delivery_states AS
        SELECT 
            b.*,
            m.comp_id,
            m.comp_name,
            m.match_format,
            m.season,
            m.competition_tier,
            m.is_primary_competition,
            m.match_status,
            m.revised_target,
            m.first_inn_revised_overs,
            m.second_inn_revised_overs,
            m.knock_out,
            -- Cumulative runs in innings BEFORE this delivery (retained for secondary sensitivity)
            COALESCE(SUM(b.total_delivery_runs) OVER (
                PARTITION BY b.match_id, b.innings 
                ORDER BY b.overid, b.over_ball_num, b.innings_ball_num 
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ), 0) as score_before_delivery,
            -- Cumulative wickets in innings BEFORE this delivery (100% exact from ball log)
            COALESCE(SUM(CASE WHEN b.is_wicket THEN 1 ELSE 0 END) OVER (
                PARTITION BY b.match_id, b.innings 
                ORDER BY b.overid, b.over_ball_num, b.innings_ball_num 
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ), 0) as wickets_lost_before_delivery,
            -- Cumulative legal balls in innings BEFORE this delivery (100% exact from ball log)
            COALESCE(SUM(CASE WHEN b.is_legal_ball THEN 1 ELSE 0 END) OVER (
                PARTITION BY b.match_id, b.innings 
                ORDER BY b.overid, b.over_ball_num, b.innings_ball_num 
                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
            ), 0) as legal_balls_bowled_before_delivery
        FROM '{bbb_path}' b
        JOIN '{matches_path}' m USING (match_id)
    """)

    # 2. Extract first innings total to establish target for innings 2 (for secondary score-aware comparison)
    print("2. Computing first innings totals for target resolution...")
    con.execute("""
        CREATE OR REPLACE TABLE first_inn_totals AS
        SELECT 
            match_id,
            SUM(total_delivery_runs) as inn1_total_runs,
            SUM(CASE WHEN is_legal_ball THEN 1 ELSE 0 END) as inn1_legal_balls
        FROM delivery_states
        WHERE innings = 1
        GROUP BY match_id
    """)

    # 3. Compute scoreboard-aware features and mathematical pressure
    print("3. Deriving context-based structural pressure components...")
    df_pressure = con.execute("""
        WITH enriched_deliveries AS (
            SELECT 
                d.*,
                f.inn1_total_runs,
                CASE 
                    WHEN d.innings = 2 AND d.revised_target IS NOT NULL THEN d.revised_target
                    WHEN d.innings = 2 AND f.inn1_total_runs IS NOT NULL THEN f.inn1_total_runs + 1
                    ELSE NULL
                END as target_runs,
                -- Total legal balls scheduled (accounting for revised overs if any)
                CASE 
                    WHEN d.innings = 1 AND d.first_inn_revised_overs IS NOT NULL THEN d.first_inn_revised_overs
                    WHEN d.innings = 2 AND d.second_inn_revised_overs IS NOT NULL THEN d.second_inn_revised_overs
                    ELSE 120
                END as total_scheduled_legal_balls
            FROM delivery_states d
            LEFT JOIN first_inn_totals f USING (match_id)
        ),
        derived_metrics AS (
            SELECT 
                *,
                GREATEST(0, total_scheduled_legal_balls - legal_balls_bowled_before_delivery) as balls_remaining,
                GREATEST(0, 10 - wickets_lost_before_delivery) as wickets_in_hand,
                CASE 
                    WHEN target_runs IS NOT NULL THEN GREATEST(0, target_runs - score_before_delivery)
                    ELSE NULL
                END as runs_required,
                -- Current Run Rate
                CASE 
                    WHEN legal_balls_bowled_before_delivery > 0 
                    THEN (score_before_delivery * 6.0) / legal_balls_bowled_before_delivery
                    ELSE 0.0
                END as current_run_rate,
                -- Required Run Rate (retained for secondary sensitivity)
                CASE 
                    WHEN innings = 2 AND target_runs IS NOT NULL AND (total_scheduled_legal_balls - legal_balls_bowled_before_delivery) > 0
                    THEN (GREATEST(0, target_runs - score_before_delivery) * 6.0) / (total_scheduled_legal_balls - legal_balls_bowled_before_delivery)
                    WHEN innings = 2 AND target_runs IS NOT NULL AND (total_scheduled_legal_balls - legal_balls_bowled_before_delivery) <= 0
                    THEN 36.0
                    ELSE NULL
                END as required_run_rate
            FROM enriched_deliveries
        )
        SELECT 
            *,
            -- Scoreboard validity flag
            CASE 
                WHEN innings = 2 AND target_runs IS NOT NULL THEN 'VERIFIED_SCOREBOARD'
                WHEN innings = 1 THEN 'VERIFIED_FIRST_INNINGS'
                ELSE 'CONTEXT_ONLY'
            END as score_confidence,
            
            -- Resource Scarcity Factor (0 to 1): decreases as wickets in hand and balls decrease
            (1.0 - (wickets_in_hand / 10.0) * (balls_remaining / 120.0)) as resource_scarcity,
            
            -- Match Urgency Factor (0 to 1): higher in death overs and late chase
            (1.0 - (balls_remaining / 120.0)) as match_urgency,
            
            -- Wicket Scarcity Factor (0 to 1): non-linear exponential increase as wickets drop
            POWER((10.0 - wickets_in_hand) / 10.0, 1.5) as wicket_scarcity,
            
            -- Scoring Demand Factor (0 to 1, retained for secondary score-aware comparison)
            CASE 
                WHEN innings = 2 AND required_run_rate IS NOT NULL THEN
                    LEAST(1.0, GREATEST(0.0, (required_run_rate - 5.0) / 15.0))
                WHEN innings = 1 THEN
                    LEAST(1.0, GREATEST(0.0, ((165.0 * (120 - balls_remaining) / 120.0) - score_before_delivery + 20.0) / 50.0))
                ELSE 0.5
            END as scoring_demand,
            
            -- Knockout match weight multiplier
            CASE WHEN knock_out = 1 THEN 1.15 ELSE 1.0 END as knockout_multiplier
        FROM derived_metrics
    """).fetchdf()

    print("4. Calculating Final Primary Context-Only Pressure Scores...")
    # Vectorized computation
    r_scarcity = df_pressure['resource_scarcity'].clip(0, 1)
    m_urgency = df_pressure['match_urgency'].clip(0, 1)
    w_scarcity = df_pressure['wicket_scarcity'].clip(0, 1)
    w_hand = df_pressure['wickets_in_hand'].clip(0, 10)
    ko_mult = df_pressure['knockout_multiplier']

    # PRIMARY BATTING PRESSURE (Context-Only):
    # Pressure_context = (0.45 * Resource_Scarcity + 0.35 * Match_Urgency + 0.20 * Wicket_Scarcity) * 100 * M_knockout
    raw_batting_context = (
        0.45 * r_scarcity + 
        0.35 * m_urgency + 
        0.20 * w_scarcity
    ) * 100.0 * ko_mult

    # PRIMARY BOWLING PRESSURE (Context-Only Leverage):
    # Bowling leverage peaks in high-urgency death overs against batting sides with wickets in hand,
    # without depending on scoreboard run totals.
    # Leverage = (wickets_in_hand / 10.0) * Match_Urgency
    bowler_leverage = (w_hand / 10.0) * m_urgency
    raw_bowling_context = (
        0.40 * bowler_leverage + 
        0.35 * m_urgency + 
        0.25 * r_scarcity
    ) * 100.0 * ko_mult

    # Store Primary Context-Only Scores
    df_pressure['batting_pressure_score'] = raw_batting_context.clip(0, 100).round(2)
    df_pressure['bowling_pressure_score'] = raw_bowling_context.clip(0, 100).round(2)
    
    # High-pressure thresholds (documented threshold = 60.0)
    df_pressure['is_high_batting_pressure'] = df_pressure['batting_pressure_score'] >= 60.0
    df_pressure['is_high_bowling_pressure'] = df_pressure['bowling_pressure_score'] >= 60.0

    # Also compute and store secondary score-aware scores for sensitivity reporting
    p_scoring = df_pressure['scoring_demand'].clip(0, 1)
    raw_bat_score_aware = (0.35 * p_scoring + 0.30 * r_scarcity + 0.20 * m_urgency + 0.15 * w_scarcity) * 100.0 * ko_mult
    df_pressure['secondary_score_aware_batting_pressure'] = raw_bat_score_aware.clip(0, 100).round(2)
    
    output_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    df_pressure.to_parquet(output_path, index=False)
    print(f"   -> Successfully saved {len(df_pressure)} deliveries with context-only pressure scores to {output_path}")

    # Pressure distribution metrics
    n_primary = (df_pressure['is_primary_competition'] == True).sum()
    n_bat_hp = ((df_pressure['is_primary_competition'] == True) & (df_pressure['is_high_batting_pressure'] == True)).sum()
    n_bowl_hp = ((df_pressure['is_primary_competition'] == True) & (df_pressure['is_high_bowling_pressure'] == True)).sum()
    print(f"   Primary deliveries: {n_primary}")
    print(f"   High batting pressure deliveries: {n_bat_hp} ({n_bat_hp/n_primary*100:.2f}%)")
    print(f"   High bowling pressure deliveries: {n_bowl_hp} ({n_bowl_hp/n_primary*100:.2f}%)")

if __name__ == "__main__":
    build_pressure_features()
