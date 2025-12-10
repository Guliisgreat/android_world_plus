# Wikipedia M3A Agent Results

## Summary

| Metric | Value |
|--------|-------|
| App | Wikipedia |
| Total Tasks | 5 |
| Successful | 2 |
| Failed | 3 |
| Success Rate | 40.0% |

## Results by Task

| Task | Status | Score | Steps | Complexity |
|------|--------|-------|-------|------------|
| WikipediaOpen | ✅ Pass | 1.00 | 2/10 | 1.0 |
| WikipediaGoToSearchTab | ❌ Fail | 0.00 | 15/15 | 1.5 |
| WikipediaGoToSavedTab | ✅ Pass | 1.00 | 13/15 | 1.5 |
| WikipediaIncreaseTextSize180 | ❌ Fail | 0.00 | 30/30 | 3.0 |
| WikipediaDisablePreviewAndFeed | ❌ Fail | 0.00 | 40/40 | 4.0 |

## Detailed Results

### Task 1: WikipediaOpen ✅
- **Goal**: Open the Wikipedia app.
- **Complexity**: 1.0
- **Steps**: 2/10
- **Result**: Agent successfully opened the Wikipedia app.

### Task 2: WikipediaGoToSearchTab ❌
- **Goal**: In the Wikipedia app, go to the search tab.
- **Complexity**: 1.5
- **Steps**: 15/15 (max steps reached)
- **Result**: Agent did not complete the task within the step limit.

### Task 3: WikipediaGoToSavedTab ✅
- **Goal**: In the Wikipedia app, go to the saved tab.
- **Complexity**: 1.5
- **Steps**: 13/15
- **Result**: Agent successfully navigated to the saved tab.

### Task 4: WikipediaIncreaseTextSize180 ❌
- **Goal**: In the Wikipedia app, increase the text size to 180%.
- **Complexity**: 3.0
- **Steps**: 30/30 (max steps reached)
- **Result**: Agent did not complete the task within the step limit.

### Task 5: WikipediaDisablePreviewAndFeed ❌
- **Goal**: In the Wikipedia app, disable the 'show link previews', 'top read' feed settings, and return to the feed.
- **Complexity**: 4.0
- **Steps**: 40/40 (max steps reached)
- **Result**: Agent did not complete the task within the step limit.

## Failure Analysis

| Failure Type | Count | Tasks |
|--------------|-------|-------|
| Max steps reached | 3 | WikipediaGoToSearchTab, WikipediaIncreaseTextSize180, WikipediaDisablePreviewAndFeed |

**Observations**:
- All failures were due to the agent reaching the maximum step limit without completing the task
- Higher complexity tasks (3.0-4.0) were more likely to fail
- Simple navigation tasks had mixed results (search tab failed, saved tab succeeded)

## Command Used

```bash
python scripts/test_all_bmoca_tasks.py --app wikipedia --run_all --console_port 5706 --grpc_port 8556
```

