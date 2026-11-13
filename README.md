# T20 Pressure Intelligence Lab

**Rajasthan Royals SupeRR Selector Season 2 — Round 1 Challenge Submission**  
**Analytical Architecture:** Role-Adjusted Context-Only Structural Pressure Engine with Empirical Bayes Shrinkage and Match-Level Consistency  
**Dataset:** 883 Matches, 200,999 Deliveries (IPL 2022–2026 + T20Is from 2022 onward)

---

## Executive Summary

The **T20 Pressure Intelligence Lab** identifies professional T20 batters and bowlers who consistently perform above or maintain their normal baselines in high-urgency match situations, evaluated against role and phase expectations.

### Final Refined Rankings (Role-Adjusted, Neutral Format, Match Consistency)

#### Top 10 Batters Under Pressure
1. **Naman Dhir** (Rating: **73.99** | Pressure SR: **196.4** | Shrunk Lift: **+42.9** | 277 balls, 26 matches, 76.2% consistency)
2. **Jacob Bethell** (Rating: **71.45** | Pressure SR: **198.4** | Shrunk Lift: **+31.8** | 125 balls, 12 matches, 75.0% consistency)
3. **Suryakumar Yadav** (Rating: **69.75** | Pressure SR: **195.7** | Shrunk Lift: **+34.4** | 669 balls, 60 matches, 73.9% consistency)
4. **Hasan Nawaz** (Rating: **68.10** | Pressure SR: **185.9** | Shrunk Lift: **+27.1** | 128 balls, 15 matches, 81.8% consistency)
5. **Rajat Patidar** (Rating: **67.57** | Pressure SR: **193.1** | Shrunk Lift: **+28.7** | 232 balls, 24 matches, 70.6% consistency)
6. **Shreyas Iyer** (Rating: **67.04** | Pressure SR: **190.2** | Shrunk Lift: **+27.8** | 518 balls, 44 matches, 70.3% consistency)
7. **Quinton de Kock** (Rating: **66.53** | Pressure SR: **197.4** | Shrunk Lift: **+19.9** | 116 balls, 11 matches, 62.5% consistency)
8. **Sameer Rizvi** (Rating: **66.12** | Pressure SR: **178.0** | Shrunk Lift: **+22.1** | 141 balls, 12 matches, 70.0% consistency)
9. **Sikandar Raza** (Rating: **65.84** | Pressure SR: **179.0** | Shrunk Lift: **+20.1** | 324 balls, 28 matches, 65.0% consistency)
10. **Donovan Ferreira** (Rating: **64.82** | Pressure SR: **181.0** | Shrunk Lift: **+31.1** | 226 balls, 22 matches, 62.5% consistency)

#### Top 10 Bowlers Under Pressure
1. **Abrar Ahmed** (Rating: **74.62** | Pressure Econ: **6.41** | Shrunk Lift: **+2.00** | 161 balls, 23 matches, 76.5% consistency)
2. **Sunil Narine** (Rating: **71.42** | Pressure Econ: **6.80** | Shrunk Lift: **+1.91** | 336 balls, 47 matches, 70.5% consistency)
3. **Craig Young** (Rating: **68.47** | Pressure Econ: **7.99** | Shrunk Lift: **+0.77** | 163 balls, 20 matches, 75.0% consistency)
4. **Jasprit Bumrah** (Rating: **68.37** | Pressure Econ: **7.38** | Shrunk Lift: **+1.77** | 665 balls, 66 matches, 70.5% consistency)
5. **Mujeeb Ur Rahman** (Rating: **68.26** | Pressure Econ: **7.42** | Shrunk Lift: **+0.99** | 144 balls, 25 matches, 88.2% consistency)
6. **Roston Chase** (Rating: **67.81** | Pressure Econ: **7.16** | Shrunk Lift: **+1.16** | 155 balls, 25 matches, 80.0% consistency)
7. **Jamie Overton** (Rating: **66.96** | Pressure Econ: **8.03** | Shrunk Lift: **+0.90** | 183 balls, 20 matches, 57.9% consistency)
8. **Akeal Hosein** (Rating: **66.34** | Pressure Econ: **7.45** | Shrunk Lift: **+1.04** | 249 balls, 38 matches, 65.5% consistency)
9. **Matheesha Pathirana** (Rating: **65.24** | Pressure Econ: **8.03** | Shrunk Lift: **+1.13** | 671 balls, 49 matches, 64.4% consistency)
10. **Abbas Afridi** (Rating: **64.34** | Pressure Econ: **8.87** | Shrunk Lift: **+0.36** | 138 balls, 17 matches, 50.0% consistency)

---

## Deliverables Index

- **Top 10 Batters Export:** `artifacts/rankings/top10_batters.csv`
- **Top 10 Bowlers Export:** `artifacts/rankings/top10_bowlers.csv`
- **Complete Batters Ranking:** `artifacts/rankings/complete_batter_rankings.csv`
- **Complete Bowlers Ranking:** `artifacts/rankings/complete_bowler_rankings.csv`
- **Archived Context v1 Rankings:** `artifacts/rankings/archived_context_v1/`
- **Archived Score-Aware Rankings:** `artifacts/rankings/archived_score_aware/`
- **Official Methodology Report:** `artifacts/methodology/methodology_report.md`
- **1,000 Bootstrap Validation Report:** `artifacts/validation/bootstrap_1000_validation_report.json`
- **Audit Summary Data:** `artifacts/audit/data_audit_summary.json`
- **Comprehensive Audit Report:** `final_audit_report.md`
