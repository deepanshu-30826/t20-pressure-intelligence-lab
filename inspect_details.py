import duckdb
con = duckdb.connect()

print("--- DISMISSAL TYPES ---")
print(con.execute("""
    SELECT dismissal_type, dismissal_type_id, count(*), 
           sum(CASE WHEN is_wicket THEN 1 ELSE 0 END) as is_wicket_count
    FROM 'ball_by_ball.csv'
    WHERE dismissal_type IS NOT NULL OR is_wicket = True
    GROUP BY dismissal_type, dismissal_type_id
    ORDER BY count(*) DESC
""").fetchdf().to_string())

print("\n--- IPL & T20 COMPETITIONS ---")
print(con.execute("""
    SELECT comp_id, comp_name, match_format, season, count(DISTINCT m.match_id) as matches
    FROM 'competitions.csv' c
    LEFT JOIN 'matches.csv' m USING (comp_id)
    WHERE comp_name ILIKE '%IPL%' OR comp_name ILIKE '%Asia Cup%' OR match_format = 'T20'
    GROUP BY comp_id, comp_name, match_format, season
    ORDER BY comp_name
""").fetchdf().to_string())
