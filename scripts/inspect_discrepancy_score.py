import duckdb

conn = duckdb.connect()

print("--- Match 14094 in matches.csv ---")
m = conn.execute("SELECT * FROM 'matches.csv' WHERE match_id = 14094").df()
print(m.T.to_string())

print("\n--- Match 14094 in raw ball_by_ball.csv ---")
df1 = conn.execute("""
    SELECT 
        innings,
        count(*) as total_balls,
        sum(runs) as batter_runs,
        sum(extras1_runs) as sum_extras1,
        sum(extras_2_runs) as sum_extras2,
        sum(case when extras_type = 'wide' then 1 else 0 end) as wides,
        sum(case when extras_type = 'legbyes' then extras1_runs else 0 end) as legbyes,
        sum(case when extras_type = 'byes' then extras1_runs else 0 end) as byes,
        sum(case when extras_type = 'Overstep' then 1 else 0 end) as oversteps,
        sum(case when extras_type = 'other' then 1 else 0 end) as others
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094
    GROUP BY innings
""").df()
print(df1.to_string())

print("\n--- Deliveries in innings 1 with extras in raw ball_by_ball.csv ---")
extras1 = conn.execute("""
    SELECT overid, over_ball_num, striker_name, bowler_name, runs, extras_type, extras1_runs, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094 AND innings = 1 AND (extras_type != 'none' OR extras1_runs > 0 OR extras_2_runs > 0)
""").df()
print(extras1.to_string())

print("\n--- Deliveries in innings 2 with extras in raw ball_by_ball.csv ---")
extras2 = conn.execute("""
    SELECT overid, over_ball_num, striker_name, bowler_name, runs, extras_type, extras1_runs, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094 AND innings = 2 AND (extras_type != 'none' OR extras1_runs > 0 OR extras_2_runs > 0)
""").df()
print(extras2.to_string())
