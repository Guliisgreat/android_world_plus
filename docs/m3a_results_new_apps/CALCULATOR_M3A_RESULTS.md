# Calculator M3A Agent Test Results

## Overview

This document records the M3A agent performance on Calculator (BMOCA) tasks.

- **Agent**: M3A
- **App**: Calculator (Google)
- **Date**: December 5, 2025
- **Emulator**: Console port 5706, gRPC port 8556

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 19 |
| Successful | 3 |
| Failed | 16 |
| Success Rate | 15.8% (3/19) |

## Results by Task

| # | Task | Steps | Result | Score | Notes |
|---|------|-------|--------|-------|-------|
| 1 | CalculatorOpen | 4/10 | ✅ Success | 1.00 | Open calculator app |
| 2 | CalculatorInput1 | 4/15 | ✅ Success | 1.00 | Input single digit |
| 3 | CalculatorInput1Plus1 | 7/15 | ❌ Failed | 0.00 | Agent completed, conditions not met |
| 4 | CalculatorInput3Times5 | 13/15 | ✅ Success | 1.00 | Multiplication |
| 5 | CalculatorInput2Plus24Div3 | 20/20 | ❌ Max steps | 0.00 | Complex expression |
| 6 | CalculatorInput17Times23 | 11/20 | ❌ Failed | 0.00 | Agent completed, conditions not met |
| 7 | CalculatorInputCos60 | 13/20 | ❌ Failed | 0.00 | Trigonometry function |
| 8 | CalculatorInputCos180 | 12/20 | ❌ Failed | 0.00 | Trigonometry function |
| 9 | CalculatorInputFactorial6 | 20/20 | ❌ Max steps | 0.00 | Factorial operation |
| 10 | CalculatorInputSqrt25 | 20/20 | ❌ Max steps | 0.00 | Square root |
| 11 | CalculatorInputLn1234 | 20/20 | ❌ Max steps | 0.00 | Natural logarithm |
| 12 | CalculatorInput5Choose2 | 25/25 | ❌ Failed | 0.00 | Combinations (5C2) |
| 13 | CalculatorInput10Choose2 | 25/25 | ❌ Failed | 0.00 | Combinations (10C2) |
| 14 | CalculatorInputPercent50Of28 | 20/20 | ❌ Failed | 0.00 | Percentage calculation |
| 15 | CalculatorGeometricMean | 25/25 | ❌ Failed | 0.00 | Geometric mean |
| 16 | CalculatorHarmonicMean | 25/25 | ❌ Failed | 0.00 | Harmonic mean |
| 17 | CalculatorConvert45DegreesToRadians | 25/25 | ❌ Failed | 0.00 | Degree to radian conversion |
| 18 | CalculatorSumFirst5Fibonacci | 25/25 | ❌ Failed | 0.00 | Sum: 1+1+2+3+5 |
| 19 | CalculatorSumFirst5Primes | 25/25 | ❌ Failed | 0.00 | Sum: 2+3+5+7+11 |

## Failure Analysis

### By Failure Type

| Failure Type | Count | Percentage |
|--------------|-------|------------|
| Successful | 3 | 16% |
| Max steps reached | 4 | 21% |
| Agent completed but validation failed | 12 | 63% |

### Observations

1. **Simple tasks succeed**: Opening app (Task 1), single input (Task 2), basic multiplication (Task 4) all passed.

2. **Scientific functions fail**: cos(), factorial, sqrt, ln all failed - agent struggles with scientific calculator mode.

3. **Complex expressions fail**: Multi-operator expressions (2+24÷3) exceed step limits.

4. **Validation issues**: Most tasks the agent completes but the calculator display doesn't match expected value.

## Command to Run All Tasks

```bash
python scripts/test_all_bmoca_tasks.py --app calculator --run_all --console_port 5706 --grpc_port 8556
```

## Environment Verification

All tasks loaded and executed correctly, confirming:
- ✅ Emulator connection works
- ✅ Task registry is properly configured
- ✅ Calculator app launches correctly
- ✅ Validation logic executes properly
