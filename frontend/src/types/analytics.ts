export interface OverviewData {
  total_matches: number;
  total_deliveries: number;
  pressure_deliveries: number;
  ipl_matches: number;
  t20i_matches: number;
  top_batter: {
    player_id: number;
    player_name: string;
    composite_pressure_rating: number;
    pressure_strike_rate: number;
  };
  top_bowler: {
    player_id: number;
    player_name: string;
    composite_pressure_rating: number;
    pressure_economy: number;
  };
  pressure_distribution: {
    batting_pressure: {
      mean: number;
      std: number;
      p25: number;
      p50: number;
      p75: number;
      p90: number;
      high_pressure_deliveries: number;
      high_pressure_pct: number;
    };
    bowling_pressure: {
      mean: number;
      std: number;
      p25: number;
      p50: number;
      p75: number;
      p90: number;
      high_pressure_deliveries: number;
      high_pressure_pct: number;
    };
  };
}

export interface BatterRanking {
  player_id: number;
  player_name: string;
  total_matches: number;
  overall_balls_faced: number;
  overall_strike_rate: number;
  pressure_balls_faced: number;
  pressure_matches: number;
  pressure_strike_rate: number;
  expected_baseline_sr: number;
  role_adjusted_psr: number;
  role_lift: number;
  shrunk_sr_lift: number;
  boundary_gain: number;
  dot_reduction: number;
  qualifying_matches: number;
  match_consistency_pct: number;
  ipl_pressure_balls: number;
  t20i_pressure_balls: number;
  z_role_psr: number;
  z_shrunk_lift: number;
  z_boundary: number;
  z_dot: number;
  z_consistency: number;
  composite_pressure_rating: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  rank: number;
  format_contribution: string;
  analytical_justification: string;
}

export interface BowlerRanking {
  player_id: number;
  player_name: string;
  total_matches: number;
  overall_legal_balls: number;
  overall_economy: number;
  pressure_legal_balls: number;
  pressure_matches: number;
  pressure_economy: number;
  expected_baseline_econ: number;
  role_adjusted_pecon: number;
  role_lift: number;
  shrunk_econ_lift: number;
  pressure_wicket_rate: number;
  boundary_suppression: number;
  dot_gain: number;
  qualifying_matches: number;
  match_consistency_pct: number;
  ipl_pressure_balls: number;
  t20i_pressure_balls: number;
  z_role_pecon: number;
  z_shrunk_lift: number;
  z_pwr: number;
  z_boundary: number;
  z_dot: number;
  z_consistency: number;
  composite_pressure_rating: number;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  rank: number;
  format_contribution: string;
  analytical_justification: string;
}

export interface PhaseSplit {
  innings_phase: string;
  balls: number;
  runs: number;
  pressure_balls: number;
  pressure_runs: number;
}

export interface PlayerProfileResponse {
  player_id: number;
  name: string;
  batting_profile: BatterRanking | null;
  bowling_profile: BowlerRanking | null;
  batting_phase_split: PhaseSplit[];
}

export interface PlayerMatchRecord {
  match_id: number;
  comp_name: string;
  season: string;
  match_date: string;
  balls_faced: number;
  runs: number;
  pressure_balls: number;
  pressure_runs: number;
}

export interface DataAuditSummary {
  system_name?: string;
  audit_version?: string;
  audit_timestamp?: string;
  dataset_summary?: {
    total_matches_in_archive: number;
    total_deliveries_in_archive: number;
    primary_matches: number;
    primary_deliveries: number;
    ipl_matches: number;
    t20i_matches: number;
    excluded_development_competitions: Array<{
      comp_id: number;
      comp_name: string;
      matches: number;
      deliveries: number;
      exclusion_reason: string;
    }>;
  };
  data_quality_findings?: {
    extras_classification: {
      status: string;
      total_other_extras_instances: number;
      recommendation: string;
    };
    score_reconstruction_audit: {
      status: string;
      summary: string;
      mitigation_strategy: string;
    };
  };
}
