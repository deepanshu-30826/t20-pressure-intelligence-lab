"""
Data Pipeline Module for T20 Pressure Intelligence Lab.
Ingests, cleans, validates, and stores clean Parquet files.
"""

import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = WORKSPACE  # CSV files are in WORKSPACE
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
AUDIT_DIR = os.path.join(WORKSPACE, "artifacts", "audit")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(AUDIT_DIR, exist_ok=True)

con = duckdb.connect()

def run_pipeline():
    print("=== STARTING T20 DATA PIPELINE ===")
    
    # 1. Competitions & Format Classification
    print("1. Processing competitions...")
    df_comps = con.execute(f"""
        SELECT 
            comp_id,
            comp_name,
            match_format,
            season,
            CASE 
                WHEN comp_name ILIKE '%IPL%' THEN 'IPL'
                WHEN match_format = 'T20I' THEN 'T20I'
                WHEN comp_name ILIKE '%Emerging%' OR comp_name ILIKE '%Rising Stars%' THEN 'T20_DEVELOPMENT'
                ELSE 'OTHER_T20'
            END as competition_tier,
            CASE
                WHEN comp_name ILIKE '%IPL%' OR match_format = 'T20I' THEN TRUE
                ELSE FALSE
            END as is_primary_competition
        FROM '{os.path.join(RAW_DIR, 'competitions.csv')}'
    """).fetchdf()
    
    comps_path = os.path.join(PROCESSED_DIR, "competitions.parquet")
    df_comps.to_parquet(comps_path, index=False)
    print(f"   -> Saved {len(df_comps)} competitions to {comps_path}")

    # 2. Canonical Player Dimension
    print("2. Constructing canonical player dimension...")
    df_players = con.execute(f"""
        WITH all_players AS (
            SELECT DISTINCT player_id, player_name FROM '{os.path.join(RAW_DIR, 'competition_team_player_mapping.csv')}'
            UNION
            SELECT DISTINCT striker_id as player_id, striker_name as player_name FROM '{os.path.join(RAW_DIR, 'ball_by_ball.csv')}'
            UNION
            SELECT DISTINCT non_striker_id as player_id, non_striker_name as player_name FROM '{os.path.join(RAW_DIR, 'ball_by_ball.csv')}'
            UNION
            SELECT DISTINCT bowler_id as player_id, bowler_name as player_name FROM '{os.path.join(RAW_DIR, 'ball_by_ball.csv')}'
        )
        SELECT player_id, any_value(player_name) as player_name
        FROM all_players
        GROUP BY player_id
        ORDER BY player_id
    """).fetchdf()
    
    players_path = os.path.join(PROCESSED_DIR, "players.parquet")
    df_players.to_parquet(players_path, index=False)
    print(f"   -> Saved {len(df_players)} canonical players to {players_path}")

    # 3. Matches
    print("3. Processing matches...")
    df_matches = con.execute(f"""
        SELECT 
            m.match_id,
            m.comp_id,
            c.comp_name,
            c.match_format,
            c.season,
            c.competition_tier,
            c.is_primary_competition,
            m.match_number,
            m.match_date,
            m.stage,
            m.venue_id,
            m.venue_country,
            m.home_team_id,
            m.home_team,
            m.away_team_id,
            m.away_team,
            m.toss_win_team_id,
            m.toss_opted,
            m.man_of_the_match,
            m.first_inn_revised_overs,
            m.second_inn_revised_overs,
            m.revised_target,
            m.knock_out,
            m.win_team_id,
            m.result,
            CASE 
                WHEN m.result ILIKE '%abandoned%' OR m.result ILIKE '%no result%' THEN 'ABANDONED_OR_NO_RESULT'
                WHEN m.first_inn_revised_overs IS NOT NULL OR m.second_inn_revised_overs IS NOT NULL OR m.revised_target IS NOT NULL THEN 'SHORTENED_REVISED'
                WHEN m.result ILIKE '%super over%' OR m.result ILIKE '%tied%' THEN 'TIED_OR_SUPER_OVER'
                ELSE 'NORMAL'
            END as match_status
        FROM '{os.path.join(RAW_DIR, 'matches.csv')}' m
        JOIN '{comps_path}' c USING (comp_id)
    """).fetchdf()
    
    matches_path = os.path.join(PROCESSED_DIR, "matches.parquet")
    df_matches.to_parquet(matches_path, index=False)
    print(f"   -> Saved {len(df_matches)} matches to {matches_path}")

    # 4. Ball by Ball with Validated Cricket Delivery Semantics
    print("4. Processing ball_by_ball with verified cricket rules...")
    # Interpretation:
    # is_legal_ball: True for bowler legal delivery (wides and no-balls are not legal)
    # is_batter_ball: True for ball faced by batter (wides and penalties do not count, no-balls DO count)
    # bowler_wicket: True for Caught, Bowled, LBW, Stump, Hit Wicket. False for RunOut, Retire Out, Obstructing.
    df_bbb = con.execute(f"""
        SELECT 
            b.match_id,
            b.innings,
            b.overid,
            b.over_ball_num,
            b.innings_ball_num,
            b.batting_team_id,
            b.bowling_team_id,
            b.striker_id,
            b.striker_name,
            b.non_striker_id,
            b.non_striker_name,
            b.bowler_id,
            b.bowler_name,
            b.batting_type,
            b.bowling_type,
            b.batting_order,
            b.runs as batter_runs,
            b.is_four,
            b.is_six,
            b.is_wicket,
            b.dismissal_type_id,
            b.dismissal_type,
            b.dismissed_player_id,
            b.extras_type,
            b.extras_2_runs,
            b.pace_or_spin,
            b.bowl_speed,
            b.stroke,
            b.delivery_style,
            b.over_or_around,
            b.on_or_off,
            b.delivery_ist_time,
            -- Bowler wicket credit flag
            CASE 
                WHEN b.is_wicket AND b.dismissal_type_id IN (1, 2, 3, 5, 6) THEN TRUE
                ELSE FALSE
            END as is_bowler_wicket,
            -- Legal delivery for bowler
            CASE 
                WHEN b.extras_type IN ('wide', 'Overstep', 'other', 'Penalty') THEN FALSE
                ELSE TRUE
            END as is_legal_ball,
            -- Ball faced by batter
            CASE 
                WHEN b.extras_type IN ('wide', 'Penalty') THEN FALSE
                ELSE TRUE
            END as is_batter_ball,
            -- Extras assigned to bowling runs
            CASE 
                WHEN b.extras_type = 'wide' THEN 1 + b.extras_2_runs
                WHEN b.extras_type IN ('Overstep', 'other') THEN 1 + b.extras_2_runs
                ELSE 0
            END as bowler_extras,
            -- Total runs conceded by bowler (batter runs + bowler extras)
            b.runs + CASE 
                WHEN b.extras_type = 'wide' THEN 1 + b.extras_2_runs
                WHEN b.extras_type IN ('Overstep', 'other') THEN 1 + b.extras_2_runs
                ELSE 0
            END as bowler_runs_conceded,
            -- Team extras
            CASE 
                WHEN b.extras_type = 'wide' THEN 1 + b.extras_2_runs
                WHEN b.extras_type IN ('Overstep', 'other') THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'byes' THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'legbyes' THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'Penalty' THEN 5
                ELSE 0
            END as total_delivery_extras,
            -- Total delivery score added to innings total
            b.runs + CASE 
                WHEN b.extras_type = 'wide' THEN 1 + b.extras_2_runs
                WHEN b.extras_type IN ('Overstep', 'other') THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'byes' THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'legbyes' THEN 1 + b.extras_2_runs
                WHEN b.extras_type = 'Penalty' THEN 5
                ELSE 0
            END as total_delivery_runs,
            -- Innings phase
            CASE 
                WHEN b.overid <= 6 THEN 'POWERPLAY'
                WHEN b.overid <= 15 THEN 'MIDDLE'
                ELSE 'DEATH'
            END as innings_phase
        FROM '{os.path.join(RAW_DIR, 'ball_by_ball.csv')}' b
    """).fetchdf()

    bbb_path = os.path.join(PROCESSED_DIR, "ball_by_ball.parquet")
    df_bbb.to_parquet(bbb_path, index=False)
    print(f"   -> Saved {len(df_bbb)} ball-by-ball records to {bbb_path}")

    # 5. Data Audit Report Generation
    print("5. Generating data audit report...")
    audit = {
        "raw_counts": {
            "ball_by_ball": len(df_bbb),
            "matches": len(df_matches),
            "competitions": len(df_comps),
            "players": len(df_players)
        },
        "primary_competitions": {
            "IPL": int(df_matches[df_matches['competition_tier'] == 'IPL']['match_id'].nunique()),
            "T20I": int(df_matches[df_matches['competition_tier'] == 'T20I']['match_id'].nunique()),
            "T20_DEVELOPMENT": int(df_matches[df_matches['competition_tier'] == 'T20_DEVELOPMENT']['match_id'].nunique())
        },
        "legal_balls_summary": {
            "total_deliveries": len(df_bbb),
            "legal_bowler_deliveries": int(df_bbb['is_legal_ball'].sum()),
            "batter_balls_faced": int(df_bbb['is_batter_ball'].sum()),
            "wides": int((df_bbb['extras_type'] == 'wide').sum()),
            "oversteps": int((df_bbb['extras_type'] == 'Overstep').sum()),
            "other_noballs": int((df_bbb['extras_type'] == 'other').sum()),
            "byes": int((df_bbb['extras_type'] == 'byes').sum()),
            "legbyes": int((df_bbb['extras_type'] == 'legbyes').sum())
        },
        "wickets_summary": {
            "total_wickets": int(df_bbb['is_wicket'].sum()),
            "bowler_credited_wickets": int(df_bbb['is_bowler_wicket'].sum()),
            "run_outs": int((df_bbb['dismissal_type'] == 'RunOut').sum()),
            "other_dismissals": int(df_bbb['is_wicket'].sum() - df_bbb['is_bowler_wicket'].sum() - (df_bbb['dismissal_type'] == 'RunOut').sum())
        }
    }
    
    with open(os.path.join(AUDIT_DIR, "data_audit_summary.json"), "w") as f:
        json.dump(audit, f, indent=2)
    print("=== DATA PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_pipeline()
