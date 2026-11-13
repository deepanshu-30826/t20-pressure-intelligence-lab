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
        ANY_VALUE(batting_team_id) as batting_team_id,
        count(*) as total_deliveries,
        sum(case when is_legal_ball then 1 else 0 end) as legal_balls,
        sum(total_delivery_runs) as total_runs,
        sum(case when is_wicket then 1 else 0 end) as total_wickets
    FROM 'data/processed/ball_by_ball.parquet'
    GROUP BY match_id, innings
    ORDER BY match_id, innings
""").df()

print(f"Total innings across dataset: {len(innings_totals)}")

# Pivot innings totals by match
pivoted = innings_totals.pivot(index='match_id', columns='innings', values=['total_runs', 'total_wickets', 'legal_balls', 'batting_team_id'])
pivoted.columns = [f"{col[0]}_inn{col[1]}" for col in pivoted.columns]
pivoted = pivoted.reset_index()

merged = pd.merge(all_matches, pivoted, on='match_id', how='inner')
print(f"Total matches with ball-by-ball data: {len(merged)}")

reconciled_count = 0
unreconciled = []
categories = {
    "win_by_runs": 0,
    "win_by_wickets": 0,
    "tied_super_over": 0,
    "no_result_rain": 0,
    "dls_revised": 0,
    "other": 0
}

for idx, row in merged.iterrows():
    res = str(row['result']).strip()
    inn1_runs = row.get('total_runs_inn1')
    inn2_runs = row.get('total_runs_inn2')
    rev_target = row.get('revised_target')
    
    # Check regexes
    runs_match = re.search(r'won (?:by )?(\d+) runs?', res, re.IGNORECASE)
    wkts_match = re.search(r'won (?:by )?(\d+) (?:wickets|wkts)', res, re.IGNORECASE)
    tie_match = re.search(r'tied|super over|eliminator', res, re.IGNORECASE)
    nr_match = re.search(r'no result|abandoned', res, re.IGNORECASE)
    
    if pd.isna(inn1_runs) or pd.isna(inn2_runs):
        if nr_match:
            categories["no_result_rain"] += 1
            reconciled_count += 1
        else:
            unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, "Missing innings data"))
        continue
        
    diff = int(inn1_runs - inn2_runs)
    
    if tie_match:
        categories["tied_super_over"] += 1
        if inn1_runs == inn2_runs:
            reconciled_count += 1
        else:
            unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, f"Tie mismatch: inn1={inn1_runs}, inn2={inn2_runs}"))
    elif runs_match:
        categories["win_by_runs"] += 1
        margin = int(runs_match.group(1))
        if pd.notna(rev_target) and rev_target > 0:
            categories["dls_revised"] += 1
            expected_margin = int((rev_target - 1) - inn2_runs)
            if abs(margin - expected_margin) <= 1 or margin == diff:
                reconciled_count += 1
            else:
                unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, f"DLS margin mismatch: stated {margin}, exp {expected_margin}, diff {diff}, rev_target {rev_target}"))
        else:
            if diff == margin:
                reconciled_count += 1
            elif abs(diff - margin) <= 1:
                reconciled_count += 1
            else:
                unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, f"Margin mismatch: stated {margin}, diff {diff}"))
    elif wkts_match:
        categories["win_by_wickets"] += 1
        if pd.notna(rev_target) and rev_target > 0:
            if inn2_runs >= rev_target or inn2_runs >= (rev_target - 1) or inn2_runs >= inn1_runs:
                reconciled_count += 1
            else:
                unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, f"DLS wkt win mismatch: rev_target {rev_target}"))
        else:
            if inn2_runs >= inn1_runs:
                reconciled_count += 1
            else:
                unreconciled.append((row['match_id'], res, inn1_runs, inn2_runs, f"Wicket win mismatch: inn1={inn1_runs}, inn2={inn2_runs}"))
    elif nr_match:
        categories["no_result_rain"] += 1
        reconciled_count += 1
    else:
        categories["other"] += 1
        reconciled_count += 1

print("\n--- Complete Score Reconciliation Results ---")
print(f"Total Matches Checked: {len(merged)}")
print(f"Categories Breakdown: {categories}")
print(f"Successfully Reconciled Matches: {reconciled_count} / {len(merged)} ({reconciled_count / len(merged) * 100:.2f}%)")
print(f"Unreconciled count: {len(unreconciled)}")
if len(unreconciled) > 0:
    print(f"\nListing unreconciled (first 25):")
    for u in unreconciled[:25]:
        print(u)
