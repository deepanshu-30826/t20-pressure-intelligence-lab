import duckdb
import pandas as pd

con = duckdb.connect()

print("--- AUDITING 'other' EXTRAS_TYPE ---")
# Check how many distinct matches and balls have extras_type = 'other'
other_df = con.execute("""
    SELECT 
        match_id, 
        innings, 
        overid, 
        over_ball_num, 
        striker_name, 
        bowler_name, 
        runs, 
        extras_type, 
        extras1_runs, 
        extras_2_runs,
        is_four,
        is_six
    FROM 'ball_by_ball.csv'
    WHERE extras_type = 'other'
""").fetchdf()

print(f"Total 'other' deliveries: {len(other_df)}")
print("Distribution of runs on 'other' deliveries:")
print(other_df['runs'].value_counts().to_string())

print("Distribution of extras_2_runs on 'other' deliveries:")
print(other_df['extras_2_runs'].value_counts().to_string())

# Check whether 'other' balls cause the over to have more than 6 balls!
print("\n--- CHECKING IF 'other' EXTENDS OVER LENGTH (REBOWLED) ---")
overs_with_other = con.execute("""
    WITH over_summary AS (
        SELECT 
            match_id, 
            innings, 
            overid,
            count(*) as total_deliveries_in_over,
            sum(CASE WHEN extras_type = 'other' THEN 1 ELSE 0 END) as other_count,
            sum(CASE WHEN extras_type = 'wide' THEN 1 ELSE 0 END) as wide_count,
            sum(CASE WHEN extras_type = 'Overstep' THEN 1 ELSE 0 END) as overstep_count,
            sum(CASE WHEN extras_type = 'None' THEN 1 ELSE 0 END) as none_count
        FROM 'ball_by_ball.csv'
        GROUP BY match_id, innings, overid
    )
    SELECT 
        count(*) as total_overs_with_other,
        avg(total_deliveries_in_over) as avg_balls_in_over,
        min(total_deliveries_in_over) as min_balls_in_over,
        max(total_deliveries_in_over) as max_balls_in_over,
        avg(total_deliveries_in_over - wide_count - overstep_count - other_count) as avg_legal_balls_if_other_is_noball,
        avg(total_deliveries_in_over - wide_count - overstep_count) as avg_legal_balls_if_other_is_legal
    FROM over_summary
    WHERE other_count > 0
""").fetchdf()
print(overs_with_other.to_string())
