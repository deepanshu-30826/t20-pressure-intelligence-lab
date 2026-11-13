import unittest
import pandas as pd
import numpy as np
import os
import json

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROCESSED_DIR = os.path.join(WORKSPACE, "data", "processed")
RANKINGS_DIR = os.path.join(WORKSPACE, "artifacts", "rankings")
VALIDATION_DIR = os.path.join(WORKSPACE, "artifacts", "validation")

class TestRigorousAudit(unittest.TestCase):
    def test_top10_batters_integrity(self):
        df = pd.read_csv(os.path.join(RANKINGS_DIR, "top10_batters.csv"))
        self.assertEqual(len(df), 10)
        self.assertEqual(df['rank'].tolist(), list(range(1, 11)))
        self.assertEqual(df['player_id'].nunique(), 10)
        # Verify 100% High confidence in Top 10
        self.assertTrue((df['confidence_level'] == 'HIGH').all())
        # All have >= 100 pressure balls
        self.assertTrue((df['pressure_balls_faced'] >= 100).all())
        # All have >= 10 pressure matches
        self.assertTrue((df['pressure_matches'] >= 10).all())

    def test_top10_bowlers_integrity(self):
        df = pd.read_csv(os.path.join(RANKINGS_DIR, "top10_bowlers.csv"))
        self.assertEqual(len(df), 10)
        self.assertEqual(df['rank'].tolist(), list(range(1, 11)))
        self.assertEqual(df['player_id'].nunique(), 10)
        # Verify 100% High confidence in Top 10
        self.assertTrue((df['confidence_level'] == 'HIGH').all())
        # All have >= 100 pressure legal balls
        self.assertTrue((df['pressure_legal_balls'] >= 100).all())
        # All have >= 10 pressure matches
        self.assertTrue((df['pressure_matches'] >= 10).all())

    def test_no_future_data_leakage(self):
        # Verify pre-delivery cumulative score matches
        dp = pd.read_parquet(os.path.join(PROCESSED_DIR, "delivery_pressure.parquet"))
        sample = dp[dp['match_id'] == 14094].sort_values(['innings', 'overid', 'over_ball_num'])
        # Pre-delivery score for ball 1 of inning 1 must be 0
        self.assertEqual(sample.iloc[0]['score_before_delivery'], 0)
        self.assertEqual(sample.iloc[0]['wickets_lost_before_delivery'], 0)

    def test_cricket_extras_classification(self):
        bbb = pd.read_parquet(os.path.join(PROCESSED_DIR, "ball_by_ball.parquet"))
        # Wide and Overstep must not be legal balls
        self.assertTrue((bbb[bbb['extras_type'].isin(['wide', 'Overstep', 'other'])]['is_legal_ball'] == False).all())
        # Byes and legbyes must be legal balls
        self.assertTrue((bbb[bbb['extras_type'].isin(['byes', 'legbyes'])]['is_legal_ball'] == True).all())

    def test_bootstrap_report_exists(self):
        val_file = os.path.join(VALIDATION_DIR, "bootstrap_1000_validation_report.json")
        self.assertTrue(os.path.exists(val_file))
        with open(val_file) as f:
            data = json.load(f)
            self.assertEqual(data['iterations'], 1000)

if __name__ == '__main__':
    unittest.main()
