import duckdb

conn = duckdb.connect()

print("--- Describing ball_by_ball.csv ---")
csv_cols = conn.execute("DESCRIBE SELECT * FROM 'ball_by_ball.csv'").df()
print(csv_cols[['column_name', 'column_type']].to_string())

print("\n--- Raw CSV extras breakdown for 'other' and 'Overstep' ---")
raw_csv_other = conn.execute("""
    SELECT 
        extras_type, extras1_runs, extras_2_runs,
        count(*) as cnt,
        avg(runs) as avg_runs,
        sum(case when is_wicket then 1 else 0 end) as wickets
    FROM 'ball_by_ball.csv'
    WHERE extras_type in ('other', 'Overstep')
    GROUP BY extras_type, extras1_runs, extras_2_runs
    ORDER BY extras_type, cnt DESC
""").df()
print(raw_csv_other.to_string())

print("\n--- Check legal balls in overs containing 'other' in ball_by_ball.csv ---")
legal_in_overs = conn.execute("""
    WITH other_overs AS (
        SELECT DISTINCT match_id, innings, overid
        FROM 'ball_by_ball.csv'
        WHERE extras_type = 'other'
    ),
    over_stats AS (
        SELECT 
            b.match_id, b.innings, b.overid,
            count(*) as total_deliveries,
            sum(case when extras_type in ('none', 'legbyes', 'byes') then 1 else 0 end) as standard_legal_deliveries,
            sum(case when extras_type = 'other' then 1 else 0 end) as other_count,
            sum(case when extras_type = 'wide' then 1 else 0 end) as wide_count,
            sum(case when extras_type = 'Overstep' then 1 else 0 end) as overstep_count
        FROM 'ball_by_ball.csv' b
        JOIN other_overs o ON b.match_id = o.match_id AND b.innings = o.innings AND b.overid = o.overid
        GROUP BY b.match_id, b.innings, b.overid
    )
    SELECT 
        standard_legal_deliveries,
        count(*) as num_overs
    FROM over_stats
    GROUP BY standard_legal_deliveries
    ORDER BY standard_legal_deliveries
""").df()
print(legal_in_overs.to_string())

print("\n--- Check total deliveries in overs containing 'other' vs standard overs without 'other' ---")
over_delivs = conn.execute("""
    WITH other_overs AS (
        SELECT DISTINCT match_id, innings, overid
        FROM 'ball_by_ball.csv'
        WHERE extras_type = 'other'
    )
    SELECT 
        count(*) as total_overs_with_other,
        avg(total_deliveries) as avg_delivs_in_other_overs
    FROM (
        SELECT b.match_id, b.innings, b.overid, count(*) as total_deliveries
        FROM 'ball_by_ball.csv' b
        JOIN other_overs o ON b.match_id = o.match_id AND b.innings = o.innings AND b.overid = o.overid
        GROUP BY b.match_id, b.innings, b.overid
    )
""").df()
print(over_delivs.to_string())

print("\n--- Compare with overs containing 'Overstep' ---")
overstep_delivs = conn.execute("""
    WITH overstep_overs AS (
        SELECT DISTINCT match_id, innings, overid
        FROM 'ball_by_ball.csv'
        WHERE extras_type = 'Overstep'
    )
    SELECT 
        count(*) as total_overs_with_overstep,
        avg(total_deliveries) as avg_delivs_in_overstep_overs
    FROM (
        SELECT b.match_id, b.innings, b.overid, count(*) as total_deliveries
        FROM 'ball_by_ball.csv' b
        JOIN overstep_overs o ON b.match_id = o.match_id AND b.innings = o.innings AND b.overid = o.overid
        GROUP BY b.match_id, b.innings, b.overid
    )
""").df()
print(overstep_delivs.to_string())
