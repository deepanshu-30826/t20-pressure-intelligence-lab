import duckdb

con = duckdb.connect()

print("--- OVER 19 IN MATCH 14094 INNINGS 1 ---")
print(con.execute("""
    SELECT overid, over_ball_num, innings_ball_num, striker_name, bowler_name, runs, extras_type, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094 AND innings = 1 AND overid = 19
    ORDER BY innings_ball_num
""").fetchdf().to_string())
