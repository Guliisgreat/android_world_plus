# App Onboarding Guide

This document describes how the 6 apps were onboarded into AndroidWorld, including app details, data setup, validation methods, and AVD configuration.

## Overview

| Category | App | Package | Tasks | Complexity | Validation |
|----------|-----|---------|-------|------------|------------|
| AndroidLab | Bluecoins | `com.rammigsoftware.bluecoins` | 15 | 2.0-4.0 | SQLite |
| AndroidLab | Maps.me | `com.mapswithme.maps.pro` | 15 | 2.0-3.5 | SQLite + UI |
| AndroidLab | Pi Music | `com.Project100Pi.themusicplayer` | 12 | 1.0-2.5 | SQLite + MediaStore + SharedPrefs |
| BMOCA | Calculator | `com.google.android.calculator` | 19 | 1.0-3.0 | UI |
| BMOCA | Snapseed | `com.niksoftware.snapseed` | 11 | 1.0-3.0 | UI + SharedPrefs |
| BMOCA | Wikipedia | `org.wikipedia` | 5 | 1.0-4.0 | UI + SharedPrefs |
| **Total** | | | **77** | **1.0-4.0** | |

---

## AVD Configuration

### AVD Details

| Property | Value |
|----------|-------|
| AVD Name | `AWAvd` |
| Snapshot Name | `apps_ready_dec2025` |
| Android Version | Android 14 (API 34) |
| Default Location | San Francisco Bay Area |
| Emulator Date | October 15, 2023 (framework default) |

### Starting the Emulator

```bash
export CONSOLE_PORT=5554
export GRPC_PORT=8554

emulator -avd AWAvd \
  -no-window \
  -no-audio \
  -skip-adb-auth \
  -no-boot-anim \
  -gpu auto \
  -grpc $GRPC_PORT \
  -port $CONSOLE_PORT \
  -snapshot apps_ready_dec2025 \
  -no-snapshot-save &

adb -s emulator-$CONSOLE_PORT wait-for-device
```

### Key Flags

| Flag | Purpose |
|------|---------|
| `-snapshot apps_ready_dec2025` | Load pre-configured snapshot with all apps ready |
| `-no-snapshot-save` | Prevent saving changes (keeps snapshot clean) |
| `-grpc` | gRPC port for AndroidWorld communication |
| `-port` | Console port (ADB uses this) |

---

## App-Specific Onboarding

### 1. Bluecoins (Finance)

**Data Storage**: SQLite (`bluecoins.fydb`)

#### Pre-loaded Data

| Date | Type | Amount | Notes |
|------|------|--------|-------|
| Oct 15, 2023 | Expense | 512 USD | Other category |
| Oct 15, 2023 | Expense | 888 USD | Other category |
| Oct 15, 2023 | Expense | 256 USD | Other category |
| Oct 15, 2023 | Expense | 768 USD | Other category |
| Oct 13, 2023 | Income | 15,000 USD | For edit tasks |
| Oct 14, 2023 | Income | 5,000 USD | For edit tasks |

#### Database Schema

| Field | Type | Description |
|-------|------|-------------|
| `amount` | INTEGER | Stored in micro-units (÷1,000,000 for USD) |
| `date` | TEXT | Format: `YYYY-MM-DD HH:MM:SS` |
| `transactionTypeID` | INTEGER | 3=Expense, 4=Income, 5=Transfer |
| `notes` | TEXT | Transaction notes |

#### Validation

- **Query tasks**: Compare agent answer with database values
- **Create tasks**: Count transactions before/after
- **Edit tasks**: Verify field changes in database

---

### 2. Maps.me (Navigation)

**Data Storage**: SQLite (`favorites`, `search-history`)

#### Default Setup

- Location: San Francisco Bay Area
- Sample destinations: Stanford, Berkeley, OpenAI, Golden Gate Bridge

#### Database Tables

| Database | Table | Purpose |
|----------|-------|---------|
| `favorites` | `Bookmark` | Saved places |
| `favorites` | `Category` | Bookmark categories (Work, Home) |
| `search-history` | `PlacesHistory` | Recently viewed places |
| `search-history` | `QueryHistory` | Search queries |

#### Validation

- **Route queries**: Check agent answer for distance/time units (km, min, hour)
- **Nearby places**: Verify via PlacesHistory table
- **Bookmarks**: Check Category + Bookmark tables
- **Navigation**: UI check for destination text AND navigation active

---

### 3. Pi Music Player (Music)

**Data Storage**: SQLite + MediaStore + SharedPreferences

#### Pre-loaded Songs (10)

| Title | Artist | Album | Duration |
|-------|--------|-------|----------|
| Wish You Were Here | Pink Floyd | Wish You Were Here | 5:34 |
| Comfortably Numb | Pink Floyd | The Wall | 6:22 |
| Time | Pink Floyd | The Dark Side of the Moon | 6:53 |
| Money | Pink Floyd | The Dark Side of the Moon | 6:22 |
| Shine On You Crazy Diamond | Pink Floyd | Wish You Were Here | 13:30 |
| Another Brick in the Wall | Pink Floyd | The Wall | 3:59 |
| Amigo | Eason Chan | U87 | 4:28 |
| Ten Years | Eason Chan | Special Thanks To | 3:25 |
| Erta Ale | Eason Chan | The Key | 4:44 |
| Lightship | Sonny Boy | Sonny Boy OST | 4:05 |

#### Pre-loaded Playlists (2)

| Playlist | Songs |
|----------|-------|
| Favorite | Wish You Were Here, Comfortably Numb, Time, Amigo, Lightship |
| Rock Classics | Money, Shine On You Crazy Diamond, Another Brick in the Wall, Ten Years, Erta Ale |

#### Data Paths

| Type | Path |
|------|------|
| SQLite | `/data/data/com.Project100Pi.themusicplayer/databases/songinfodatabase` |
| MediaStore | `content://media/external/audio/media` |
| SharedPrefs | `/data/data/com.Project100Pi.themusicplayer/shared_prefs/com.Project100Pi.themusicplayer_preferences.xml` |

#### Playback State (SharedPreferences)

| Field | Description |
|-------|-------------|
| `last_media_player_state` | `STATE_STARTED`, `STATE_PAUSED`, `STATE_STOPPED` |
| `currPlayPos` | Current position in play queue (0-indexed) |
| `nowPlayingList` | Song IDs separated by `‚‗‚` |

#### Validation

- **Song count/sort**: Pi Music SQLite
- **Artist/album queries**: MediaStore
- **Playback state**: SharedPreferences + MediaStore
- **Sort operations**: UI-based

---

### 4. Calculator (Math)

**Data Storage**: UI state only (no persistence)

#### Validation Method

Check formula/result display via UI accessibility tree:

| Resource ID | Purpose |
|-------------|---------|
| `com.google.android.calculator:id/formula` | Formula display |
| `com.google.android.calculator:id/result_preview` | Result preview |
| `com.google.android.calculator:id/result_final` | Final result |

#### Special Notations

| Input | Display |
|-------|---------|
| cos(60) | `c60` |
| ln(1234) | `l1234` |
| 3×5 | `3×5` (multiplication sign) |
| 24÷3 | `24÷3` (division sign) |

---

### 5. Snapseed (Photo Editing)

**Data Storage**: SharedPreferences (`Preferences.xml`)

#### Preferences Path

```
/data/data/com.niksoftware.snapseed/shared_prefs/Preferences.xml
```

#### Settings Fields

| Setting | Preference Key | Example Value |
|---------|----------------|---------------|
| Dark theme | `pref_appearance_use_dark_theme` | `true` |
| Format quality | `pref_export_setting_compression` | `100` |
| Image sizing | `pref_export_setting_long_edge` | `2000` |

#### Validation

- **Navigation**: UI check for `logo_view`, `looks_button`, `tools_button`
- **Filter applied**: UI check for filter name selected
- **Settings**: Read SharedPreferences XML

---

### 6. Wikipedia (Knowledge)

**Data Storage**: SharedPreferences

#### Preferences Path

```
/data/data/org.wikipedia/shared_prefs/org.wikipedia_preferences.xml
```

#### Settings Fields

| Setting | Preference Key | Example |
|---------|----------------|---------|
| Text size | `textSizeMultiplier` | `8` (180%) |
| Link previews | `showLinkPreviews` | `false` |
| Feed state | (last element) | `[true,false,true,...]` |

#### Text Size Values

| Percentage | Value |
|------------|-------|
| 50% | -5 |
| 100% (default) | 0 |
| 180% | 8 |

#### Validation

- **Tab navigation**: Check selected tab resource ID
- **Settings**: Read SharedPreferences XML

---

## Saving App Snapshots

Each app has its own snapshot for clean state restoration:

```bash
# Save snapshots for AndroidLab apps
python app_content_lg.py --console=5554 --grpc=8554 save --package=bluecoins
python app_content_lg.py --console=5554 --grpc=8554 save --package=maps.me
python app_content_lg.py --console=5554 --grpc=8554 save --package=pimusic

# Save snapshots for BMOCA apps
python app_content_lg.py --console=5554 --grpc=8554 save --package=calculator
python app_content_lg.py --console=5554 --grpc=8554 save --package=snapseed
python app_content_lg.py --console=5554 --grpc=8554 save --package=wikipedia
```

## Task Initialization Flow

```
1. Load AVD snapshot (apps_ready_dec2025)
2. Restore app-specific snapshot (via app_content_lg.py)
3. Generate random task parameters
4. Execute task with agent
5. Validate success via appropriate method
6. Restore snapshot for next task (no state leakage)
```

## Validation Methods Summary

| Method | Used By | How |
|--------|---------|-----|
| **SQLite** | Bluecoins, Maps.me, Pi Music | Query database tables |
| **MediaStore** | Pi Music | Query Android media provider |
| **SharedPreferences** | Pi Music, Snapseed, Wikipedia | Parse XML preferences file |
| **UI State** | Calculator, Snapseed, Wikipedia, Maps.me | Check accessibility tree |

## Related Files

| File | Purpose |
|------|---------|
| `android_world/task_evals/single/*.py` | Task implementations |
| `android_world/registry.py` | Task registration |
| `scripts/test_androidlab_apps.py` | AndroidLab test runner |
| `scripts/test_all_bmoca_tasks.py` | BMOCA test runner |
| `app_content_lg.py` | Snapshot save/restore tool |

