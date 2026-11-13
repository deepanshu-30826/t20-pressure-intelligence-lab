import duckdb
import os
import pandas as pd

con = duckdb.connect()

tables = [
    'ball_by_ball.csv',
    'competitions.csv',
    'competition_team_player_mapping.csv',
    'matches.csv',
    'playing_eleven.csv',
    'teams.csv'
]

print("Starting discovery...")
for t in tables:
    print(f"\n==========================================")
    print(f"TABLE: {t}")
    print(f"==========================================")
    count = con.execute(f"SELECT count(*) FROM '{t}'").fetchone()[0]
    print(f"Row count: {count:,}")
    
    schema = con.execute(f"DESCRIBE SELECT * FROM '{t}'").fetchall()
    print("Columns:")
    for col in schema:
        null_count = con.execute(f"SELECT count(*) FROM '{t}' WHERE \"{col[0]}\" IS NULL").fetchone()[0]
        distinct_count = con.execute(f"SELECT count(DISTINCT \"{col[0]}\") FROM '{t}'").fetchone()[0]
        print(f"  - {col[0]} ({col[1]}): nulls={null_count:,}, distinct={distinct_count:,}")
        
    print("\nSample (first 2 rows):")
    sample = con.execute(f"SELECT * FROM '{t}' LIMIT 2").fetchdf()
    print(sample.to_dict(orient='records'))

print("\nDiscovery finished.")
