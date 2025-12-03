# Wikipedia App Tasks Documentation

## Overview

The Wikipedia app tasks test navigation and customization features of the Wikipedia mobile app. Tasks include basic navigation, text size adjustments, and feed customization settings.

**Package Name**: `org.wikipedia`  
**Total Available Tasks**: 5 (many tasks are commented out in registry)  
**Complexity Range**: 1.0 - 4.0

## Task List

### Basic Navigation

#### WikipediaOpen
- **Complexity**: 1.0
- **Description**: Open the Wikipedia app
- **Goal**: "Open Wikipedia."
- **Success Criteria**: Wikipedia app is open (detected by package name)

#### WikipediaGoToSearchTab
- **Complexity**: 1.5
- **Description**: Navigate to the search tab in Wikipedia
- **Goal**: "Go to search tab in Wikipedia."
- **Success Criteria**: Search tab is selected (`org.wikipedia:id/nav_tab_search`)

#### WikipediaGoToSavedTab
- **Complexity**: 1.5
- **Description**: Navigate to the saved/reading lists tab in Wikipedia
- **Goal**: "Go to saved tab in Wikipedia."
- **Success Criteria**: Saved tab is selected (`org.wikipedia:id/nav_tab_reading_lists`)

### Text Size Customization

#### WikipediaIncreaseTextSize180
- **Complexity**: 3.0
- **Description**: Increase text size to 180% in Wikipedia
- **Goal**: "Increase the text size to 180% in Wikipedia."
- **Success Criteria**: Text size multiplier is set to "8" in preferences (180% = value 8)
- **Note**: Text size multiplier only appears in XML after being explicitly set

### Feed Customization

#### WikipediaDisablePreviewAndFeed
- **Complexity**: 4.0
- **Description**: Disable 'show link previews' and 'top read' feed settings, then return to feed
- **Goal**: "Disable the 'show link previews', 'top read' feed settings, and return to the feed on Wikipedia."
- **Success Criteria**: 
  - `showLinkPreviews` is set to `false`
  - Feed state shows 'top read' (index 1) disabled: `[true,false,true,true,true,true,true,true,true,true]`
  - User is in the feed tab (`org.wikipedia:id/nav_tab_explore`)

## Currently Disabled Tasks

The following tasks are implemented but commented out in the registry (not available for testing):

- `WikipediaDecreaseTextSize50` - Decrease text size to 50%
- `WikipediaDisableFeaturedArticleFeed` - Disable featured article feed
- `WikipediaDisableTop2Topics` - Disable top 2 topics
- `WikipediaDisableTop1AndRandomizer` - Disable top 1 and randomizer topics
- `WikipediaDisableTop2AndRandomizer` - Disable top 2 and randomizer topics
- `WikipediaDisableHistoryTopics` - Disable history-related topics
- `WikipediaDisableDayTopics` - Disable topics with 'day' in name
- `WikipediaDisableEvenIndices` - Disable topics with even-numbered indices
- `WikipediaDisableOddIndices` - Disable topics with odd-numbered indices
- `WikipediaDisablePrimeIndices` - Disable topics with prime-numbered indices
- `WikipediaDisableFeedAndTextSize50` - Combined: disable feed and set text size to 50%
- `WikipediaDisableFeedAndTextSize180` - Combined: disable feed and set text size to 180%

## Testing

To test Wikipedia tasks, use the unified test script:

```bash
# List all Wikipedia tasks
python scripts/test_all_bmoca_tasks.py --app wikipedia

# Test a specific task
python scripts/test_all_bmoca_tasks.py --app wikipedia --task WikipediaOpen

# Test text size task
python scripts/test_all_bmoca_tasks.py --app wikipedia --task WikipediaIncreaseTextSize180
```

## Implementation Details

### Helper Functions

- **`_check_wikipedia_open(state)`**: Checks if Wikipedia app is open by looking for package name
- **`_check_tab_selected(state, resource_id)`**: Checks if a specific tab is selected (checks both resource_id and resource_name)
- **`_get_text_size_multiplier(env)`**: Reads preferences XML to get text size multiplier value
- **`_get_feed_state(env)`**: Reads preferences XML to get feed customization state (JSON-like array)
- **`_get_show_link_previews(env)`**: Reads preferences XML to get show link previews setting
- **`_read_preferences_xml(env)`**: Reads and parses Wikipedia preferences XML file

### Preferences File

- **Path**: `/data/data/org.wikipedia/shared_prefs/org.wikipedia_preferences.xml`
- **Text Size**: `<int name="textSizeMultiplier" value="8"/>` (only exists after being set)
- **Show Link Previews**: `<boolean name="showLinkPreviews" value="false"/>`
- **Feed State**: Stored in last element's text as JSON-like array: `[true,false,true,...]`

### Resource IDs

- Search tab: `org.wikipedia:id/nav_tab_search`
- Saved tab: `org.wikipedia:id/nav_tab_reading_lists`
- Explore/Feed tab: `org.wikipedia:id/nav_tab_explore`

### Text Size Multiplier Values

- **Default (100%)**: Value 0 (or not present in XML)
- **50%**: Value -5
- **180%**: Value 8

## Notes

- Android SharedPreferences only store values that have been explicitly set
- Default values (like text size = 0) don't appear in XML until changed
- Feed state is stored as a JSON-like array string in the last XML element
- Tab selection is checked by both `resource_id` and `resource_name` for compatibility
- Many feed customization tasks are implemented but disabled in the registry
- Combined tasks require multiple settings to be configured and user to return to feed tab

