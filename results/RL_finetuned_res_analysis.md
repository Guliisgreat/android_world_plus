# RL-Finetuned Agent Performance Summary (All 6 Apps)

## Overview

- **Agent**: RL-Finetuned UI-TARS-7B-SFT Agent on unseen apps
- **Total Apps**: 6 (3 AndroidLab + 3 BMOCA)
- **Total Tasks**: 77
- **Date**: December 2025

## Per-App Results

| App | Tasks | Successful | SR (%) | Avg Steps | Max Steps (avg) |
|-----|-------|------------|--------|-----------|-----------------|
| **Bluecoins** | 15 | 2 | 13.3% | 12.1 | 27.0 |
| **Maps.me** | 15 | 1 | 6.7% | 17.2 | 23.3 |
| **Pi Music** | 12 | 5 | 41.7% | 10.1 | 17.1 |
| **Calculator** | 19 | 4 | 21.1% | 10.6 | 19.7 |
| **Snapseed** | 11 | 4 | 36.4% | 12.6 | 20.9 |
| **Wikipedia** | 5 | 3 | 60.0% | 10.4 | 22.0 |

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| **Total Tasks** | 77 |
| **Total Successful** | 19 |
| **Overall SR** | 24.7% |
| **Weighted SR Variance** | 237.2 pp² |
| **Weighted SR Std Dev** | 15.4 pp |
| **Average Steps/Task** | 12.4 |

*Note: Weighted variance uses task counts as weights (apps with more tasks contribute more). Units are percentage points (pp).*

## By App Category

| Category | Apps | Tasks | SR (%) | Avg Steps |
|----------|------|-------|--------|-----------|
| **AndroidLab** | Bluecoins, Maps.me, Pi Music | 42 | 19.1% | 13.3 |
| **BMOCA** | Calculator, Snapseed, Wikipedia | 35 | 31.4% | 11.2 |

## Key Insights