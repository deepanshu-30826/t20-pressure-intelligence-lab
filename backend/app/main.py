"""
FastAPI Application for T20 Pressure Intelligence Lab.
Local, secure, high-performance API serving real analytical data.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import duckdb
import pandas as pd
import os
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/app
BACKEND_DIR = os.path.dirname(CURRENT_DIR)                # backend
REPO_DIR = os.path.dirname(BACKEND_DIR)                   # repo root

if os.path.exists(os.path.join(BACKEND_DIR, "data", "processed")):
    PROCESSED_DIR = os.path.join(BACKEND_DIR, "data", "processed").replace("\\", "/")
else:
    PROCESSED_DIR = os.path.join(REPO_DIR, "data", "processed").replace("\\", "/")

if os.path.exists(os.path.join(BACKEND_DIR, "artifacts")):
    ARTIFACTS_DIR = os.path.join(BACKEND_DIR, "artifacts").replace("\\", "/")
else:
    ARTIFACTS_DIR = os.path.join(REPO_DIR, "artifacts").replace("\\", "/")

app = FastAPI(title="T20 Pressure Intelligence Lab API", version="1.0.0")

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
origins = ["*"] if allowed_origins_env == "*" else [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

con = duckdb.connect()

def query_df(q: str):
    cur = con.cursor()
    try:
        return cur.execute(q).fetchdf()
    finally:
        cur.close()

def query_one(q: str):
    cur = con.cursor()
    try:
        return cur.execute(q).fetchone()
    finally:
        cur.close()

@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "T20 Pressure Intelligence Lab"}

@app.get("/api/overview")
def get_overview():
    matches_p = os.path.join(PROCESSED_DIR, "matches.parquet")
    bbb_p = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    b_p = os.path.join(PROCESSED_DIR, "ranked_batters.parquet")
    bw_p = os.path.join(PROCESSED_DIR, "ranked_bowlers.parquet")
    
    total_matches = query_one(f"SELECT count(*) FROM '{matches_p}'")[0]
    total_deliveries = query_one(f"SELECT count(*) FROM '{bbb_p}'")[0]
    total_pressure_delivs = query_one(f"SELECT count(*) FROM '{bbb_p}' WHERE is_high_batting_pressure OR is_high_bowling_pressure")[0]
    
    ipl_matches = query_one(f"SELECT count(*) FROM '{matches_p}' WHERE competition_tier = 'IPL'")[0]
    t20i_matches = query_one(f"SELECT count(*) FROM '{matches_p}' WHERE competition_tier = 'T20I'")[0]
    
    top_b = query_df(f"SELECT player_id, player_name, composite_pressure_rating, pressure_strike_rate FROM '{b_p}' ORDER BY rank LIMIT 1").to_dict(orient='records')[0]
    top_bw = query_df(f"SELECT player_id, player_name, composite_pressure_rating, pressure_economy FROM '{bw_p}' ORDER BY rank LIMIT 1").to_dict(orient='records')[0]
    
    # Pressure distribution summary
    with open(os.path.join(ARTIFACTS_DIR, "audit", "pressure_distribution.json")) as f:
        p_dist = json.load(f)
        
    return {
        "total_matches": total_matches,
        "total_deliveries": total_deliveries,
        "pressure_deliveries": total_pressure_delivs,
        "ipl_matches": ipl_matches,
        "t20i_matches": t20i_matches,
        "top_batter": top_b,
        "top_bowler": top_bw,
        "pressure_distribution": p_dist
    }

@app.get("/api/data-audit")
def get_data_audit():
    audit_file = os.path.join(ARTIFACTS_DIR, "audit", "data_audit_summary.json")
    if os.path.exists(audit_file):
        with open(audit_file) as f:
            return json.load(f)
    return {}

@app.get("/api/rankings/batters")
def get_batter_rankings(limit: int = 200, confidence: str = None):
    b_p = os.path.join(PROCESSED_DIR, "ranked_batters.parquet")
    query = f"SELECT * FROM '{b_p}'"
    if confidence and confidence.upper() != 'ALL':
        query += f" WHERE confidence_level = '{confidence.upper()}'"
    query += f" ORDER BY rank LIMIT {limit}"
    df = query_df(query)
    return df.to_dict(orient='records')

@app.get("/api/rankings/bowlers")
def get_bowler_rankings(limit: int = 200, confidence: str = None):
    bw_p = os.path.join(PROCESSED_DIR, "ranked_bowlers.parquet")
    query = f"SELECT * FROM '{bw_p}'"
    if confidence and confidence.upper() != 'ALL':
        query += f" WHERE confidence_level = '{confidence.upper()}'"
    query += f" ORDER BY rank LIMIT {limit}"
    df = query_df(query)
    return df.to_dict(orient='records')

@app.get("/api/players/{player_id}")
def get_player_profile(player_id: int):
    b_p = os.path.join(PROCESSED_DIR, "ranked_batters.parquet")
    bw_p = os.path.join(PROCESSED_DIR, "ranked_bowlers.parquet")
    bbb_p = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    
    b_profile = query_df(f"SELECT * FROM '{b_p}' WHERE player_id = {player_id}")
    bw_profile = query_df(f"SELECT * FROM '{bw_p}' WHERE player_id = {player_id}")
    
    if len(b_profile) == 0 and len(bw_profile) == 0:
        # Check canonical player table
        pl_p = os.path.join(PROCESSED_DIR, "players.parquet")
        pl = query_df(f"SELECT * FROM '{pl_p}' WHERE player_id = {player_id}")
        if len(pl) == 0:
            raise HTTPException(status_code=404, detail="Player not found")
        return {"player": pl.iloc[0].to_dict(), "batting": None, "bowling": None}
        
    # Phase breakdowns
    phase_bat = query_df(f"""
        SELECT 
            innings_phase,
            count(*) as balls,
            sum(batter_runs) as runs,
            sum(CASE WHEN is_high_batting_pressure THEN 1 ELSE 0 END) as pressure_balls,
            sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as pressure_runs
        FROM '{bbb_p}'
        WHERE striker_id = {player_id} AND is_batter_ball = 1
        GROUP BY innings_phase
    """)
    
    return {
        "player_id": player_id,
        "name": b_profile.iloc[0]['player_name'] if len(b_profile) > 0 else bw_profile.iloc[0]['player_name'],
        "batting_profile": b_profile.iloc[0].to_dict() if len(b_profile) > 0 else None,
        "bowling_profile": bw_profile.iloc[0].to_dict() if len(bw_profile) > 0 else None,
        "batting_phase_split": phase_bat.to_dict(orient='records')
    }

@app.get("/api/players/{player_id}/match-history")
def get_player_matches(player_id: int, limit: int = 15):
    bbb_p = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    df = query_df(f"""
        SELECT 
            match_id,
            comp_name,
            season,
            delivery_ist_time::DATE as match_date,
            sum(is_batter_ball) as balls_faced,
            sum(batter_runs) as runs,
            sum(CASE WHEN is_high_batting_pressure THEN is_batter_ball ELSE 0 END) as pressure_balls,
            sum(CASE WHEN is_high_batting_pressure THEN batter_runs ELSE 0 END) as pressure_runs
        FROM '{bbb_p}'
        WHERE striker_id = {player_id}
        GROUP BY match_id, comp_name, season, match_date
        ORDER BY match_date DESC
        LIMIT {limit}
    """)
    return df.to_dict(orient='records')

@app.get("/api/matches/{match_id}")
def get_match_details(match_id: int):
    matches_p = os.path.join(PROCESSED_DIR, "matches.parquet")
    bbb_p = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    
    match_row = query_df(f"SELECT * FROM '{matches_p}' WHERE match_id = {match_id}")
    if len(match_row) == 0:
        raise HTTPException(status_code=404, detail="Match not found")
        
    timeline = query_df(f"""
        SELECT 
            innings,
            overid,
            over_ball_num,
            striker_name,
            bowler_name,
            batter_runs,
            total_delivery_runs,
            is_wicket,
            dismissal_type,
            batting_pressure_score,
            bowling_pressure_score,
            score_before_delivery,
            wickets_lost_before_delivery
        FROM '{bbb_p}'
        WHERE match_id = {match_id}
        ORDER BY innings, overid, over_ball_num
    """)
    
    return {
        "match": match_row.iloc[0].to_dict(),
        "deliveries": timeline.to_dict(orient='records')
    }

@app.get("/api/model/validation")
def get_validation_report():
    val_file = os.path.join(ARTIFACTS_DIR, "validation", "validation_report.json")
    if os.path.exists(val_file):
        with open(val_file) as f:
            return json.load(f)
    return {}
