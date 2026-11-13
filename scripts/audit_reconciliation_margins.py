import duckdb
import pandas as pd
import re

conn = duckdb.connect()

all_matches = conn.execute("""
    SELECT 
        m.match_id, m.comp_id, m.result, m.revised_target, m.win_team_id,
        c.comp_name
    FROM 'matches.csv' m
    JOIN 'competitions.csv' c ON m.comp_id = c.comp_id
""").df()

innings_totals = conn.execute("""
    SELECT 
        match_id, innings,
        sum(total_delivery_runs) as total_runs,
        sum(case when is_wicket then 1 else 0 end) as total_wickets
    FROM 'data/processed/ball_by_ball.parquet'
    GROUP BY match_id, innings
""").df()

pivoted = innings_totals.pivot(index='match_id', columns='innings', values=['total_runs', 'total_wickets'])
pivoted.columns = [f"{col[0]}_inn{col[1]}" for col in pivoted.columns]
pivoted = pivoted.reset_index()

merged = pd.merge(all_matches, pivoted, on='match_id', how='inner')

# Analyze win by runs margin errors
margin_diffs = []
chase_diffs = []

for idx, row in merged.iterrows():
    res = str(row['result']).strip()
    inn1_runs = row.get('total_runs_inn1')
    inn2_runs = row.get('total_runs_inn2')
    rev_target = row.get('revised_target')
    
    if pd.isna(inn1_runs) or pd.isna(inn2_runs):
        continue
        
    diff = int(inn1_runs - inn2_runs)
    
    runs_match = re.search(r'won (?:by )?(\d+) runs?', res, re.IGNORECASE)
    wkts_match = re.search(r'won (?:by )?(\d+) (?:wickets|wkts)', res, re.IGNORECASE)
    
    if runs_match and (pd.isna(rev_target) or rev_target == 0):
        margin = int(runs_match.group(1))
        margin_diffs.append(abs(diff - margin))
    elif wkts_match and (pd.isna(rev_target) or rev_target == 0):
        # In a chase win, inn2_runs should be >= inn1_runs + 1 (target)
        # Discrepancy is how far inn2_runs is from inn1_runs
        chase_diffs.append(inn2_runs - inn1_runs)

s_margin = pd.Series(margin_diffs)
print("--- Win by Runs: Error Distribution |diff - margin| ---")
print(s_margin.value_counts(bins=[-0.1, 0.5, 1.5, 3.5, 5.5, 10.5, 100]).sort_index())
print(f"Exact match (0 runs error): {(s_margin == 0).sum()} / {len(s_margin)} ({(s_margin == 0).mean()*100:.1f}%)")
print(f"Within 1 run: {(s_margin <= 1).sum()} / {len(s_margin)} ({(s_margin <= 1).mean()*100:.1f}%)")
print(f"Within 3 runs: {(s_margin <= 3).sum()} / {len(s_margin)} ({(s_margin <= 3).mean()*100:.1f}%)")
print(f"Within 5 runs: {(s_margin <= 5).sum()} / {len(s_margin)} ({(s_margin <= 5).mean()*100:.1f}%)")
print(f"Max error: {s_margin.max()} runs")

s_chase = pd.Series(chase_diffs)
print("\n--- Win by Wickets: Innings 2 Runs minus Innings 1 Runs ---")
print(f"Chases where inn2 >= inn1: {(s_chase >= 0).sum()} / {len(s_chase)} ({(s_chase >= 0).mean()*100:.1f}%)")
print(f"Chases where inn2 < inn1: {(s_chase < 0).sum()} / {len(s_chase)} ({(s_chase < 0).mean()*100:.1f}%)")
print(f"Distribution of inn2 - inn1 for 'chase wins':")
print(s_chase.value_counts().sort_index().head(10))
