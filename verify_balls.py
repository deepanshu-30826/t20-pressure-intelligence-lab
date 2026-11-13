import duckdb

con = duckdb.connect()

print("--- OVER BALL NUM FOR WIDES AND NO BALLS ---")
print(con.execute("""
    SELECT extras_type, count(*), 
           sum(CASE WHEN over_ball_num = lead_ball THEN 0 ELSE 1 END) as is_unique
    FROM (
        SELECT extras_type, over_ball_num, 
               LEAD(over_ball_num) OVER (PARTITION BY match_id, innings, overid ORDER BY innings_ball_num) as lead_ball
        FROM 'ball_by_ball.csv'
        WHERE match_id = 14094
    )
    GROUP BY extras_type
""").fetchdf().to_string())

# In cricket, legal deliveries in an over = 6 (except shortened or incomplete overs).
# Let's count deliveries by over for normal completed overs:
print("\n--- LEGAL BALLS DEFINITION VERIFICATION ---")
print(con.execute("""
    SELECT 
        count(*) as total_deliveries,
        sum(CASE WHEN extras_type IN ('wide', 'Penalty') THEN 0 ELSE 1 END) as balls_faced_batter,
        sum(CASE WHEN extras_type IN ('wide', 'Overstep', 'Penalty') THEN 0 ELSE 1 END) as legal_deliveries_bowler,
        sum(CASE WHEN extras_type = 'wide' THEN 1 ELSE 0 END) as wides,
        sum(CASE WHEN extras_type = 'Overstep' THEN 1 ELSE 0 END) as oversteps,
        sum(CASE WHEN extras_type = 'byes' THEN 1 ELSE 0 END) as byes,
        sum(CASE WHEN extras_type = 'legbyes' THEN 1 ELSE 0 END) as legbyes
    FROM 'ball_by_ball.csv'
""").fetchdf().to_string())

# Check how many legal balls bowled per 20-over completed innings in IPL 2022:
print("\n--- LEGAL BALLS PER INNINGS (IPL 2022 MATCH 14094 INN 1) ---")
print(con.execute("""
    SELECT 
        overid,
        count(*) as total_records,
        sum(CASE WHEN extras_type NOT IN ('wide', 'Overstep', 'Penalty') THEN 1 ELSE 0 END) as legal_bowler_balls,
        sum(CASE WHEN extras_type NOT IN ('wide', 'Penalty') THEN 1 ELSE 0 END) as batter_balls_faced
    FROM 'ball_by_ball.csv'
    WHERE match_id = 14094 AND innings = 1
    GROUP BY overid
    ORDER BY overid
""").fetchdf().to_string())
