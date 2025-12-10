# BMOCA Tasks Documentation

## Overview

This directory contains documentation for all BMOCA (Benchmark for Mobile Control Agents) app tasks implemented in AndroidWorld. These tasks test various mobile apps including Calculator, Snapseed, and Wikipedia.

## Quick Start

### Test All Tasks

Use the unified test script to test tasks from any BMOCA app:

```bash
# List all available tasks
python scripts/test_all_bmoca_tasks.py --app all

# List tasks for a specific app
python scripts/test_all_bmoca_tasks.py --app calculator
python scripts/test_all_bmoca_tasks.py --app snapseed
python scripts/test_all_bmoca_tasks.py --app wikipedia

# Test a specific task
python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorOpen
python scripts/test_all_bmoca_tasks.py --app snapseed --task SnapseedTask1
python scripts/test_all_bmoca_tasks.py --app wikipedia --task WikipediaOpen
```

### Requirements

- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Emulator**: Running Android emulator on port 5554 (default)
- **Apps Installed**: Calculator, Snapseed, and Wikipedia apps must be installed on the emulator

## App Documentation

### [Calculator Tasks](./BMOCA_TASKS_CALCULATOR.md)
- **Total Tasks**: 19
- **Complexity Range**: 1.0 - 3.0
- **Categories**: Basic operations, advanced math, combinatorics, statistics, unit conversion, formulas

### [Snapseed Tasks](./BMOCA_TASKS_SNAPSEED.md)
- **Total Tasks**: 11
- **Complexity Range**: 1.0 - 3.0
- **Categories**: Navigation, filter application, settings configuration, combined tasks

### [Wikipedia Tasks](./BMOCA_TASKS_WIKIPEDIA.md)
- **Total Available Tasks**: 5 (many implemented but disabled)
- **Complexity Range**: 1.0 - 4.0
- **Categories**: Navigation, text size customization, feed customization

## Task Statistics

| App | Total Tasks | Available | Complexity Range |
|-----|-------------|-----------|------------------|
| Calculator | 19 | 19 | 1.0 - 3.0 |
| Snapseed | 11 | 11 | 1.0 - 3.0 |
| Wikipedia | 17 | 5 | 1.0 - 4.0 |
| **Total** | **47** | **35** | **1.0 - 4.0** |

## Individual Test Scripts

For app-specific testing, you can also use the individual test scripts:

```bash
# Calculator tasks
python scripts/test_single_calculator_task.py --task CalculatorOpen

# Snapseed tasks
python scripts/test_single_snapseed_task.py --task SnapseedTask1

# Wikipedia tasks
python scripts/test_single_wikipedia_task.py --task WikipediaOpen
```

## Task Complexity Guide

- **1.0 - 1.5**: Simple tasks (open app, basic input)
- **2.0 - 2.5**: Moderate tasks (formulas, settings, filters)
- **3.0**: Complex tasks (multi-step operations, statistical calculations)
- **4.0+**: Advanced tasks (multiple settings, feed customization)

## Common Patterns

### Formula Input Tasks
Many Calculator tasks verify that the correct formula is displayed in the formula field.

### Settings Tasks
Snapseed and Wikipedia tasks often modify app settings stored in SharedPreferences XML files.

### Combined Tasks
Some tasks require multiple steps:
1. Configure a setting
2. Perform an action (e.g., apply filter)
3. Verify both conditions are met

## Testing Best Practices

1. **Start Simple**: Test basic tasks (complexity 1.0-1.5) first
2. **Verify Setup**: Ensure apps are installed and accessible
3. **Check Logs**: Review task execution logs for debugging
4. **Test Incrementally**: Test individual tasks before running full suites
5. **Monitor API Usage**: GPT-4 API calls can be expensive for large test suites

## Troubleshooting

### Task Not Found
- Verify the task is registered in `android_world/registry.py`
- Check that the task name matches exactly (case-sensitive)
- Use `--app all` to see all available tasks

### App Not Opening
- Verify the app is installed: `adb shell pm list packages | grep <package_name>`
- Check app package name matches the implementation
- Ensure emulator is running and accessible

### Settings Not Persisting
- Some settings only appear in XML after being explicitly set
- Default values may not be stored in SharedPreferences
- Check file permissions and root access if needed

## Related Files

- **Task Implementations**: `android_world/task_evals/single/{calculator,snapseed,wikipedia}.py`
- **Test Files**: `android_world/task_evals/single/{calculator,snapseed,wikipedia}_test.py`
- **Registry**: `android_world/registry.py`
- **Test Scripts**: `scripts/test_all_bmoca_tasks.py`, `scripts/test_single_*_task.py`

## Additional Resources

- [AndroidWorld Documentation](../../README.md)
- [Task Evaluation Framework](../../android_world/task_evals/README.md)
- [M3A Agent Documentation](../../android_world/agents/README.md)

