import duckdb
import pandas as pd

con = duckdb.connect()

print("--- OVER BALL NUM AND EXTRAS ---")
print(con.execute("""
    SELECT extras_type, count(*), 
           sum(runs) as total_runs,
           sum(extras_2_runs) as total_extras2
    FROM 'ball_by_ball.csv'
    GROUP BY extras_type
""").fetchdf().to_string())

print("\n--- SAMPLE SCORE RECONSTRUCTION CHECK ---")
# Pick 3 matches from IPL 2022 and inspect total runs by innings
sample_matches = con.execute("""
    SELECT DISTINCT m.match_id, c.comp_name, m.result
    FROM 'matches.csv' m
    JOIN 'competitions.csv' c USING (comp_id)
    WHERE c.comp_name = 'IPL 2022' AND m.result LIKE '%Won by%'
    LIMIT 5
""").fetchdf()
print("Sample matches:")
print(sample_matches.to_string())

for m_id in sample_matches['match_id'].head(3):
    print(f"\n--- MATCH {m_id} ---")
    match_info = con.execute(f"SELECT * FROM 'matches.csv' WHERE match_id = {m_id}").fetchdf().iloc[0]
    print(f"Result: {match_info['result']}")
    
    # Check runs summed
    inn_stats = con.execute(f"""
        SELECT innings, 
               count(*) as total_rows,
               sum(CASE WHEN extras_type NOT IN ('wide', 'Penalty') THEN 1 ELSE 0 END) as legal_balls_candidate,
               sum(CASE WHEN extras_type NOT IN ('wide', 'Penalty', 'Overstep') THEN 1 ELSE 0 END) as legal_balls_no_nb,
               sum(runs) as sum_runs,
               sum(CASE WHEN extras_type = 'wide' THEN 1 ELSE 0 END) as wides_count,
               sum(CASE WHEN extras_type = 'Overstep' THEN 1 ELSE 0 END) as overstep_count,
               sum(CASE WHEN extras_type = 'byes' THEN 1 ELSE 0 END) as byes_count,
               sum(CASE WHEN extras_type = 'legbyes' THEN 1 ELSE 0 END) as legbyes_count,
               sum(extras_2_runs) as sum_extras_2
        FROM 'ball_by_ball.csv'
        WHERE match_id = {m_id}
        GROUP BY innings
        ORDER BY innings
    """).fetchdf()
    print(inn_stats.to_string())
