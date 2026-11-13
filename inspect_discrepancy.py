import duckdb

con = duckdb.connect()

print("--- INVESTIGATING DISCREPANCIES IN EXTRAS ---")
# Let's inspect Match 14096 Innings 1 (RCB vs PBKS):
# RCB scored 205/2, our calculation gave 194. Why 11 runs difference?
# Let's inspect deliveries with extras in 14096 inn 1:
print(con.execute("""
    SELECT overid, over_ball_num, striker_name, bowler_name, runs, extras_type, extras1_runs, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14096 AND innings = 1 AND (extras_type != 'None' OR runs > 0)
    LIMIT 25
""").fetchdf().to_string())

# Let's see all extras deliveries in 14096 inn 1:
print("\nAll extras in 14096 inn 1:")
print(con.execute("""
    SELECT overid, over_ball_num, runs, extras_type, extras1_runs, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14096 AND innings = 1 AND extras_type != 'None'
""").fetchdf().to_string())
