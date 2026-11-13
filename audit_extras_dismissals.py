import duckdb

con = duckdb.connect()

print("--- AUDITING DISMISSALS ON 'other' DELIVERIES ---")
print(con.execute("""
    SELECT is_wicket, dismissal_type, count(*)
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'other' AND is_wicket = True
    GROUP BY is_wicket, dismissal_type
""").fetchdf().to_string())

print("\n--- AUDITING DISMISSALS ON 'Overstep' DELIVERIES ---")
print(con.execute("""
    SELECT is_wicket, dismissal_type, count(*)
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'Overstep' AND is_wicket = True
    GROUP BY is_wicket, dismissal_type
""").fetchdf().to_string())

print("\n--- AUDITING DISMISSALS ON 'wide' DELIVERIES ---")
print(con.execute("""
    SELECT is_wicket, dismissal_type, count(*)
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'wide' AND is_wicket = True
    GROUP BY is_wicket, dismissal_type
""").fetchdf().to_string())
