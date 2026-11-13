import duckdb
import pandas as pd

con = duckdb.connect()

print("=== COMPETITION SCOPE AUDIT ===")
comps = con.execute("""
    SELECT 
        c.comp_id, 
        c.comp_name, 
        c.match_format, 
        c.season,
        count(DISTINCT m.match_id) as match_count,
        count(b.match_id) as delivery_count
    FROM 'competitions.csv' c
    LEFT JOIN 'matches.csv' m ON c.comp_id = m.comp_id
    LEFT JOIN 'ball_by_ball.csv' b ON m.match_id = b.match_id
    GROUP BY c.comp_id, c.comp_name, c.match_format, c.season
    ORDER BY c.match_format, c.season, c.comp_name
""").fetchdf()

ipl = comps[comps['comp_name'].str.contains('IPL', case=False)]
t20i = comps[comps['match_format'] == 'T20I']
other = comps[~comps['comp_name'].str.contains('IPL', case=False) & (comps['match_format'] != 'T20I')]

print(f"Total matches: {comps['match_count'].sum()}, Total deliveries: {comps['delivery_count'].sum()}")
print(f"IPL matches: {ipl['match_count'].sum()}, deliveries: {ipl['delivery_count'].sum()}")
print(f"T20I matches: {t20i['match_count'].sum()}, deliveries: {t20i['delivery_count'].sum()}")
print(f"Other T20 matches: {other['match_count'].sum()}, deliveries: {other['delivery_count'].sum()}")

print("\n--- INCLUDED IPL COMPETITION IDs ---")
print(ipl[['comp_id', 'comp_name', 'season', 'match_count', 'delivery_count']].to_string())

print("\n--- EXCLUDED OTHER T20 COMPETITION IDs ---")
print(other[['comp_id', 'comp_name', 'season', 'match_count', 'delivery_count']].to_string())

print(f"\nTotal T20I competitions included: {len(t20i)}")
