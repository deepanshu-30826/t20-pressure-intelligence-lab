import duckdb
import pandas as pd

con = duckdb.connect()

print("--- AUDITING PLAYER CAREER HISTORIES IN SUPPLIED DATASET ---")
# Check which competitions each Top 10 player participated in
players_to_audit = [
    # Batters
    (813, "Jos Buttler"),
    (2921, "Fakhar Zaman"),
    (6467, "Anuj Rawat"),
    (6725, "Sherfane Rutherford"),
    (1699, "Suryakumar Yadav"),
    (37052, "Naman Dhir"),
    (796, "Matthew Wade"),
    (1077, "David Miller"),
    (3024, "Mohammad Rizwan"),
    (838, "Glenn Maxwell"),
    # Bowlers
    (2382, "Jamie Overton"),
    (46066, "Vipraj Nigam"),
    (8530, "Kartik Tyagi"),
    (5979, "Abrar Ahmed"),
    (2636, "Adam Zampa"),
    (158, "Amit Mishra"),
    (4856, "Benjamin Sears"),
    (7967, "Noor Ahmad"),
    (5808, "Karim Janat"),
    (4487, "Vyshak Kumar")
]

p_ids = [p[0] for p in players_to_audit]

career_df = con.execute(f"""
    WITH p_bbb AS (
        SELECT 
            striker_id as player_id,
            match_id,
            innings_phase,
            is_high_batting_pressure,
            is_high_bowling_pressure
        FROM 'data/processed/delivery_pressure.parquet'
        WHERE striker_id IN ({','.join(map(str, p_ids))})
        UNION ALL
        SELECT 
            bowler_id as player_id,
            match_id,
            innings_phase,
            is_high_batting_pressure,
            is_high_bowling_pressure
        FROM 'data/processed/delivery_pressure.parquet'
        WHERE bowler_id IN ({','.join(map(str, p_ids))})
    )
    SELECT 
        p.player_id,
        m.competition_tier,
        count(DISTINCT m.match_id) as matches,
        min(m.season) as earliest_season,
        max(m.season) as latest_season
    FROM p_bbb p
    JOIN 'data/processed/matches.parquet' m USING (match_id)
    GROUP BY p.player_id, m.competition_tier
    ORDER BY p.player_id, m.competition_tier
""").fetchdf()

print(career_df.to_string())
