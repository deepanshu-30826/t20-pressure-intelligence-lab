# Official Methodology Report — T20 Pressure Intelligence Lab
## SupeRR Selector Season 2: Round 1 Challenge

---

### Executive Summary & Final Refined Primary Rankings

The **T20 Pressure Intelligence Lab** is an analytical system developed strictly in accordance with the official Round 1 Problem Statement:
> *"Build a data-driven system that measures how batters and bowlers perform in high-pressure match situations compared with their usual performance levels. Use your system to identify and rank the players who deliver most consistently when it matters."*

This is an independent, **league-wide** analytical evaluation covering **883 matches** and **200,999 ball-by-ball deliveries** across all historical IPL (2022–2026) and T20 Internationals (2022 onwards) in the supplied dataset. It is not an IPL 2027 auction filter or Rajasthan Royals squad selector.

#### Final Primary Methodology Refinements:
1. **Context-Only Structural Pressure Model:** Driven by Resource Scarcity, Match Urgency, Wickets Lost, and Knockout Stage Multipliers ($P \ge 60.0$). Completely avoids reconstructed run-chase score drift.
2. **Neutral Format Policy:** $W_{\text{format}} = 1.0$ (no artificial bonus or penalty for tournament coverage).
3. **Role-Adjusted Performance Baselines:**
   - Batters evaluated against position bands (1–3, 4–5, 6–7, 8+) and innings phases (Powerplay 1–6, Middle 7–15, Death 16–20).
   - Bowlers evaluated against phase-specific baseline expectations (Powerplay 8.15, Middle 8.01, Death 9.58 econ).
4. **Match-Level Consistency replacing Volume Bonuses:**
   - Multiplicative volume weights ($W_{\text{sample}}, W_{\text{match}}$) removed.
   - Replaced by explicit match consistency: percentage of qualifying matches in which the player met or exceeded their expected baseline.
5. **Empirical Bayes Shrinkage ($k=40$):** Sample-size stability enforced through principled shrinkage.

---

### Final Refined Top 10 Batters Under Pressure (League-Wide)

| Rank | Player Name | Player ID | Composite Rating | Pressure SR | Expected Role Par SR | Shrunk Lift ($k=40$) | Pressure Balls | Matches | Match Consistency % | Qualifying Matches | 95% Metric CI | Bootstrap $P(\text{Top } 10)$ | Median Rank | 95% Rank CI | Stability Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Naman Dhir** | `37052` | **73.99** | **196.4** | 147.2 | **+42.9** | 277 | 26 | **76.2%** | 21 | [174.1, 218.0] | **88.1%** | 4.0 | [1 – 18] | **HIGHLY STABLE** |
| **2** | **Jacob Bethell** | `23311` | **71.45** | **198.4** | 156.4 | **+31.8** | 125 | 12 | **75.0%** | 8 | [150.8, 234.1] | **67.4%** | 5.0 | [1 – 34] | SAMPLE-SENSITIVE |
| **3** | **Suryakumar Yadav** | `1699` | **69.75** | **195.7** | 159.3 | **+34.4** | 669 | 60 | **73.9%** | 46 | [178.6, 210.7] | **79.8%** | 6.0 | [1 – 20] | **HIGHLY STABLE** |
| **4** | **Hasan Nawaz** | `34891` | **68.10** | **185.9** | 150.3 | **+27.1** | 128 | 15 | **81.8%** | 11 | [136.5, 230.2] | **48.4%** | 11.0 | [1 – 35] | SAMPLE-SENSITIVE |
| **5** | **Rajat Patidar** | `4177` | **67.57** | **193.1** | 159.4 | **+28.7** | 232 | 24 | **70.6%** | 17 | [152.3, 225.3] | **54.8%** | 9.0 | [1 – 34] | SAMPLE-SENSITIVE |
| **6** | **Shreyas Iyer** | `3647` | **67.04** | **190.2** | 160.2 | **+27.8** | 518 | 44 | **70.3%** | 37 | [170.9, 208.0] | **53.9%** | 10.0 | [2 – 27] | SAMPLE-SENSITIVE |
| **7** | **Quinton de Kock** | `2101` | **66.53** | **197.4** | 170.6 | **+19.9** | 116 | 11 | **62.5%** | 8 | [135.0, 253.3] | **45.9%** | 12.0 | [1 – 35] | SAMPLE-SENSITIVE |
| **8** | **Sameer Rizvi** | `22722` | **66.12** | **178.0** | 149.7 | **+22.1** | 141 | 12 | **70.0%** | 10 | [151.4, 203.4] | **25.7%** | 18.0 | [3 – 34] | SAMPLE-SENSITIVE |
| **9** | **Sikandar Raza** | `2984` | **65.84** | **179.0** | 156.4 | **+20.1** | 324 | 28 | **65.0%** | 20 | [157.0, 199.1] | **20.5%** | 19.0 | [3 – 33] | SAMPLE-SENSITIVE |
| **10** | **Donovan Ferreira** | `13264` | **64.82** | **181.0** | 144.4 | **+31.1** | 226 | 22 | **62.5%** | 16 | [146.3, 212.7] | **44.6%** | 13.0 | [1 – 34] | SAMPLE-SENSITIVE |

---

### Final Refined Top 10 Bowlers Under Pressure (League-Wide)

| Rank | Player Name | Player ID | Composite Rating | Pressure Econ | Expected Phase Par Econ | Shrunk Lift ($k=40$) | Pressure Balls | Matches | Match Consistency % | Qualifying Matches | 95% Metric CI | Bootstrap $P(\text{Top } 10)$ | Median Rank | 95% Rank CI | Stability Classification |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | **Abrar Ahmed** | `5979` | **74.62** | **6.41** | 8.91 | **+2.00** | 161 | 23 | **76.5%** | 17 | [5.15, 7.93] | **96.6%** | 2.0 | [1 – 11] | **HIGHLY STABLE** |
| **2** | **Sunil Narine** | `781` | **71.42** | **6.80** | 8.94 | **+1.91** | 336 | 47 | **70.5%** | 44 | [5.82, 8.01] | **96.9%** | 2.0 | [1 – 11] | **HIGHLY STABLE** |
| **3** | **Craig Young** | `3720` | **68.47** | **7.99** | 8.95 | **+0.77** | 163 | 20 | **75.0%** | 16 | [6.68, 9.81] | **39.1%** | 13.0 | [2 – 32] | SAMPLE-SENSITIVE |
| **4** | **Jasprit Bumrah** | `1884` | **68.37** | **7.38** | 9.26 | **+1.77** | 665 | 66 | **70.5%** | 61 | [6.79, 8.49] | **94.3%** | 4.0 | [1 – 13] | **HIGHLY STABLE** |
| **5** | **Mujeeb Ur Rahman** | `6450` | **68.26** | **7.42** | 8.68 | **+0.99** | 144 | 25 | **88.2%** | 17 | [6.26, 9.44] | **51.4%** | 10.0 | [2 – 31] | SAMPLE-SENSITIVE |
| **6** | **Roston Chase** | `2687` | **67.81** | **7.16** | 8.62 | **+1.16** | 155 | 25 | **80.0%** | 15 | [6.00, 8.98] | **59.9%** | 9.0 | [1 – 28] | SAMPLE-SENSITIVE |
| **7** | **Jamie Overton** | `2382` | **66.96** | **8.03** | 9.13 | **+0.90** | 183 | 20 | **57.9%** | 19 | [6.80, 10.39] | **30.4%** | 17.0 | [2 – 34] | SAMPLE-SENSITIVE |
| **8** | **Akeal Hosein** | `2417` | **66.34** | **7.45** | 8.66 | **+1.04** | 249 | 38 | **65.5%** | 29 | [6.40, 9.59] | **37.3%** | 14.0 | [2 – 32] | SAMPLE-SENSITIVE |
| **9** | **Matheesha Pathirana** | `20785` | **65.24** | **8.03** | 9.23 | **+1.13** | 671 | 49 | **64.4%** | 45 | [7.96, 9.91] | **10.7%** | 19.0 | [7 – 32] | SAMPLE-SENSITIVE |
| **10** | **Abbas Afridi** | `7699` | **64.34** | **8.87** | 9.33 | **+0.36** | 138 | 17 | **50.0%** | 16 | [7.45, 11.16] | **13.2%** | 24.0 | [5 – 35] | SAMPLE-SENSITIVE |

*Sample Threshold Declaration:* The criteria of $\ge 100$ pressure balls and $\ge 10$ pressure matches represent **strict minimum sample thresholds for candidate eligibility**, not guarantees of absolute statistical certainty. True rank sensitivity is fully disclosed in the bootstrap columns above.

---

### Section 1: Role and Phase Baseline Adjustments

A batter or bowler should not be compared blindly against players executing completely different tactical roles.

#### Batting Benchmarks by Position Band & Phase:
- **Top Order (1–3):** Powerplay SR = 138.9, Middle SR = 145.0, Death SR = 184.6.
- **Middle Order (4–5):** Powerplay SR = 116.3, Middle SR = 132.7, Death SR = 178.1.
- **Finishers (6–7):** Powerplay SR = 93.0, Middle SR = 117.5, Death SR = 164.7.
- **Tail (8+):** Middle SR = 92.4, Death SR = 123.8.

A batter's expected role par SR is calculated as their ball-weighted peer average across the exact position and phase combinations they faced in pressure situations.

#### Bowling Benchmarks by Phase:
- **Powerplay (1–6):** Economy = 8.15, Wicket Rate = 4.51%, Dot % = 46.6%.
- **Middle Overs (7–15):** Economy = 8.01, Wicket Rate = 4.72%, Dot % = 32.5%.
- **Death Overs (16–20):** Economy = 9.58, Wicket Rate = 7.79%, Dot % = 32.2%.

A bowler's expected phase par economy is calculated as their ball-weighted peer average across the phases they bowled in pressure situations. This properly rewards death specialists (like Bumrah and Pathirana, whose pressure economy of ~7.4–8.0 vastly outperforms the 9.58 par).

---

### Section 2: Match-Level Consistency Methodology

To eliminate raw volume inflation while rewarding match-to-match reliability:
- **Batters:** Evaluated across distinct matches where the batter faced at least **5 pressure balls**. Consistency is the percentage of qualifying matches in which the batter's match pressure SR met or exceeded their expected role baseline.
- **Bowlers:** Evaluated across distinct matches where the bowler bowled at least **6 legal pressure balls** (1 full over). Consistency is the percentage of qualifying matches in which the bowler's match pressure economy was at or below their expected phase baseline.

---

### Section 3: Composite Rating Formula & Weights

#### Batter Rating (0–100):
- **30%**: Absolute role-adjusted pressure strike rate ($z_{\text{role\_adj\_psr}}$)
- **35%**: Shrunk pressure strike rate lift over baseline ($z_{\text{shrunk\_sr\_lift}}$, $k=40$)
- **15%**: Boundary rate gain ($z_{\text{boundary\_gain}}$)
- **10%**: Dot ball reduction ($z_{\text{dot\_reduction}}$)
- **10%**: Match-level consistency ($z_{\text{match\_consistency}}$)

$$\text{Raw Score}_{\text{bat}} = 0.30 \cdot z_{\text{role\_psr}} + 0.35 \cdot z_{\text{shrunk\_lift}} + 0.15 \cdot z_{\text{boundary}} + 0.10 \cdot z_{\text{dot}} + 0.10 \cdot z_{\text{consistency}}$$
$$\text{Composite Rating}_{\text{bat}} = \text{clip}(50.0 + 12.0 \cdot \text{Raw Score}_{\text{bat}}, 0, 100)$$

#### Bowler Rating (0–100):
- **25%**: Absolute role-adjusted pressure economy ($z_{\text{role\_adj\_pecon}}$, lower is better)
- **30%**: Shrunk economy lift over baseline ($z_{\text{shrunk\_econ\_lift}}$, $k=40$, higher is better)
- **20%**: Pressure wicket rate ($z_{\text{pwr}}$, higher is better)
- **10%**: Boundary suppression ($z_{\text{boundary\_supp}}$, higher is better)
- **5%**: Dot ball gain ($z_{\text{dot\_gain}}$, higher is better)
- **10%**: Match-level consistency ($z_{\text{match\_consistency}}$, higher is better)

$$\text{Raw Score}_{\text{bowl}} = 0.25 \cdot z_{\text{role\_pecon}} + 0.30 \cdot z_{\text{shrunk\_lift}} + 0.20 \cdot z_{\text{pwr}} + 0.10 \cdot z_{\text{boundary}} + 0.05 \cdot z_{\text{dot}} + 0.10 \cdot z_{\text{consistency}}$$
$$\text{Composite Rating}_{\text{bowl}} = \text{clip}(50.0 + 12.0 \cdot \text{Raw Score}_{\text{bowl}}, 0, 100)$$
