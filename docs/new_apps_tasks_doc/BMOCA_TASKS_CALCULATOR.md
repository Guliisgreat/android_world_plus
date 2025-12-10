# Calculator App Tasks Documentation

## Overview

The Calculator app tasks test various mathematical operations and computations using the Google Calculator app. Tasks range from simple number input to complex mathematical formulas and statistical calculations.

**Package Name**: `com.google.android.calculator`  
**Total Tasks**: 19  
**Complexity Range**: 1.0 - 3.0

## Task List

### Basic Operations

#### CalculatorOpen
- **Complexity**: 1.0
- **Description**: Open the Calculator app
- **Goal**: "Open the Calculator app."
- **Success Criteria**: Calculator app is open (detected by package name or clear button)

#### CalculatorInput1
- **Complexity**: 1.5
- **Description**: Input the number 1 in the Calculator app
- **Goal**: "Input 1 in the Calculator app."
- **Success Criteria**: Formula display shows "1"

#### CalculatorInput1Plus1
- **Complexity**: 1.5
- **Description**: Input the expression '1+1' in the Calculator app
- **Goal**: "Input '1+1' in the Calculator app."
- **Success Criteria**: Formula display shows "1+1"

#### CalculatorInput3Times5
- **Complexity**: 1.5
- **Description**: Input the expression '3×5' in the Calculator app
- **Goal**: "Input '3×5' in the Calculator app."
- **Success Criteria**: Formula display shows "3×5"

#### CalculatorInput2Plus24Div3
- **Complexity**: 2.0
- **Description**: Input the expression '2+24÷3' in the Calculator app
- **Goal**: "Input '2+24÷3' in the Calculator app."
- **Success Criteria**: Formula display shows "2+24÷3"

#### CalculatorInput17Times23
- **Complexity**: 2.0
- **Description**: Input the expression '17×23' in the Calculator app
- **Goal**: "Input '17×23' in the Calculator app."
- **Success Criteria**: Formula display shows "17×23"

### Advanced Math Functions

#### CalculatorInputCos60
- **Complexity**: 2.0
- **Description**: Input 'cos(60)' in the Calculator app
- **Goal**: "Input 'cos(60)' in the Calculator app."
- **Success Criteria**: Formula display shows "c60" (Calculator's shorthand notation)

#### CalculatorInputCos180
- **Complexity**: 2.0
- **Description**: Input 'cos(180)' in the Calculator app
- **Goal**: "Input 'cos(180)' in the Calculator app."
- **Success Criteria**: Formula display shows "c180"

#### CalculatorInputFactorial6
- **Complexity**: 2.0
- **Description**: Input factorial of 6 in the Calculator app
- **Goal**: "Input factorial of 6 in the Calculator app."
- **Success Criteria**: Formula display shows "6!"

#### CalculatorInputSqrt25
- **Complexity**: 2.0
- **Description**: Input square root of 25 in the Calculator app
- **Goal**: "Input square root of 25 in the Calculator app."
- **Success Criteria**: Formula display shows "√25"

#### CalculatorInputLn1234
- **Complexity**: 2.0
- **Description**: Input 'ln(1234)' in the Calculator app
- **Goal**: "Input 'ln(1234)' in the Calculator app."
- **Success Criteria**: Formula display shows "l1234" (Calculator's shorthand notation)

### Combinatorics

#### CalculatorInput5Choose2
- **Complexity**: 2.5
- **Description**: Input the combination formula '5!÷(2!x3!)' in the Calculator app
- **Goal**: "Input '5!÷(2!x3!)' in the Calculator app."
- **Success Criteria**: Formula display shows "5!÷(2!×3!)"

#### CalculatorInput10Choose2
- **Complexity**: 2.5
- **Description**: Input the combination formula '10!÷(2!x8!)' in the Calculator app
- **Goal**: "Input '10!÷(2!x8!)' in the Calculator app."
- **Success Criteria**: Formula display shows "10!÷(2!×8!)"

### Percentage Operations

#### CalculatorInputPercent50Of28
- **Complexity**: 2.0
- **Description**: Compute 50% of 28 ('50%28') in the Calculator app
- **Goal**: "Compute 50% of 28 ('50%28') in the Calculator app."
- **Success Criteria**: Formula display shows "50%28"

### Statistical Calculations

#### CalculatorGeometricMean
- **Complexity**: 3.0
- **Description**: Compute the geometric mean of 3, 4, and 5 in the Calculator app
- **Goal**: "Compute the geometric mean of 3, 4, and 5 in the Calculator app."
- **Success Criteria**: Result display shows a value starting with "3.91" (approximately 3.914...)
- **Note**: Geometric mean = (3×4×5)^(1/3) ≈ 3.91

#### CalculatorHarmonicMean
- **Complexity**: 3.0
- **Description**: Compute the harmonic mean of 4 and 5 in the Calculator app
- **Goal**: "Compute the harmonic mean of 4 and 5 in the Calculator app."
- **Success Criteria**: Result display shows a value starting with "4.44" (approximately 4.444...)
- **Note**: Harmonic mean = 2/(1/4 + 1/5) = 40/9 ≈ 4.44

### Unit Conversion

#### CalculatorConvert45DegreesToRadians
- **Complexity**: 2.5
- **Description**: Input the formula for converting 45 degrees to radians
- **Goal**: "Input the formula for converting 45 degrees to radians ('45xπ÷180') in the Calculator app."
- **Success Criteria**: Formula display shows "45×π÷180"

### Formula Input Tasks

#### CalculatorSumFirst5Fibonacci
- **Complexity**: 2.5
- **Description**: Input the formula for computing sum of the first 5 Fibonacci numbers
- **Goal**: "Input the formula for computing sum of the first 5 Fibonacci numbers in the Calculator app."
- **Success Criteria**: Formula display shows either "0+1+1+2+3" or "1+1+2+3+5" (both are valid)

#### CalculatorSumFirst5Primes
- **Complexity**: 2.5
- **Description**: Input the formula for computing sum of the first 5 prime numbers
- **Goal**: "Input the formula for computing sum of the first 5 prime numbers in the Calculator app."
- **Success Criteria**: Formula display shows "2+3+5+7+11"

## Testing

To test Calculator tasks, use the unified test script:

```bash
# List all Calculator tasks
python scripts/test_all_bmoca_tasks.py --app calculator

# Test a specific task
python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorOpen

# Test with custom emulator port
python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorInput1Plus1 --console_port 5554
```

## Implementation Details

### Helper Functions

- **`_check_calculator_open(state)`**: Checks if Calculator app is open by looking for package name or clear button resource ID/name
- **`_get_formula_text(state)`**: Extracts the text from the formula display
- **`_get_result_text(state)`**: Extracts the text from result preview or final result display (returns tuple)

### Resource IDs

- Formula display: `com.google.android.calculator:id/formula`
- Result preview: `com.google.android.calculator:id/result_preview`
- Result final: `com.google.android.calculator:id/result_final`
- Clear button: `com.google.android.calculator:id/clr`

## Notes

- Calculator uses shorthand notation for some functions (e.g., "c60" for cos(60), "l1234" for ln(1234))
- Multiplication uses × (multiplication sign) not *
- Division uses ÷ (division sign) not /
- Some tasks verify formula input, others verify computed results
- Result verification uses prefix matching (e.g., "3.91" for geometric mean) to handle rounding

