# Pi Music Player App Tasks Documentation

## Overview

The Pi Music Player app tasks test music player operations including song queries, playlist management, playback control, and sorting operations. The app uses both its own SQLite database and Android's MediaStore for song metadata.

**Package Name**: `com.Project100Pi.themusicplayer`  
**Total Tasks**: 12  
**Complexity Range**: 1.0 - 2.0

## Default Data Setup

### Songs (10 songs)

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

### Playlists (2 default playlists)

| Playlist | Songs |
|----------|-------|
| Favorite | Wish You Were Here, Comfortably Numb, Time, Amigo, Lightship |
| Rock Classics | Money, Shine On You Crazy Diamond, Another Brick in the Wall, Ten Years, Erta Ale |

## Task List

### Query Tasks (6)

#### PiMusicQueryTotalSongs
- **Complexity**: 1.0
- **Description**: Query total number of songs
- **Goal**: "In the Pi Music Player app, tell me how many songs do I have in total?"
- **Success Criteria**: Agent provides correct count (10)
- **Validation**: Pi Music SQLite (`local_music_store` table)

#### PiMusicQueryArtistSongCount
- **Complexity**: 1.0
- **Description**: Query number of songs by a specific artist
- **Goal**: "In the Pi Music Player app, help me check how many {artist}'s songs do I have?"
- **Success Criteria**: Agent provides correct artist song count
- **Validation**: MediaStore (artist info not in Pi Music DB)

#### PiMusicQuerySongAlbum
- **Complexity**: 1.0
- **Description**: Query the album name of a specific song
- **Goal**: "In the Pi Music Player app, what is the album name of the song {song_title}?"
- **Success Criteria**: Agent provides correct album name
- **Validation**: MediaStore

#### PiMusicQueryLongestSongDuration
- **Complexity**: 2.0
- **Description**: Query duration of the longest song by an artist
- **Goal**: "In the Pi Music Player app, what is the duration time of the longest song by {artist}?"
- **Success Criteria**: Agent provides correct duration (e.g., "13:30" for Pink Floyd)
- **Validation**: MediaStore

#### PiMusicQuerySortedSongsByTitle
- **Complexity**: 2.0
- **Description**: Sort songs and identify specific positions
- **Goal**: "In the Pi Music Player app, sort the songs by title in ascending order. What are the second and fourth songs?"
- **Success Criteria**: Agent correctly identifies both songs
- **Validation**: Pi Music SQLite (`local_music_store.song_name`)

#### PiMusicQueryArtistTotalDuration
- **Complexity**: 2.0
- **Description**: Query total duration of all songs by an artist
- **Goal**: "In the Pi Music Player app, what is the total duration time of all of {artist}'s songs?"
- **Success Criteria**: Agent provides correct total duration
- **Validation**: MediaStore

### Operation Tasks (6)

#### PiMusicPlayFromPlaylist
- **Complexity**: 2.0
- **Description**: Play the first song in a specific playlist
- **Goal**: "In the Pi Music Player app, play the first song in '{playlist_name}' playlist."
- **Success Criteria**: `last_media_player_state == "STATE_STARTED"` in SharedPreferences
- **Validation**: SharedPreferences (with UI fallback)

#### PiMusicSortByDurationDescending
- **Complexity**: 2.0
- **Description**: Sort an artist's songs by duration (descending)
- **Goal**: "In the Pi Music Player app, sort {artist}'s songs by duration time in descending order."
- **Success Criteria**: Artist visible + sort indicators in UI
- **Validation**: UI-based

#### PiMusicCreatePlaylist
- **Complexity**: 2.0
- **Description**: Create a new playlist
- **Goal**: "In the Pi Music Player app, create a playlist named '{playlist_name}' for me."
- **Success Criteria**: New playlist found in `pi_playlist` SQLite table
- **Validation**: Pi Music SQLite

#### PiMusicPauseAndSeek
- **Complexity**: 2.5
- **Description**: Play a specific song, pause it, and seek to a specific time
- **Goal**: "In the Pi Music Player app, play '{song_title}', then pause it and seek to {seek_minutes} minute and {seek_seconds} seconds."
- **Default Song**: "Shine On You Crazy Diamond" (13:30) - ensures seek time is valid
- **Default Seek**: 1:27
- **Success Criteria**: `last_media_player_state == "STATE_PAUSED"` + seek time visible in UI
- **Validation**: SharedPreferences + UI (with UI fallback)

#### PiMusicPlaySongByTitleArtist
- **Complexity**: 2.0
- **Description**: Play a specific song by title and artist
- **Goal**: "In the Pi Music Player app, play {song_title} by {artist}."
- **Success Criteria**: Correct song playing (verified via SharedPreferences + MediaStore)
- **Validation**: SharedPreferences + MediaStore (see validation process below)

#### PiMusicSortByDurationAscending
- **Complexity**: 2.0
- **Description**: Sort all songs by duration (ascending)
- **Goal**: "In the Pi Music Player app, sort the songs by duration time in ascending order."
- **Success Criteria**: Duration or ascending sort indicator visible
- **Validation**: UI-based

## Testing

To test Pi Music Player tasks, use the test script:

```bash
# Test a specific task
python scripts/test_androidlab_apps.py --app pimusic --task PiMusicQueryTotalSongs

# Test with custom emulator ports
python scripts/test_androidlab_apps.py --app pimusic --task PiMusicCreatePlaylist --console_port 5706 --grpc_port 8556
```

## Implementation Details

### Database Configuration

- **Database Path**: `/data/data/com.Project100Pi.themusicplayer/databases/songinfodatabase`
- **MediaStore URI**: `content://media/external/audio/media`
- **SharedPreferences Path**: `/data/data/com.Project100Pi.themusicplayer/shared_prefs/com.Project100Pi.themusicplayer_preferences.xml`

### SQLite Tables

| Table | Description |
|-------|-------------|
| `local_music_store` | Song metadata (_id, song_name, duration, file_size) |
| `pi_song_info` | Extended info (is_favourite, play_count, album_name, lastplayed_timestamp) |
| `pi_playlist` | Playlist metadata |
| `playlist_song` | Songs in playlists |

### SharedPreferences Fields (Playback State)

| Field | Type | Description |
|-------|------|-------------|
| `last_media_player_state` | String | Playback state: `STATE_STARTED`, `STATE_PAUSED`, `STATE_STOPPED` |
| `currPlayPos` | Integer | Current position in `nowPlayingList` (0-indexed) |
| `nowPlayingList` | String | Song IDs separated by `‚‗‚` (special delimiter) |
| `playerPosition` | Integer | Current playback position in milliseconds |
| `is_player_stopped_by_user` | Boolean | Whether user manually stopped playback |

### Validation Methods

| Task Type | Validation Method |
|-----------|-------------------|
| Query (song count, sorted) | Pi Music SQLite |
| Query (artist, album, duration) | MediaStore |
| Operation (create playlist) | Pi Music SQLite |
| Operation (play song) | SharedPreferences + MediaStore |
| Operation (pause/seek) | SharedPreferences + UI |
| Operation (sort) | UI-based |

### Playback Validation Process

For tasks like `PiMusicPlaySongByTitleArtist` and `PiMusicPlayFromPlaylist`, the validation uses SharedPreferences + MediaStore to reliably verify playback state:

#### Step 1: Read SharedPreferences
```
Path: /data/data/com.Project100Pi.themusicplayer/shared_prefs/com.Project100Pi.themusicplayer_preferences.xml
```

Extract:
| Field | Example | Meaning |
|-------|---------|---------|
| `last_media_player_state` | `STATE_STARTED` | `STATE_STARTED` = playing, `STATE_PAUSED` = paused |
| `currPlayPos` | `4` | Current position in play queue (0-indexed) |
| `nowPlayingList` | `1000000060‚‗‚1000000059‚‗‚...` | Song IDs separated by `‚‗‚` |

#### Step 2: Get Current Song ID
```
current_song_id = nowPlayingList[currPlayPos]
```

#### Step 3: Query MediaStore
```bash
content query --uri content://media/external/audio/media/<song_id> --projection title:artist
```

Returns: `title=Lightship, artist=Sonny Boy`

#### Step 4: Verify Match
Compare actual title/artist with expected values.

#### Validation Diagram
```
┌─────────────────────────────────────────────────────────────────┐
│ SharedPreferences XML                                           │
├─────────────────────────────────────────────────────────────────┤
│ last_media_player_state = "STATE_STARTED"  ← Is it playing?    │
│ currPlayPos = 4                             ← Queue position    │
│ nowPlayingList = "...‚‗‚1000000063‚‗‚..."  ← Song IDs          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    nowPlayingList[4] = 1000000063
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ MediaStore Query                                                │
│ content://media/external/audio/media/1000000063                │
├─────────────────────────────────────────────────────────────────┤
│ title = "Lightship"                                            │
│ artist = "Sonny Boy"                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              Compare with expected: ✅ Match → Score 1.0
```

### Helper Functions

#### SQLite/MediaStore Functions
- `_get_songs_count(env)`: Get total songs from `local_music_store`
- `_get_sorted_song_names(env)`: Get alphabetically sorted song names
- `_playlist_exists(env, name)`: Check if playlist exists in `pi_playlist`
- `_query_mediastore(env)`: Query Android MediaStore for song metadata

#### Playback State Functions
- `_get_playback_state(env)`: Read SharedPreferences for `last_media_player_state`, `currPlayPos`, `nowPlayingList`
- `_get_song_info_from_mediastore(env, song_id)`: Query MediaStore for title/artist by song ID
- `_get_currently_playing_song(env)`: Combined function returning `is_playing`, `title`, `artist`, `song_id`

#### UI Functions
- `_check_ui_for_text(env, text)`: Check if text appears in current UI
- `_get_current_activity(env)`: Get current foreground activity name

## Notes

- Song files are injected during task initialization
- Default songs include Pink Floyd (6), Eason Chan (3), and Sonny Boy (1)
- Two default playlists are created: "Favorite" and "Rock Classics"
- New playlist names for create tasks use names NOT in defaults (e.g., "Creepy")
- Duration is formatted as MM:SS or HH:MM:SS
- MediaStore is used for artist/album metadata (not stored in Pi Music DB)

