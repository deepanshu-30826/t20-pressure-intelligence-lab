import duckdb
import pandas as pd

con = duckdb.connect()

print("--- CANONICAL PLAYER RECONCILIATION ---")
# Check how many distinct player_id in ball_by_ball vs mapping
q_players = con.execute("""
    WITH bbb_players AS (
        SELECT striker_id as player_id, striker_name as name FROM 'ball_by_ball.csv'
        UNION
        SELECT non_striker_id as player_id, non_striker_name as name FROM 'ball_by_ball.csv'
        UNION
        SELECT bowler_id as player_id, bowler_name as name FROM 'ball_by_ball.csv'
    ),
    mapping_players AS (
        SELECT DISTINCT player_id, player_name FROM 'competition_team_player_mapping.csv'
    ),
    xi_players AS (
        SELECT DISTINCT player_id FROM 'playing_eleven.csv'
    )
    SELECT 
        (SELECT count(DISTINCT player_id) FROM bbb_players) as bbb_distinct_players,
        (SELECT count(DISTINCT player_id) FROM mapping_players) as mapping_distinct_players,
        (SELECT count(DISTINCT player_id) FROM xi_players) as xi_distinct_players,
        (SELECT count(DISTINCT player_id) FROM bbb_players WHERE player_id NOT IN (SELECT player_id FROM mapping_players)) as bbb_not_in_mapping,
        (SELECT count(DISTINCT player_id) FROM xi_players WHERE player_id NOT IN (SELECT player_id FROM mapping_players)) as xi_not_in_mapping
""").fetchdf()
print(q_players.to_string())

# Check if there are players in ball_by_ball not in mapping:
missing_in_mapping = con.execute("""
    WITH bbb_players AS (
        SELECT DISTINCT striker_id as player_id, striker_name as name FROM 'ball_by_ball.csv'
        UNION
        SELECT DISTINCT bowler_id as player_id, bowler_name as name FROM 'ball_by_ball.csv'
    )
    SELECT * FROM bbb_players WHERE player_id NOT IN (SELECT player_id FROM 'competition_team_player_mapping.csv')
""").fetchdf()
print(f"Missing in mapping: {len(missing_in_mapping)}")
if len(missing_in_mapping) > 0:
    print(missing_in_mapping.to_string())

# Check name discrepancies for the same player_id:
print("\n--- NAME CONSISTENCY ACROSS DATASETS ---")
name_check = con.execute("""
    SELECT player_id, count(DISTINCT player_name) as distinct_names, array_agg(DISTINCT player_name) as names
    FROM 'competition_team_player_mapping.csv'
    GROUP BY player_id
    HAVING count(DISTINCT player_name) > 1
""").fetchdf()
print(f"Player IDs with multiple names in mapping: {len(name_check)}")
if len(name_check) > 0:
    print(name_check.head(5).to_string())
