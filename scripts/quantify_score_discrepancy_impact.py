import duckdb
import pandas as pd
import numpy as np

conn = duckdb.connect()

print("================================================================================")
print("   QUANTIFYING SCORE DISCREPANCY IMPACT ON PRESSURE & CONTEXT ALTERNATIVE       ")
print("================================================================================")

dp_path = 'data/processed/delivery_pressure.parquet'

df = conn.execute(f"""
    SELECT 
        match_id, innings, overid, over_ball_num,
        is_legal_ball, is_batter_ball, batter_runs, bowler_runs_conceded,
        striker_id, striker_name, bowler_id, bowler_name,
        balls_remaining, wickets_in_hand, runs_required, required_run_rate,
        resource_scarcity, match_urgency, wicket_pressure, scoring_demand,
        knockout_multiplier, batting_pressure_score, bowling_pressure_score,
        is_high_batting_pressure, is_high_bowling_pressure
    FROM '{dp_path}'
    WHERE is_primary_competition = TRUE
""").df()

n_total = len(df)
print(f"Total primary deliveries evaluated: {n_total}")

# 1. Simulate impact of +/- 3 runs scoreboard shift on required_run_rate in innings 2
inn2_mask = df['innings'] == 2
df_inn2 = df[inn2_mask].copy()

# Shift runs_required by +3 and -3 (upper bound of typical multi-run extras feed error)
shift_plus = np.clip(df_inn2['runs_required'] + 3, 0, None)
shift_minus = np.clip(df_inn2['runs_required'] - 3, 0, None)

b_rem = np.maximum(df_inn2['balls_remaining'], 1)
rrr_plus = (shift_plus * 6.0) / b_rem
rrr_minus = (shift_minus * 6.0) / b_rem

demand_plus = np.clip((rrr_plus - 5.0) / 15.0, 0, 1)
demand_minus = np.clip((rrr_minus - 5.0) / 15.0, 0, 1)

# Recalculate batting pressure with +3 and -3 runs
p_bat_plus = (
    0.35 * demand_plus + 
    0.30 * df_inn2['resource_scarcity'] + 
    0.20 * df_inn2['match_urgency'] + 
    0.15 * df_inn2['wicket_pressure']
) * 100.0 * df_inn2['knockout_multiplier']

p_bat_minus = (
    0.35 * demand_minus + 
    0.30 * df_inn2['resource_scarcity'] + 
    0.20 * df_inn2['match_urgency'] + 
    0.15 * df_inn2['wicket_pressure']
) * 100.0 * df_inn2['knockout_multiplier']

# Check classification flip rate (threshold 60.0)
orig_high = df_inn2['is_high_batting_pressure']
flip_plus = (p_bat_plus >= 60.0) != orig_high
flip_minus = (p_bat_minus >= 60.0) != orig_high

print("\n--- Sensitivity to +/- 3 Runs Scoreboard Discrepancy in Innings 2 ---")
print(f"Total Innings 2 deliveries: {len(df_inn2)}")
print(f"Deliveries that flip classification under +3 runs: {flip_plus.sum()} ({flip_plus.mean()*100:.2f}%)")
print(f"Deliveries that flip classification under -3 runs: {flip_minus.sum()} ({flip_minus.mean()*100:.2f}%)")
print(f"Mean absolute change in batting pressure score: {np.abs(p_bat_plus - df_inn2['batting_pressure_score']).mean():.2f} points (on 0-100 scale)")

# 2. Formulate Context-Based Pressure Alternative (Zero RRR dependence)
# Context Pressure = 0.45 * Resource Scarcity + 0.35 * Match Urgency + 0.20 * Wicket Pressure
df['context_pressure_batting'] = (
    0.45 * df['resource_scarcity'] + 
    0.35 * df['match_urgency'] + 
    0.20 * df['wicket_pressure']
) * 100.0 * df['knockout_multiplier']

df['is_high_context_batting_pressure'] = df['context_pressure_batting'] >= 60.0

corr_context = np.corrcoef(df['batting_pressure_score'], df['context_pressure_batting'])[0, 1]
print(f"\n--- Context-Only Model Comparison (Zero Scoreboard Dependence) ---")
print(f"Correlation between Primary Model and Context-Only Alternative: {corr_context:.4f}")
print(f"Classification agreement between Primary Model and Context Alternative: {(df['is_high_batting_pressure'] == df['is_high_context_batting_pressure']).mean()*100:.2f}%")

# 3. Check Top 10 Batters strike rates under Context-Only model vs Primary Model
top10_pids = [813, 1699, 1077, 6725, 20702, 796, 4986, 37052, 2984, 8101]

comparison_rows = []
for pid in top10_pids:
    p_df = df[df['striker_id'] == pid]
    p_name = p_df['striker_name'].iloc[0]
    
    # Primary model
    p_balls_prim = p_df[p_df['is_high_batting_pressure']]['is_batter_ball'].sum()
    p_runs_prim = p_df[p_df['is_high_batting_pressure']]['batter_runs'].sum()
    sr_prim = (p_runs_prim * 100.0) / p_balls_prim if p_balls_prim > 0 else 0
    
    # Context-only model
    p_balls_ctx = p_df[p_df['is_high_context_batting_pressure']]['is_batter_ball'].sum()
    p_runs_ctx = p_df[p_df['is_high_context_batting_pressure']]['batter_runs'].sum()
    sr_ctx = (p_runs_ctx * 100.0) / p_balls_ctx if p_balls_ctx > 0 else 0
    
    comparison_rows.append({
        "Player": p_name,
        "Primary Balls": int(p_balls_prim),
        "Primary SR": round(sr_prim, 1),
        "Context Balls": int(p_balls_ctx),
        "Context SR": round(sr_ctx, 1),
        "Delta SR": round(sr_ctx - sr_prim, 1)
    })

comp_df = pd.DataFrame(comparison_rows)
print("\n--- Performance Comparison: Primary Model vs Context-Only Alternative for Top 10 Batters ---")
print(comp_df.to_string(index=False))
