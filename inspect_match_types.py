import duckdb
import pandas as pd

con = duckdb.connect()

print("--- INNINGS PER MATCH ---")
inn_counts = con.execute("""
    SELECT innings, count(*) as count, count(DISTINCT match_id) as matches
    FROM 'ball_by_ball.csv'
    GROUP BY innings
    ORDER BY innings
""").fetchdf()
print(inn_counts.to_string())

print("\n--- SUPER OVERS (INNINGS 3 AND 4) ---")
super_overs = con.execute("""
    SELECT DISTINCT m.match_id, c.comp_name, m.match_date, m.result
    FROM 'ball_by_ball.csv' b
    JOIN 'matches.csv' m USING (match_id)
    JOIN 'competitions.csv' c USING (comp_id)
    WHERE b.innings IN (3, 4)
""").fetchdf()
print(super_overs.to_string())

print("\n--- SHORTENED MATCHES (REVISED OVERS / TARGET) ---")
revised = con.execute("""
    SELECT m.match_id, c.comp_name, m.match_date, m.first_inn_revised_overs, m.second_inn_revised_overs, m.revised_target, m.result
    FROM 'matches.csv' m
    JOIN 'competitions.csv' c USING (comp_id)
    WHERE m.revised_target IS NOT NULL OR m.first_inn_revised_overs IS NOT NULL OR m.second_inn_revised_overs IS NOT NULL
""").fetchdf()
print(f"Total shortened/revised matches: {len(revised)}")
print(revised.head(10).to_string())

print("\n--- MATCHES WITHOUT DELIVERIES ---")
no_delivs = con.execute("""
    SELECT m.match_id, c.comp_name, m.match_date, m.result
    FROM 'matches.csv' m
    JOIN 'competitions.csv' c USING (comp_id)
    WHERE m.match_id NOT IN (SELECT DISTINCT match_id FROM 'ball_by_ball.csv')
""").fetchdf()
print(f"Matches with no deliveries: {len(no_delivs)}")
print(no_delivs.to_string())
