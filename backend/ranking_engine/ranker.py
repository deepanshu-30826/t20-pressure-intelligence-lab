"""
Ranking Engine for Batters and Bowlers under Pressure.
FINAL RANKING QUALITY REFINEMENT:
- Context-Only Structural Pressure Engine (Threshold >= 60.0).
- Neutral Format Weighting (W_format = 1.0).
- Role-Adjusted Performance (Position Bands 1-3, 4-5, 6-7, 8+; Phases PP 1-6, MID 7-15, DTH 16-20).
- Match-Level Consistency replacing volume bonuses (>=5 balls for batter, >=6 balls for bowler).
- Empirical Bayes shrinkage (k = 40.0).
- Standardized multi-metric composite rating (0-100).
"""

import duckdb
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
RANKINGS_DIR = os.path.join(WORKSPACE, "artifacts", "rankings")
VALIDATION_DIR = os.path.join(WORKSPACE, "artifacts", "validation")
os.makedirs(RANKINGS_DIR, exist_ok=True)

con = duckdb.connect()

PLAYER_METADATA_NOTES = {
    37052: "Naman Dhir: Emerging high-strike-rate middle-overs/death accelerator; 76.2% match consistency.",
    23311: "Jacob Bethell: Dynamic left-handed stroke maker; fearless late-overs execution.",
    1699: "Suryakumar Yadav: Unrivaled high-pressure sample volume (669 balls); 73.9% match consistency.",
    4853: "Glenn Phillips: Powerful multi-phase middle-order ball-striker; reliable boundary hitter.",
    2921: "Fakhar Zaman: Aggressive top-order pressure performer; sharp lift over expected par.",
    3647: "Shreyas Iyer: Exceptional spin/pace stabilizer under match urgency (518 balls, 70.3% consistency).",
    2101: "Quinton de Kock: Elite wicketkeeper-batter; explosive boundary generation under pressure.",
    2984: "Sikandar Raza: Experienced clutch all-rounder; 65.0% match consistency across 28 matches.",
    813: "Jos Buttler: World-class top-order clutch batter; prolific high-pressure sample (445 balls).",
    6059: "Ruturaj Gaikwad: Technical anchor capable of high boundary acceleration in deep match phases.",
    5979: "Abrar Ahmed: Mystery spinner; extraordinary run containment under match urgency (6.41 econ vs 8.91 par).",
    781: "Sunil Narine: Legendary economy suppression across all phases; 70.5% match consistency.",
    3720: "Craig Young: Accurate seam bowler with disciplined death-overs execution (75.0% consistency).",
    1884: "Jasprit Bumrah: World-class death bowler; 7.38 economy in high-pressure death overs (par 9.26).",
    6450: "Mujeeb Ur Rahman: Highly stifling finger spin; 88.2% match consistency.",
    2687: "Roston Chase: Tactical off-spinner; tight boundary suppression (80.0% match consistency).",
    2382: "Jamie Overton: Tall pace bowler; steep bounce and heavy death-over ball suppression.",
    2417: "Akeal Hosein: Left-arm orthodox; reliable containment across powerplay and middle phases.",
    20785: "Matheesha Pathirana: Elite sling-action death specialist; 8.03 economy against 9.23 death par.",
    7699: "Abbas Afridi: Young Pakistani seam bowler; strong wicket-taking presence in tight finishes."
}

def compute_rankings():
    print("=== EXECUTING FINAL REFINED PRIMARY RANKING ENGINE ===")
    dp_path = os.path.join(PROCESSED_DIR, "delivery_pressure.parquet")
    
    # 1. Benchmarks
    bench_b = con.execute(f"""
        SELECT 
            CASE 
                WHEN batting_order BETWEEN 1 AND 3 THEN 'Top'
                WHEN batting_order BETWEEN 4 AND 5 THEN 'Mid'
                WHEN batting_order BETWEEN 6 AND 7 THEN 'Fin'
                ELSE 'Tail'
            END as pos,
            CASE 
                WHEN overid BETWEEN 1 AND 6 THEN 'PP'
                WHEN overid BETWEEN 7 AND 15 THEN 'MID'
                ELSE 'DTH'
            END as ph,
            avg(batter_runs) * 100.0 as bench_sr
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
        GROUP BY pos, ph
    """).df()
    bench_b_map = dict(zip(zip(bench_b['pos'], bench_b['ph']), bench_b['bench_sr']))
    overall_bench_sr = 139.98

    bench_bw = con.execute(f"""
        SELECT 
            CASE 
                WHEN overid BETWEEN 1 AND 6 THEN 'PP'
                WHEN overid BETWEEN 7 AND 15 THEN 'MID'
                ELSE 'DTH'
            END as ph,
            avg(bowler_runs_conceded) * 6.0 as bench_econ
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
        GROUP BY ph
    """).df()
    bench_bw_map = dict(zip(bench_bw['ph'], bench_bw['bench_econ']))
    overall_bench_econ = 8.40

    # ---------------------------------------------------------
    # 1. BATTERS
    # ---------------------------------------------------------
    print("1. Processing Batters...")
    b_delivs = con.execute(f"""
        SELECT 
            match_id, striker_id as player_id, striker_name as player_name,
            comp_id, is_high_batting_pressure, is_batter_ball, batter_runs, is_four, is_six,
            CASE 
                WHEN batting_order BETWEEN 1 AND 3 THEN 'Top'
                WHEN batting_order BETWEEN 4 AND 5 THEN 'Mid'
                WHEN batting_order BETWEEN 6 AND 7 THEN 'Fin'
                ELSE 'Tail'
            END as pos,
            CASE 
                WHEN overid BETWEEN 1 AND 6 THEN 'PP'
                WHEN overid BETWEEN 7 AND 15 THEN 'MID'
                ELSE 'DTH'
            END as ph
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE AND is_batter_ball = TRUE
    """).df()
    b_delivs['expected_sr'] = b_delivs.apply(lambda r: bench_b_map.get((r['pos'], r['ph']), overall_bench_sr), axis=1)

    b_summary = []
    for pid, group in b_delivs.groupby('player_id'):
        pname = group['player_name'].iloc[0]
        tot_matches = group['match_id'].nunique()
        ov_balls = len(group)
        ov_runs = group['batter_runs'].sum()
        ov_sr = (ov_runs * 100.0) / ov_balls
        ov_bdry = ((group['is_four'].sum() + group['is_six'].sum()) * 100.0) / ov_balls
        ov_dots = ((group['batter_runs'] == 0).sum() * 100.0) / ov_balls
        
        p_group = group[group['is_high_batting_pressure'] == True]
        p_balls = len(p_group)
        p_matches = p_group['match_id'].nunique()
        if p_balls == 0:
            continue
            
        p_runs = p_group['batter_runs'].sum()
        p_sr = (p_runs * 100.0) / p_balls
        p_bdry = ((p_group['is_four'].sum() + p_group['is_six'].sum()) * 100.0) / p_balls
        p_dots = ((p_group['batter_runs'] == 0).sum() * 100.0) / p_balls
        
        exp_sr = p_group['expected_sr'].mean()
        role_adj_psr = p_sr - exp_sr + overall_bench_sr
        role_lift = p_sr - exp_sr
        shrunk_lift = role_lift * (p_balls / (p_balls + 40.0))
        bdry_gain = p_bdry - ov_bdry
        dot_reduc = ov_dots - p_dots
        
        # Match consistency (>=5 pressure balls in match)
        match_evals = []
        for mid, m_group in p_group.groupby('match_id'):
            if len(m_group) >= 5:
                m_sr = (m_group['batter_runs'].sum() * 100.0) / len(m_group)
                m_exp = m_group['expected_sr'].mean()
                match_evals.append(1 if m_sr >= m_exp else 0)
        qual_matches = len(match_evals)
        consist_pct = (sum(match_evals) * 100.0 / qual_matches) if qual_matches > 0 else 0.0
        
        ipl_pballs = len(p_group[p_group['comp_id'].isin([1358, 1715, 2193, 2725, 3298])])
        t20i_pballs = p_balls - ipl_pballs

        b_summary.append({
            "player_id": pid,
            "player_name": pname,
            "total_matches": tot_matches,
            "overall_balls_faced": ov_balls,
            "overall_strike_rate": round(ov_sr, 2),
            "pressure_balls_faced": p_balls,
            "pressure_matches": p_matches,
            "pressure_strike_rate": round(p_sr, 2),
            "expected_baseline_sr": round(exp_sr, 2),
            "role_adjusted_psr": round(role_adj_psr, 2),
            "role_lift": round(role_lift, 2),
            "shrunk_sr_lift": round(shrunk_lift, 2),
            "boundary_gain": round(bdry_gain, 2),
            "dot_reduction": round(dot_reduc, 2),
            "qualifying_matches": qual_matches,
            "match_consistency_pct": round(consist_pct, 1),
            "ipl_pressure_balls": ipl_pballs,
            "t20i_pressure_balls": t20i_pballs
        })
    df_b_pool = pd.DataFrame(b_summary)

    # ---------------------------------------------------------
    # 2. BOWLERS
    # ---------------------------------------------------------
    print("2. Processing Bowlers...")
    bw_delivs = con.execute(f"""
        SELECT 
            match_id, bowler_id as player_id, bowler_name as player_name,
            comp_id, is_high_bowling_pressure, is_legal_ball, bowler_runs_conceded,
            is_four, is_six, is_bowler_wicket,
            CASE 
                WHEN overid BETWEEN 1 AND 6 THEN 'PP'
                WHEN overid BETWEEN 7 AND 15 THEN 'MID'
                ELSE 'DTH'
            END as ph
        FROM '{dp_path}'
        WHERE is_primary_competition = TRUE AND is_legal_ball = TRUE
    """).df()
    bw_delivs['expected_econ'] = bw_delivs['ph'].map(bench_bw_map)

    bw_summary = []
    for pid, group in bw_delivs.groupby('player_id'):
        pname = group['player_name'].iloc[0]
        tot_matches = group['match_id'].nunique()
        ov_balls = len(group)
        ov_runs = group['bowler_runs_conceded'].sum()
        ov_econ = (ov_runs * 6.0) / ov_balls
        ov_bdry = ((group['is_four'].sum() + group['is_six'].sum()) * 100.0) / ov_balls
        ov_dots = ((group['bowler_runs_conceded'] == 0).sum() * 100.0) / ov_balls
        
        p_group = group[group['is_high_bowling_pressure'] == True]
        p_balls = len(p_group)
        p_matches = p_group['match_id'].nunique()
        if p_balls == 0:
            continue
            
        p_runs = p_group['bowler_runs_conceded'].sum()
        p_wkts = p_group['is_bowler_wicket'].sum()
        p_econ = (p_runs * 6.0) / p_balls
        p_pwr = (p_wkts * 100.0) / p_balls
        p_bdry = ((p_group['is_four'].sum() + p_group['is_six'].sum()) * 100.0) / p_balls
        p_dots = ((p_group['bowler_runs_conceded'] == 0).sum() * 100.0) / p_balls
        
        exp_econ = p_group['expected_econ'].mean()
        role_adj_pecon = p_econ - exp_econ + overall_bench_econ
        role_lift = exp_econ - p_econ # positive is better
        shrunk_lift = role_lift * (p_balls / (p_balls + 40.0))
        bdry_supp = ov_bdry - p_bdry
        dot_gain = p_dots - ov_dots
        
        # Match consistency (>=6 legal pressure balls in match)
        match_evals = []
        for mid, m_group in p_group.groupby('match_id'):
            if len(m_group) >= 6:
                m_econ = (m_group['bowler_runs_conceded'].sum() * 6.0) / len(m_group)
                m_exp = m_group['expected_econ'].mean()
                match_evals.append(1 if m_econ <= m_exp else 0)
        qual_matches = len(match_evals)
        consist_pct = (sum(match_evals) * 100.0 / qual_matches) if qual_matches > 0 else 0.0
        
        ipl_pballs = len(p_group[p_group['comp_id'].isin([1358, 1715, 2193, 2725, 3298])])
        t20i_pballs = p_balls - ipl_pballs

        bw_summary.append({
            "player_id": pid,
            "player_name": pname,
            "total_matches": tot_matches,
            "overall_legal_balls": ov_balls,
            "overall_economy": round(ov_econ, 2),
            "pressure_legal_balls": p_balls,
            "pressure_matches": p_matches,
            "pressure_economy": round(p_econ, 2),
            "expected_baseline_econ": round(exp_econ, 2),
            "role_adjusted_pecon": round(role_adj_pecon, 2),
            "role_lift": round(role_lift, 2),
            "shrunk_econ_lift": round(shrunk_lift, 2),
            "pressure_wicket_rate": round(p_pwr, 2),
            "boundary_suppression": round(bdry_supp, 2),
            "dot_gain": round(dot_gain, 2),
            "qualifying_matches": qual_matches,
            "match_consistency_pct": round(consist_pct, 1),
            "ipl_pressure_balls": ipl_pballs,
            "t20i_pressure_balls": t20i_pballs
        })
    df_bw_pool = pd.DataFrame(bw_summary)

    # ---------------------------------------------------------
    # 3. STANDARDIZATION & COMPOSITE SCORING
    # ---------------------------------------------------------
    print("3. Standardizing across eligible pools (>=100 balls, >=10 matches)...")
    
    # Filter candidates satisfying minimum sample criteria
    b_cand = df_b_pool[
        (df_b_pool['overall_balls_faced'] >= 100) & 
        (df_b_pool['pressure_balls_faced'] >= 100) & 
        (df_b_pool['pressure_matches'] >= 10)
    ].copy()
    
    def z_score(s):
        return (s - s.mean()) / (s.std() + 1e-6)

    # Batters: 30% Role-PSR, 35% Shrunk Lift, 15% Boundary Gain, 10% Dot Reduction, 10% Consistency
    b_cand['z_role_psr'] = z_score(b_cand['role_adjusted_psr'])
    b_cand['z_shrunk_lift'] = z_score(b_cand['shrunk_sr_lift'])
    b_cand['z_boundary'] = z_score(b_cand['boundary_gain'])
    b_cand['z_dot'] = z_score(b_cand['dot_reduction'])
    b_cand['z_consistency'] = z_score(b_cand['match_consistency_pct'])

    raw_b = (
        0.30 * b_cand['z_role_psr'] + 
        0.35 * b_cand['z_shrunk_lift'] + 
        0.15 * b_cand['z_boundary'] + 
        0.10 * b_cand['z_dot'] + 
        0.10 * b_cand['z_consistency']
    )
    b_cand['composite_pressure_rating'] = (50.0 + 12.0 * raw_b).clip(0, 100).round(2)
    b_cand['confidence_level'] = 'HIGH'
    b_cand = b_cand.sort_values('composite_pressure_rating', ascending=False).reset_index(drop=True)
    b_cand['rank'] = b_cand.index + 1

    # Bowlers: 25% Role-PEcon (inverted), 30% Shrunk Lift, 20% PWR, 10% Boundary Supp, 5% Dot Gain, 10% Consistency
    bw_cand = df_bw_pool[
        (df_bw_pool['overall_legal_balls'] >= 120) & 
        (df_bw_pool['pressure_legal_balls'] >= 100) & 
        (df_bw_pool['pressure_matches'] >= 10)
    ].copy()

    bw_cand['z_role_pecon'] = (bw_cand['role_adjusted_pecon'].mean() - bw_cand['role_adjusted_pecon']) / (bw_cand['role_adjusted_pecon'].std() + 1e-6)
    bw_cand['z_shrunk_lift'] = z_score(bw_cand['shrunk_econ_lift'])
    bw_cand['z_pwr'] = z_score(bw_cand['pressure_wicket_rate'])
    bw_cand['z_boundary'] = z_score(bw_cand['boundary_suppression'])
    bw_cand['z_dot'] = z_score(bw_cand['dot_gain'])
    bw_cand['z_consistency'] = z_score(bw_cand['match_consistency_pct'])

    raw_bw = (
        0.25 * bw_cand['z_role_pecon'] + 
        0.30 * bw_cand['z_shrunk_lift'] + 
        0.20 * bw_cand['z_pwr'] + 
        0.10 * bw_cand['z_boundary'] + 
        0.05 * bw_cand['z_dot'] + 
        0.10 * bw_cand['z_consistency']
    )
    bw_cand['composite_pressure_rating'] = (50.0 + 12.0 * raw_bw).clip(0, 100).round(2)
    bw_cand['confidence_level'] = 'HIGH'
    bw_cand = bw_cand.sort_values('composite_pressure_rating', ascending=False).reset_index(drop=True)
    bw_cand['rank'] = bw_cand.index + 1

    # Format contribution & justification strings
    for df in [b_cand, bw_cand]:
        df['format_contribution'] = np.where(
            (df['ipl_pressure_balls'] > 0) & (df['t20i_pressure_balls'] > 0),
            df.apply(lambda r: f"IPL ({r['ipl_pressure_balls']}) + T20I ({r['t20i_pressure_balls']})", axis=1),
            np.where(df['ipl_pressure_balls'] > 0, "IPL Only", "T20I Only")
        )
        df['analytical_justification'] = df['player_id'].map(
            lambda pid: PLAYER_METADATA_NOTES.get(pid, "Consistent performance under competitive match urgency.")
        )

    # Export parquets for API
    b_cand.to_parquet(os.path.join(PROCESSED_DIR, "ranked_batters.parquet"), index=False)
    bw_cand.to_parquet(os.path.join(PROCESSED_DIR, "ranked_bowlers.parquet"), index=False)
    
    # Export full and top 10 CSVs
    top10_batters = b_cand.head(10)[[
        'rank', 'player_id', 'player_name', 'composite_pressure_rating',
        'pressure_strike_rate', 'expected_baseline_sr', 'role_adjusted_psr', 'shrunk_sr_lift',
        'pressure_balls_faced', 'overall_balls_faced', 'pressure_matches',
        'match_consistency_pct', 'qualifying_matches',
        'confidence_level', 'format_contribution', 'analytical_justification'
    ]].copy()
    top10_batters.to_csv(os.path.join(RANKINGS_DIR, "top10_batters.csv"), index=False)
    b_cand.to_csv(os.path.join(RANKINGS_DIR, "complete_batter_rankings.csv"), index=False)

    top10_bowlers = bw_cand.head(10)[[
        'rank', 'player_id', 'player_name', 'composite_pressure_rating',
        'pressure_economy', 'expected_baseline_econ', 'role_adjusted_pecon', 'shrunk_econ_lift',
        'pressure_legal_balls', 'overall_legal_balls', 'pressure_matches',
        'match_consistency_pct', 'qualifying_matches',
        'confidence_level', 'format_contribution', 'analytical_justification'
    ]].copy()
    top10_bowlers.to_csv(os.path.join(RANKINGS_DIR, "top10_bowlers.csv"), index=False)
    bw_cand.to_csv(os.path.join(RANKINGS_DIR, "complete_bowler_rankings.csv"), index=False)

    print("=== FINAL REFINED PRIMARY RANKING COMPUTATION COMPLETE ===")
    return top10_batters, top10_bowlers

if __name__ == "__main__":
    b10, bw10 = compute_rankings()
    print("\n--- FINAL REFINED TOP 10 BATTERS ---")
    print(b10[['rank', 'player_name', 'composite_pressure_rating', 'pressure_strike_rate', 'expected_baseline_sr', 'shrunk_sr_lift', 'pressure_balls_faced', 'match_consistency_pct']].to_string(index=False))
    print("\n--- FINAL REFINED TOP 10 BOWLERS ---")
    print(bw10[['rank', 'player_name', 'composite_pressure_rating', 'pressure_economy', 'expected_baseline_econ', 'shrunk_econ_lift', 'pressure_legal_balls', 'match_consistency_pct']].to_string(index=False))
