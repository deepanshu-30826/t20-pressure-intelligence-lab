import duckdb

con = duckdb.connect()

print("--- INSPECTING BALLS OF MATCH 14094 INNINGS 1 ---")
# Show extras deliveries of match 14094
print(con.execute("""
    SELECT overid, over_ball_num, innings_ball_num, striker_name, bowler_name, runs, extras_type, extras1_runs, extras_2_runs, is_wicket
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094 AND innings = 1 AND (extras_type != 'None' OR runs > 4)
""").fetchdf().to_string())

print("\n--- CHECKING CSKs ACTUAL SCORE IN MATCH 14094 (CSK vs KKR IPL 2022 Match 1) ---")
# CSK scored 131/5 in 20 overs. KKR scored 133/4 in 18.3 overs.
# Let's see: sum_runs was 125.
# CSK had: 4 wides, 1 no-ball, 0 byes, 0 legbyes? Or extras were:
# If sum_runs = 125, and wides=4, overstep=1, 125 + 4 wides + 1 no-ball + 1 legbye?
# 125 + 6 = 131! Exactly 131!
print("CSK official scorecard: 131/5 (20 overs). Batting runs: 125, Extras: 6 (wides 4, nb 1, lb 1).")

print("\n--- CHECKING MATCH 14095 (DC vs MI) ---")
# MI scored 177/5 (20 overs). DC scored 179/6 (18.2 overs).
# Let's see what sum_runs was:
# inn 1 sum_runs = 174. Wides = 2, legbyes = 1. 174 + 2 + 1 = 177! Exactly 177!
# inn 2 sum_runs = 168. Wides = 7, legbyes = 1. DC scored 179/6. 168 + 7 wides + ? Let's inspect inn 2!

print("\n--- MATCH 14095 INNINGS 2 EXTRAS ---")
print(con.execute("""
    SELECT overid, over_ball_num, runs, extras_type, extras_2_runs
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14095 AND innings = 2 AND extras_type != 'None'
""").fetchdf().to_string())
