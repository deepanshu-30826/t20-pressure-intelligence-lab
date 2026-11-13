import duckdb

con = duckdb.connect()

print("--- EXTRAS TYPE = 'other' INSPECTION ---")
print(con.execute("""
    SELECT match_id, innings, overid, over_ball_num, striker_name, bowler_name, runs, extras_type, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'other'
    LIMIT 10
""").fetchdf().to_string())

print("\n--- EXTRAS TYPE = 'Overstep' INSPECTION ---")
print(con.execute("""
    SELECT match_id, innings, overid, over_ball_num, striker_name, bowler_name, runs, extras_type, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'Overstep'
    LIMIT 10
""").fetchdf().to_string())
