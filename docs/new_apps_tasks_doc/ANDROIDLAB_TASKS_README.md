# AndroidLab Tasks Documentation

## Overview

This directory contains documentation for all AndroidLab app tasks implemented in AndroidWorld. These tasks test three mobile apps from the AndroidLab benchmark: Bluecoins (finance), Maps.me (navigation), and Pi Music Player (music).

## Quick Start

### Test All Tasks

Use the unified test script to test tasks from any AndroidLab app:

```bash
# List all available tasks for an app
python scripts/test_androidlab_apps.py --app bluecoins
python scripts/test_androidlab_apps.py --app maps.me
python scripts/test_androidlab_apps.py --app pimusic

# Test a specific task
python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsQuerySpendingOnDate
python scripts/test_androidlab_apps.py --app maps.me --task MapsMeNavigateToStanford
python scripts/test_androidlab_apps.py --app pimusic --task PiMusicQueryTotalSongs

# Run ALL tasks for an app
python scripts/test_androidlab_apps.py --app bluecoins --run_all
python scripts/test_androidlab_apps.py --app maps.me --run_all
python scripts/test_androidlab_apps.py --app pimusic --run_all
python scripts/test_androidlab_apps.py --app all --run_all  # Run all 42 tasks

# Test with custom emulator ports
python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsAddExpense --console_port 5706 --grpc_port 8556
```

The `--run_all` flag runs all tasks sequentially and provides a summary at the end with:
- Success/failure counts and success rate
- Per-task results with scores and step counts
- Error messages for any failed tasks

### Requirements

- **OpenAI API Key**: Set `OPENAI_API_KEY` environment variable
- **Emulator**: Running Android emulator (default ports: console=5706, grpc=8556)
- **Apps Installed**: Bluecoins, Maps.me, and Pi Music Player must be installed on the emulator
- **App Snapshots**: Run `app_content_lg.py save` to save initial app states

## App Documentation

### [Bluecoins Tasks](./ANDROIDLAB_TASKS_BLUECOINS.md)
- **Package**: `com.rammigsoftware.bluecoins`
- **Total Tasks**: 15
- **Complexity Range**: 2.0 - 4.0
- **Categories**: Query (5), Create (5), Edit (5)
- **Validation**: SQLite database (`bluecoins.fydb`)

### [Maps.me Tasks](./ANDROIDLAB_TASKS_MAPSME.md)
- **Package**: `com.mapswithme.maps.pro`
- **Total Tasks**: 15
- **Complexity Range**: 2.0 - 3.5
- **Categories**: Route queries (5), Nearby places (4), Bookmarks (1), Navigation (5)
- **Validation**: SQLite + UI-based

### [Pi Music Player Tasks](./ANDROIDLAB_TASKS_PIMUSIC.md)
- **Package**: `com.Project100Pi.themusicplayer`
- **Total Tasks**: 12
- **Complexity Range**: 1.0 - 2.0
- **Categories**: Query (6), Operation (6)
- **Validation**: SQLite + MediaStore + UI-based

## Task Statistics

| App | Total Tasks | Complexity Range | Validation |
|-----|-------------|------------------|------------|
| Bluecoins | 15 | 2.0 - 4.0 | SQLite |
| Maps.me | 15 | 2.0 - 3.5 | SQLite + UI |
| Pi Music | 12 | 1.0 - 2.0 | SQLite + MediaStore + UI |
| **Total** | **42** | **1.0 - 4.0** | |

## Task Complexity Guide

- **1.0 - 1.5**: Simple queries (e.g., count songs)
- **2.0 - 2.5**: Standard operations (e.g., add expense, navigate, play song)
- **3.0 - 3.5**: Multi-step operations (e.g., add with note/label, compare routes)
- **4.0+**: Complex edits (e.g., change type + amount + note)

## Validation Methods

### SQLite Validation
- **Bluecoins**: `bluecoins.fydb` database
- **Maps.me**: `favorites` and `search-history` databases
- **Pi Music**: `songinfodatabase`

### MediaStore Validation
- Used for Pi Music artist/album metadata
- Queries `content://media/external/audio/media`

### UI-Based Validation
- Navigation: Check for destination text AND navigation indicators
- Playback: Check for pause button or "now playing" text
- Sort: Check for sort indicators

## Data Setup

### Bluecoins (October 2023)
- **Oct 15**: 4 expenses: 512, 888, 256, 768 USD (category: Other)
- **Oct 13**: 1 income: 15,000 USD (for edit tasks)
- **Oct 14**: 1 income: 5,000 USD (for edit tasks)
- **Dec 9**: 1 income: 5,000 USD (for edit tasks)

### Pi Music Player
- 10 songs (6 Pink Floyd, 3 Eason Chan, 1 Sonny Boy)
- 2 playlists: "Favorite" and "Rock Classics"

### Maps.me
- Default location: San Francisco Bay Area
- Sample destinations: Stanford, Berkeley, OpenAI

## Saving App Snapshots

Before running tests, save app snapshots:

```bash
# Save snapshots for all AndroidLab apps
python app_content_lg.py --console=5706 --grpc=8556 save --package=bluecoins
python app_content_lg.py --console=5706 --grpc=8556 save --package=maps.me
python app_content_lg.py --console=5706 --grpc=8556 save --package=pimusic
```

## Troubleshooting

### OpenAI API Errors
- **Rate limit**: Wait or upgrade API tier
- **Quota exceeded**: Check billing at https://platform.openai.com/account/billing

### Task Not Found
- Verify task is registered in `android_world/registry.py`
- Check exact task name (case-sensitive)

### App Not Opening
- Verify app is installed: `adb shell pm list packages | grep <package>`
- Check package name in `adb_utils.py` `_PATTERN_TO_ACTIVITY` mapping

### SQLite Validation Fails
- Check snapshot was restored correctly
- Verify database path and table names
- Some fields may have different default values

### Navigation Validation Fails
- Both conditions must be met: destination visible AND navigation active
- Check if agent launched correct app (Maps.me, not Google Maps)

## Related Files

- **Task Implementations**: `android_world/task_evals/single/{bluecoins,maps_me,pimusic}.py`
- **Test Files**: `android_world/task_evals/single/{bluecoins,maps_me,pimusic}_test.py`
- **Registry**: `android_world/registry.py`
- **Test Script**: `scripts/test_androidlab_apps.py`
- **Snapshot Tool**: `app_content_lg.py`

## Additional Resources

- [AndroidWorld Documentation](../README.md)
- [BMOCA Tasks Documentation](./BMOCA_TASKS_README.md)
- [Task Evaluation Framework](../android_world/task_evals/README.md)

