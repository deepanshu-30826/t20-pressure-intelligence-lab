import duckdb
import pandas as pd

conn = duckdb.connect()

print("================================================================================")
print("             FORENSIC AUDIT OF ALL 264 'other' EXTRAS DELIVERIES                ")
print("================================================================================")

# 1. Total breakdown of runs and dismissals across all 264 instances
breakdown = conn.execute("""
    SELECT 
        extras_2_runs,
        runs as batter_runs,
        count(*) as count,
        sum(case when is_wicket then 1 else 0 end) as wickets,
        list(distinct dismissal_type) as dismissals
    FROM 'ball_by_ball.csv'
    WHERE lower(extras_type) = 'other'
    GROUP BY extras_2_runs, runs
    ORDER BY count DESC
""").df()
print("Breakdown of (extras_2_runs, batter_runs):")
print(breakdown.to_string())

# 2. Inspect the 11 exception overs (where standard_legal_deliveries != 6)
exceptions_df = conn.execute("""
    WITH other_overs AS (
        SELECT DISTINCT match_id, innings, overid
        FROM 'ball_by_ball.csv'
        WHERE lower(extras_type) = 'other'
    ),
    over_stats AS (
        SELECT 
            b.match_id, b.innings, b.overid,
            count(*) as total_deliveries,
            sum(case when lower(extras_type) in ('none', 'legbyes', 'byes') then 1 else 0 end) as legal_deliveries,
            sum(case when lower(extras_type) = 'other' then 1 else 0 end) as other_count,
            sum(case when lower(extras_type) = 'wide' then 1 else 0 end) as wide_count,
            sum(case when lower(extras_type) = 'overstep' then 1 else 0 end) as overstep_count
        FROM 'ball_by_ball.csv' b
        JOIN other_overs o ON b.match_id = o.match_id AND b.innings = o.innings AND b.overid = o.overid
        GROUP BY b.match_id, b.innings, b.overid
    )
    SELECT 
        s.*,
        m.result, m.revised_target
    FROM over_stats s
    JOIN 'matches.csv' m ON s.match_id = m.match_id
    WHERE legal_deliveries != 6
    ORDER BY legal_deliveries, match_id
""").df()
print(f"\nAudit of the {len(exceptions_df)} overs where standard_legal_deliveries != 6:")
print(exceptions_df.to_string())
