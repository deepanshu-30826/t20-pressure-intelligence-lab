import duckdb
import pandas as pd

con = duckdb.connect()

print("--- EXAMINING COMPETITIONS IN DATASET ---")
comps = con.execute("""
    SELECT c.comp_id, c.comp_name, c.match_format, c.season, count(DISTINCT m.match_id) as match_count,
           min(m.match_date) as start_date, max(m.match_date) as end_date
    FROM 'competitions.csv' c
    JOIN 'matches.csv' m USING (comp_id)
    GROUP BY c.comp_id, c.comp_name, c.match_format, c.season
    ORDER BY c.season DESC, c.match_format, c.comp_name
""").fetchdf()

print(f"Total competitions with matches: {len(comps)}")
print("\nNon-T20I, non-IPL competitions:")
other_comps = comps[~comps['comp_name'].str.contains('IPL') & (comps['match_format'] != 'T20I')]
print(other_comps.to_string())

print("\nIPL Competitions:")
ipl_comps = comps[comps['comp_name'].str.contains('IPL')]
print(ipl_comps.to_string())

print("\nT20I Competitions summary by season:")
t20i_summary = con.execute("""
    SELECT c.season, count(DISTINCT c.comp_id) as num_comps, count(DISTINCT m.match_id) as num_matches
    FROM 'competitions.csv' c
    JOIN 'matches.csv' m USING (comp_id)
    WHERE c.match_format = 'T20I'
    GROUP BY c.season
    ORDER BY c.season DESC
""").fetchdf()
print(t20i_summary.to_string())
