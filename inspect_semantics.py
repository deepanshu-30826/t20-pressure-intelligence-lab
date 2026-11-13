import duckdb
import pandas as pd

con = duckdb.connect()

print("==========================================")
print("1. INVESTIGATING EXTRAS & RUNS")
print("==========================================")

# Check extras_type and its relation to extras1_runs and extras_2_runs
q1 = con.execute("""
    SELECT extras_type, 
           count(*) as count, 
           array_agg(DISTINCT extras1_runs) as distinct_extras1,
           array_agg(DISTINCT extras_2_runs) as distinct_extras2,
           array_agg(DISTINCT runs) as distinct_runs
    FROM 'ball_by_ball.csv'
    GROUP BY extras_type
""").fetchdf()
print("Extras distribution:")
print(q1.to_string())

# Cross-tab of extras_type vs extras1_runs
q2 = con.execute("""
    SELECT extras_type, extras1_runs, count(*) as count
    FROM 'ball_by_ball.csv'
    GROUP BY extras_type, extras1_runs
    ORDER BY extras_type, count DESC
""").fetchdf()
print("\nCross-tab extras_type vs extras1_runs:")
print(q2.to_string())

# Cross-tab of extras_type vs extras_2_runs
q3 = con.execute("""
    SELECT extras_type, extras_2_runs, count(*) as count
    FROM 'ball_by_ball.csv'
    GROUP BY extras_type, extras_2_runs
    ORDER BY extras_type, count DESC
""").fetchdf()
print("\nCross-tab extras_type vs extras_2_runs:")
print(q3.to_string())

# Let's inspect rows where is_four is True or is_six is True
q4 = con.execute("""
    SELECT is_four, is_six, runs, count(*) as count
    FROM 'ball_by_ball.csv'
    GROUP BY is_four, is_six, runs
    ORDER BY is_four, is_six, runs
""").fetchdf()
print("\nRuns vs is_four and is_six:")
print(q4.to_string())

# Let's inspect sample deliveries with extras_type != 'None'
q5 = con.execute("""
    SELECT match_id, innings, overid, over_ball_num, extras_type, extras1_runs, extras_2_runs, runs, is_four, is_six, is_wicket
    FROM 'ball_by_ball.csv'
    WHERE extras_type != 'None'
    LIMIT 20
""").fetchdf()
print("\nSample extras deliveries:")
print(q5.to_string())

print("\n==========================================")
print("2. INVESTIGATING DISMISSALS & WICKETS")
print("==========================================")
q6 = con.execute("""
    SELECT dismissal_type, dismissal_type_id, count(*) as count,
           sum(CASE WHEN is_wicket THEN 1 ELSE 0 END) as is_wicket_true_count
    FROM 'ball_by_ball.csv'
    WHERE dismissal_type IS NOT NULL OR is_wicket = True
    GROUP BY dismissal_type, dismissal_type_id
    ORDER BY count DESC
""").fetchdf()
print("Dismissal types:")
print(q6.to_string())

print("\n==========================================")
print("3. INVESTIGATING COMPETITIONS & SEASONS")
print("==========================================")
q7 = con.execute("""
    SELECT comp_id, comp_name, match_format, season, count(DISTINCT m.match_id) as match_count
    FROM 'competitions.csv' c
    LEFT JOIN 'matches.csv' m USING (comp_id)
    GROUP BY comp_id, comp_name, match_format, season
    ORDER BY season DESC, match_format, comp_name
""").fetchdf()
print("Competitions breakdown (all):")
print(q7.to_string())
