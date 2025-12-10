# Bluecoins M3A Agent Test Results

## Overview

This document records the M3A (GPT-4-turbo) agent performance on Bluecoins tasks.

- **Agent**: M3A with GPT-4-turbo-2024-04-09
- **App**: Bluecoins (Personal Finance)
- **Date**: December 5, 2025
- **Emulator**: Console port 5706, gRPC port 8556

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 15 |
| Successful | 1 |
| Failed | 14 |
| Success Rate | 6.7% |

## Results by Task

### Query Tasks (5 tasks)

| # | Task | Steps | Result | Score | Notes |
|---|------|-------|--------|-------|-------|
| 1 | BluecoinsQuerySpendingOnDate | 6/20 | ✅ Success | 1.00 | Agent found correct total ($2,424) |
| 2 | BluecoinsQuerySpendingCategory | 20/20 | ❌ Max steps | 0.00 | Agent did not provide answer |
| 3 | BluecoinsQueryTotalSpendingOnDate | 20/20 | ❌ Max steps | 0.00 | Agent did not provide answer |
| 4 | BluecoinsQueryTransactionCount | 20/20 | ❌ Max steps | 0.00 | Agent did not provide answer |
| 5 | BluecoinsQueryCategorySpending | 25/25 | ❌ Max steps | 0.00 | Agent did not provide answer |

### Add Tasks (5 tasks)

| # | Task | Steps | Result | Score | Notes |
|---|------|-------|--------|-------|-------|
| 6 | BluecoinsAddExpense | 9/15 | ❌ Validation failed | 0.00 | No new transaction added |
| 7 | BluecoinsAddIncomeWithLabel | 20/20 | ❌ Max steps | 0.00 | No new transaction added |
| 8 | BluecoinsAddExpenseOnDate | 16/25 | ❌ Validation failed | 0.00 | No new transaction added |
| 9 | BluecoinsAddIncomeOnDateWithNote | 16/30 | ❌ Validation failed | 0.00 | No new transaction added |
| 10 | BluecoinsAddExpenseOnDateWithLabel | 12/30 | ❌ Validation failed | 0.00 | No new transaction added |

### Edit Tasks (5 tasks)

| # | Task | Steps | Result | Score | Notes |
|---|------|-------|--------|-------|-------|
| 11 | BluecoinsEditExpenseAmount | 25/25 | ❌ Max steps | 0.00 | No transaction found with new amount |
| 12 | BluecoinsEditIncomeDateAndAmount | 35/35 | ❌ Max steps | 0.00 | - |
| 13 | BluecoinsEditTransactionType | 35/35 | ❌ Max steps | 0.00 | - |
| 14 | BluecoinsEditTransactionTypeAmountNote | 33/40 | ❌ Validation failed | 0.00 | Task conditions not met |
| 15 | BluecoinsEditExpenseDateAmountNote | 40/40 | ❌ Max steps | 0.00 | - |

## Failure Analysis

### By Failure Type

| Failure Type | Count | Percentage |
|--------------|-------|------------|
| Max steps reached | 9 | 60% |
| Agent completed but validation failed | 5 | 33% |
| Successful | 1 | 7% |

### Root Causes

1. **Max Steps (9 tasks)**: Agent struggled to navigate Bluecoins UI to find/complete the required actions within step limit.

2. **Validation Failed (5 tasks)**: Agent indicated completion but:
   - For Add tasks: No transaction was actually saved (likely missed Save button)
   - For Edit tasks: Database didn't reflect the expected changes


## Environment Verification

All tasks loaded and executed correctly, confirming:
- ✅ Emulator connection works
- ✅ Task registry is properly configured
- ✅ App snapshots restore correctly
- ✅ Validation logic executes properly

The low success rate is due to **agent behavior limitations**, not environment/task design issues.

