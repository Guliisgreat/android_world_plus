# Agent Performance Comparison (All 6 Apps)

## Overview

- **Total Apps**: 6 (3 AndroidLab + 3 BMOCA)
- **Total Tasks**: 77
- **Date**: December 2025

## Per-App Success Rate (%) Comparison

| App | Tasks | T3A | M3A | Qwen2.5-VL 7B | UI-TARS 7B SFT | RL Finetuned |
|-----|-------|-----|-----|---------------|----------------|--------------|
| **Bluecoins** | 15 | 53.3% | 6.7% | 0.0% | 6.7% | 13.3% |
| **Maps.me** | 15 | 40.0% | 0.0% | 6.7% | 0.0% | 6.7% |
| **Pi Music** | 12 | 58.3% | 0.0% | 8.3% | 33.3% | 41.7% |
| **Calculator** | 19 | 36.8% | 15.8% | 0.0% | 21.1% | 21.1% |
| **Snapseed** | 11 | 45.5% | 0.0% | 0.0% | 36.4% | 36.4% |
| **Wikipedia** | 5 | 80.0% | 40.0% | 20.0% | 60.0% | 60.0% |

## Aggregate Statistics

| Metric | T3A | M3A | Qwen2.5-VL 7B | UI-TARS 7B SFT | RL Finetuned |
|--------|-----|-----|---------------|----------------|--------------|
| **Total Successful** | 37 | 6 | 3 | 16 | 19 |
| **Overall SR** | 48.1% | 7.8% | 3.9% | 20.8% | 24.7% |
| **Weighted SR Variance** | 132.8 pp² | 113.4 pp² | 30.3 pp² | 281.9 pp² | 237.2 pp² |
| **Weighted SR Std Dev** | 11.5 pp | 10.7 pp | 5.5 pp | 16.8 pp | 15.4 pp |
| **Avg Steps/Task** | 11.4 | 12.7 | 3.2 | 13.8 | 12.4 |

## By App Category

### AndroidLab Apps 

| App | Tasks | T3A | M3A | Qwen2.5-VL 7B | UI-TARS 7B SFT | RL Finetuned |
|-----|-------|-----|-----|---------------|----------------|--------------|
| Bluecoins | 15 | 53.3% | 6.7% | 0.0% | 6.7% | 13.3% |
| Maps.me | 15 | 40.0% | 0.0% | 6.7% | 0.0% | 6.7% |
| Pi Music | 12 | 58.3% | 0.0% | 8.3% | 33.3% | 41.7% |
| **Subtotal** | **42** | **50.0%** | **2.4%** | **4.8%** | **11.9%** | **19.1%** |

### BMOCA Apps 

| App | Tasks | T3A | M3A | Qwen2.5-VL 7B | UI-TARS 7B SFT | RL Finetuned |
|-----|-------|-----|-----|---------------|----------------|--------------|
| Calculator | 19 | 36.8% | 15.8% | 0.0% | 21.1% | 21.1% |
| Snapseed | 11 | 45.5% | 0.0% | 0.0% | 36.4% | 36.4% |
| Wikipedia | 5 | 80.0% | 40.0% | 20.0% | 60.0% | 60.0% |
| **Subtotal** | **35** | **45.7%** | **14.3%** | **2.9%** | **31.4%** | **31.4%** |

## Average Steps per Task

| App | Tasks | T3A | M3A | Qwen2.5-VL 7B | UI-TARS 7B SFT | RL Finetuned |
|-----|-------|-----|-----|---------------|----------------|--------------|
| Bluecoins | 15 | 12.2 | 18.4 | 3.6 | 11.9 | 12.1 |
| Maps.me | 15 | 16.5 | 10.4 | 2.2 | 20.6 | 17.2 |
| Pi Music | 12 | 6.9 | 5.4 | 2.0 | 10.5 | 10.1 |
| Calculator | 19 | 10.9 | 17.8 | 4.0 | 12.7 | 10.6 |
| Snapseed | 11 | 12.1 | 8.6 | 4.7 | 13.6 | 12.6 |
| Wikipedia | 5 | 5.2 | 20.0 | 2.0 | 11.2 | 10.4 |
| **Average** | **77** | **11.4** | **12.7** | **3.2** | **13.8** | **12.4** |

## Agent Details

- [T3A](t3a_res_analysis.md)
- [M3A](m3a_res_analysis.md)
- [Qwen2.5-VL 7B](qwen2.5vl_7B_res_analysis.md)
- [UI-TARS 7B SFT](uitars_7B_sft_res_analysis.md)
- [RL Finetuned](RL_finetuned_res_analysis.md)

