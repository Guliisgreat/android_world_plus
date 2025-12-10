# T3A Agent Performance Summary (All 6 Apps)

## Overview

- **Agent**: T3A with GPT-4o
- **Total Apps**: 6 (3 AndroidLab + 3 BMOCA)
- **Total Tasks**: 77
- **Date**: December 2025

## Per-App Results

| App | Tasks | Successful | SR (%) | Avg Steps | Max Steps (avg) |
|-----|-------|------------|--------|-----------|-----------------|
| **Bluecoins** | 15 | 8 | 53.3% | 12.2 | 26.0 |
| **Maps.me** | 15 | 6 | 40.0% | 16.5 | 23.3 |
| **Pi Music** | 12 | 7 | 58.3% | 6.9 | 17.1 |
| **Calculator** | 19 | 7 | 36.8% | 10.9 | 19.7 |
| **Snapseed** | 11 | 5 | 45.5% | 12.1 | 20.9 |
| **Wikipedia** | 5 | 4 | 80.0% | 5.2 | 22.0 |

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| **Total Tasks** | 77 |
| **Total Successful** | 37 |
| **Overall SR** | 48.1% |
| **Average Per-App SR** | 52.3% |
| **SR Std Dev** | 14.4% |
| **SR Variance** | 207.0 |
| **Average Steps/Task** | 11.4 |

## By App Category

| Category | Apps | Tasks | SR (%) | Avg Steps |
|----------|------|-------|--------|-----------|
| **AndroidLab** (new) | Bluecoins, Maps.me, Pi Music | 42 | 50.0% | 12.2 |
| **BMOCA** (existing) | Calculator, Snapseed, Wikipedia | 35 | 45.7% | 10.5 |

## Key Insights

1. **Best performing**: Wikipedia (80% SR) - simple navigation tasks
2. **Worst performing**: Calculator (36.8% SR) - complex formula input tasks
3. **Most efficient**: Wikipedia (5.2 avg steps), Pi Music (6.9 avg steps)
4. **Most steps needed**: Maps.me (16.5 avg steps) - navigation/search complexity

## Task Type Analysis

### Query Tasks (Information Retrieval)
- Generally higher success rates
- Agent uses `answer` action effectively
- Examples: BluecoinsQuery*, PiMusicQuery*, MapsMeCheck*

### Action Tasks (State Modification)
- Lower success rates
- Require precise UI interactions
- Examples: BluecoinsAdd*, BluecoinsEdit*, PiMusicCreate*

### Navigation Tasks
- Variable success rates
- Dependent on location search accuracy
- Examples: MapsMeNavigate*, WikipediaGoTo*

## Notes

- SR = Success Rate
- Avg Steps = Average number of steps taken per task
- Max Steps = Maximum allowed steps (complexity-based)
- AndroidLab apps are newly introduced tasks
- BMOCA apps are existing benchmark tasks

