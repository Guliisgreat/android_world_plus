# Snapseed App Tasks Documentation

## Overview

The Snapseed app tasks test photo editing operations using the Google Snapseed app. Tasks range from basic app navigation to applying filters and configuring export settings.

**Package Name**: `com.niksoftware.snapseed`  
**Total Tasks**: 11  
**Complexity Range**: 1.0 - 3.0

## Task List

### Basic Navigation

#### SnapseedTask1
- **Complexity**: 1.0
- **Description**: Open the Snapseed app app
- **Goal**: "Open the Snapseed app"
- **Success Criteria**: Snapseed main screen is open (detected by logo_view element)

#### SnapseedTask2
- **Complexity**: 1.5
- **Description**: Open an image in the Snapseed app
- **Goal**: "Open image in the Snapseed app"
- **Success Criteria**: Image is loaded and looks_button is selected

#### SnapseedTask5
- **Complexity**: 1.5
- **Description**: Open an image and navigate to tools tab
- **Goal**: "Open image and go to tools tab in the Snapseed app"
- **Success Criteria**: Image is open AND tools tab is active (tools_button is selected)

### Filter Application

#### SnapseedTask3
- **Complexity**: 2.0
- **Description**: Open an image and apply the "Pop" filter
- **Goal**: "Open image and apply noir Pop filter in the Snapseed app"
- **Success Criteria**: Image is open AND "Pop" filter is selected

#### SnapseedTask4
- **Complexity**: 2.0
- **Description**: Open an image and apply the "Portrait" filter
- **Goal**: "Open image and apply portrait filter in the Snapseed app"
- **Success Criteria**: Image is open AND "Portrait" filter is selected

### Settings Configuration

#### SnapseedTask6
- **Complexity**: 2.0
- **Description**: Enable dark theme in the Snapseed app
- **Goal**: "Set dark theme in the Snapseed app"
- **Success Criteria**: Dark theme preference is enabled in Preferences.xml (`pref_appearance_use_dark_theme` = true)

#### SnapseedTask7
- **Complexity**: 2.0
- **Description**: Set export format quality to JPG 100%
- **Goal**: "Set format quality to JPG 100% in the Snapseed app"
- **Success Criteria**: Format quality preference is set to "100" (`pref_export_setting_compression` = "100")

#### SnapseedTask8
- **Complexity**: 2.0
- **Description**: Set image sizing to 2000 pixels
- **Goal**: "Set image sizing to 2000 px in the Snapseed app"
- **Success Criteria**: Image sizing preference is set to "2000" (`pref_export_setting_long_edge` = "2000")

### Combined Tasks

#### SnapseedTask9
- **Complexity**: 3.0
- **Description**: Apply "Pop" filter after enabling dark theme
- **Goal**: "Apply noir Pop filter to an image after setting dark theme in the Snapseed app"
- **Success Criteria**: Dark theme is enabled AND "Pop" filter is applied to an image

#### SnapseedTask10
- **Complexity**: 3.0
- **Description**: Apply "Pop" filter after setting format quality to 100%
- **Goal**: "Apply noir Pop filter to an image after setting format quality to JPG 100% in the Snapseed app"
- **Success Criteria**: Format quality is "100" AND "Pop" filter is applied

#### SnapseedTask11
- **Complexity**: 3.0
- **Description**: Apply "Pop" filter after setting image sizing to 2000px
- **Goal**: "Apply noir Pop filter to an image after setting image sizing to 2000 px in the Snapseed app"
- **Success Criteria**: Image sizing is "2000" AND "Pop" filter is applied

## Testing

To test Snapseed tasks, use the unified test script:

```bash
# List all Snapseed tasks
python scripts/test_all_bmoca_tasks.py --app snapseed

# Test a specific task
python scripts/test_all_bmoca_tasks.py --app snapseed --task SnapseedTask1

# Test a complex task
python scripts/test_all_bmoca_tasks.py --app snapseed --task SnapseedTask9
```

## Implementation Details

### Helper Functions

- **`check_snapseed_open(state)`**: Checks if Snapseed main screen is open by looking for `tap_to_open_hint` element
- **`check_image_open(state)`**: Checks if an image is loaded by verifying `looks_button` is selected
- **`check_tools_tab(state)`**: Checks if tools tab is active by verifying `tools_button` is selected
- **`check_filter_selected(state, filter_name)`**: Checks if a specific filter is selected by matching text
- **`check_dark_theme(env)`**: Reads Preferences.xml to check if dark theme is enabled
- **`check_format_quality(env)`**: Reads Preferences.xml to get format quality setting
- **`check_image_sizing(env)`**: Reads Preferences.xml to get image sizing setting

### Preferences File

- **Path**: `/data/data/com.niksoftware.snapseed/shared_prefs/Preferences.xml`
- **Dark Theme**: `<boolean name="pref_appearance_use_dark_theme" value="true"/>`
- **Format Quality**: `<string name="pref_export_setting_compression">100</string>`
- **Image Sizing**: `<string name="pref_export_setting_long_edge">2000</string>`

### Resource IDs

- Logo view: `com.niksoftware.snapseed:id/tap_to_open_hint`
- Looks button: `com.niksoftware.snapseed:id/looks_button`
- Tools button: `com.niksoftware.snapseed:id/tools_button`

## Notes

- Snapseed must have images available in the gallery to open
- Filter names are case-sensitive (e.g., "Pop", "Portrait")
- Settings are persisted in SharedPreferences XML file
- Combined tasks require multiple steps to be completed in sequence
- Some tasks require an image to be open before applying filters

