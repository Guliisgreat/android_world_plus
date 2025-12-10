# Copyright 2025 The android_world Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tasks for Pi Music Player app.

Database schema verified on device 2025-11-29:
- Pi Music SQLite: songinfodatabase (local_music_store, pi_playlist, playlist_song)
- MediaStore: content://media/external/audio/media (for artist/album metadata)
- UI-based: playback operations (play, pause, seek)
"""

import abc
import dataclasses
import os
import random
import re
from typing import Any, Optional

from absl import logging
from android_world.env import adb_utils
from android_world.env import device_constants
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.utils import sqlite_schema_utils
from android_world.task_evals.utils import sqlite_utils
from android_world.task_evals.utils import user_data_generation
from android_world.utils import file_utils
from android_world.utils import fuzzy_match_lib


_APP_NAME = 'pi music player'
_PACKAGE_NAME = 'com.Project100Pi.themusicplayer'

# =============================================================================
# DATABASE CONFIGURATION (Verified on device 2025-11-29)
# =============================================================================
# Pi Music Player uses a single SQLite database for app-specific data:
_DB_PATH = f'/data/data/{_PACKAGE_NAME}/databases/songinfodatabase'

# Table names (verified)
_SONGS_TABLE = 'local_music_store'  # _id, song_name, duration, file_size
_SONG_INFO_TABLE = 'pi_song_info'   # Extended: is_favourite, play_count, album_name
_PLAYLISTS_TABLE = 'pi_playlist'    # _id, playlist_name, created_date, modified_date
_PLAYLIST_SONGS_TABLE = 'playlist_song'  # playlist_id, song_id, song_name, song_duration

# MediaStore URI for song metadata (artist, album - not in Pi Music DB)
_MEDIASTORE_URI = 'content://media/external/audio/media'


# =============================================================================
# SQLite Row Types (matching actual database schema)
# =============================================================================
@dataclasses.dataclass(frozen=True)
class SongRow(sqlite_schema_utils.SQLiteRow):
    """Represents a song in local_music_store table."""
    _id: Optional[int] = None
    song_name: str = ''
    duration: int = 0  # milliseconds
    file_size: int = 0


@dataclasses.dataclass(frozen=True)
class SongInfoRow(sqlite_schema_utils.SQLiteRow):
    """Represents extended song info in pi_song_info table."""
    _id: Optional[int] = None
    song_name: str = ''
    album_name: str = ''
    play_count: int = 0
    lastplayed_timestamp: int = 0
    duration: int = 0
    is_favourite: int = 0


@dataclasses.dataclass(frozen=True)
class PlaylistRow(sqlite_schema_utils.SQLiteRow):
    """Represents a playlist in pi_playlist table."""
    _id: Optional[int] = None
    android_playlist_id: int = -1
    playlist_name: str = ''
    created_date: int = 0
    modified_date: int = 0
    is_migrated: int = 1


@dataclasses.dataclass(frozen=True)
class PlaylistSongRow(sqlite_schema_utils.SQLiteRow):
    """Represents a song in playlist_song table."""
    _id: Optional[int] = None
    playlist_id: int = 0
    song_id: int = 0
    song_name: str = ''
    song_duration: int = 0
    date_added: int = 0
    album_name: str = ''


@dataclasses.dataclass(frozen=True)
class MediaStoreSong:
    """Represents a song from Android MediaStore (not SQLiteRow)."""
    _id: int = 0
    title: str = ''
    artist: str = ''
    album: str = ''
    duration: int = 0
    file_path: str = ''


# =============================================================================
# DEFAULT SONGS - 10 songs that are always injected during initialization
# =============================================================================
_DEFAULT_SONGS = [
    # (title, artist, album, duration_ms)
    # Pink Floyd songs (6 songs)
    ('Wish You Were Here', 'Pink Floyd', 'Wish You Were Here', 334000),
    ('Comfortably Numb', 'Pink Floyd', 'The Wall', 382000),
    ('Time', 'Pink Floyd', 'The Dark Side of the Moon', 413000),
    ('Money', 'Pink Floyd', 'The Dark Side of the Moon', 382000),
    ('Shine On You Crazy Diamond', 'Pink Floyd', 'Wish You Were Here', 810000),
    ('Another Brick in the Wall', 'Pink Floyd', 'The Wall', 239000),
    # Eason Chan songs (3 songs)
    ('Amigo', 'Eason Chan', 'U87', 268000),
    ('Ten Years', 'Eason Chan', 'Special Thanks To', 205000),
    ('Erta Ale', 'Eason Chan', 'The Key', 284000),
    # Sonny Boy song (1 song)
    ('Lightship', 'Sonny Boy', 'Sonny Boy OST', 245000),
]

# =============================================================================
# DEFAULT PLAYLISTS - 2 playlists created during initialization
# =============================================================================
_DEFAULT_PLAYLISTS = {
    'Favorite': [
        'Wish You Were Here',
        'Comfortably Numb',
        'Time',
        'Amigo',
        'Lightship',
    ],
    'Rock Classics': [
        'Money',
        'Shine On You Crazy Diamond',
        'Another Brick in the Wall',
        'Ten Years',
        'Erta Ale',
    ],
}

# =============================================================================
# NEW NAMES - Used ONLY for add/create operations (not in defaults)
# =============================================================================
_NEW_PLAYLIST_NAMES = [
    'Creepy',
    'Workout Mix',
    'Study Time',
    'Road Trip',
    'Chill Vibes',
]

_DEFAULT_ARTISTS = ['Pink Floyd', 'Eason Chan', 'Sonny Boy']


# =============================================================================
# Pi Music SQLite Helper Functions
# =============================================================================
def _get_all_playlists(env: interface.AsyncEnv) -> list[PlaylistRow]:
    """Get all playlists from pi_playlist table."""
    try:
        with env.controller.pull_file(_DB_PATH, timeout_sec=3) as local_db_dir:
            local_db_path = file_utils.convert_to_posix_path(
                local_db_dir, os.path.split(_DB_PATH)[1]
            )
            return sqlite_utils.execute_query(
                f'SELECT * FROM {_PLAYLISTS_TABLE};',
                local_db_path,
                PlaylistRow,
            )
    except Exception as e:
        logging.warning('Failed to get playlists: %s', e)
        return []


def _get_songs_from_local_store(env: interface.AsyncEnv) -> list[SongRow]:
    """Get all songs from local_music_store table."""
    try:
        with env.controller.pull_file(_DB_PATH, timeout_sec=3) as local_db_dir:
            local_db_path = file_utils.convert_to_posix_path(
                local_db_dir, os.path.split(_DB_PATH)[1]
            )
            return sqlite_utils.execute_query(
                f'SELECT * FROM {_SONGS_TABLE};',
                local_db_path,
                SongRow,
            )
    except Exception as e:
        logging.warning('Failed to get songs from local_music_store: %s', e)
        return []


def _get_songs_count(env: interface.AsyncEnv) -> int:
    """Get total number of songs from local_music_store."""
    songs = _get_songs_from_local_store(env)
    if songs:
        count = len(songs)
        logging.info('Got song count from database: %d songs', count)
        return count
    # Fallback only if database query fails
    fallback_count = len(_DEFAULT_SONGS)
    logging.warning('Database query failed, using fallback count: %d', fallback_count)
    return fallback_count


def _get_sorted_song_names(env: interface.AsyncEnv) -> list[str]:
    """Get song names sorted alphabetically from local_music_store."""
    songs = _get_songs_from_local_store(env)
    if songs:
        return sorted([s.song_name for s in songs])
    # Fallback to default songs
    return sorted([s[0] for s in _DEFAULT_SONGS])


def _playlist_exists(env: interface.AsyncEnv, playlist_name: str) -> bool:
    """Check if a playlist exists in pi_playlist table."""
    playlists = _get_all_playlists(env)
    return any(p.playlist_name == playlist_name for p in playlists)


def _clear_playlist_db(env: interface.AsyncEnv) -> None:
    """Clear all playlist data."""
    try:
        sqlite_utils.delete_all_rows_from_table(
            _PLAYLISTS_TABLE, _DB_PATH, env, _APP_NAME
        )
        sqlite_utils.delete_all_rows_from_table(
            _PLAYLIST_SONGS_TABLE, _DB_PATH, env, _APP_NAME
        )
    except Exception as e:
        logging.warning('Failed to clear playlist DB: %s', e)


# =============================================================================
# MediaStore Helper Functions (for artist/album metadata)
# =============================================================================
def _query_mediastore(env: interface.AsyncEnv) -> list[MediaStoreSong]:
    """Query MediaStore for all audio files with metadata."""
    try:
        result = adb_utils.issue_generic_request(
            ['shell', 'content', 'query', '--uri', _MEDIASTORE_URI],
            env.controller,
        )
        if not result or not result.generic.output:
            return []
        
        output = result.generic.output.decode('utf-8', errors='ignore')
        songs = []
        
        # Parse MediaStore output (Row: N field=value, field=value, ...)
        for line in output.split('\n'):
            if not line.startswith('Row:'):
                continue
            
            song = MediaStoreSong()
            # Extract fields using regex
            title_match = re.search(r'title=([^,]+)', line)
            artist_match = re.search(r'(?<!\w)artist=([^,]+)', line)
            album_match = re.search(r'(?<!\w)album=([^,]+)', line)
            duration_match = re.search(r'duration=(\d+)', line)
            id_match = re.search(r'_id=(\d+)', line)
            
            songs.append(MediaStoreSong(
                _id=int(id_match.group(1)) if id_match else 0,
                title=title_match.group(1).strip() if title_match else '',
                artist=artist_match.group(1).strip() if artist_match else '',
                album=album_match.group(1).strip() if album_match else '',
                duration=int(duration_match.group(1)) if duration_match else 0,
            ))
        
        return songs
    except Exception as e:
        logging.warning('Failed to query MediaStore: %s', e)
        return []


def _get_songs_by_artist(env: interface.AsyncEnv, artist: str) -> list[MediaStoreSong]:
    """Get songs by artist from MediaStore."""
    all_songs = _query_mediastore(env)
    return [s for s in all_songs if s.artist.lower() == artist.lower()]


def _get_song_by_title(env: interface.AsyncEnv, title: str) -> Optional[MediaStoreSong]:
    """Get a song by title from MediaStore."""
    all_songs = _query_mediastore(env)
    for song in all_songs:
        if song.title.lower() == title.lower():
            return song
    return None


# =============================================================================
# UI Helper Functions (fallback when DB access fails)
# =============================================================================
def _get_current_activity(env: interface.AsyncEnv) -> str:
    """Gets the current foreground activity."""
    try:
        return env.foreground_activity_name
    except Exception:
        return ''


def _check_ui_for_text(env: interface.AsyncEnv, text: str) -> bool:
    """Check if specific text appears in the current UI elements."""
    try:
        state = env.get_state(wait_to_stabilize=True)
        text_lower = text.lower()
        for element in state.ui_elements:
            element_text = (element.text or '').lower()
            content_desc = (element.content_description or '').lower()
            if text_lower in element_text or text_lower in content_desc:
                return True
    except Exception as e:
        logging.warning('Failed to check UI for text: %s', e)
    return False


def _check_ui_for_time_progress(env: interface.AsyncEnv) -> bool:
    """Check if time progress indicator (e.g., '1:16', '0:30') is visible.
    
    This indicates the now-playing screen is showing playback progress.
    """
    import re
    time_pattern = re.compile(r'^\d{1,2}:\d{2}$')  # Matches "1:16", "0:30", "12:45", etc.
    try:
        state = env.get_state(wait_to_stabilize=True)
        for element in state.ui_elements:
            element_text = (element.text or '').strip()
            if time_pattern.match(element_text):
                logging.info('Found time progress indicator: %s', element_text)
                return True
    except Exception as e:
        logging.warning('Failed to check UI for time progress: %s', e)
    return False


# =============================================================================
# SharedPreferences-based Playback State Functions
# =============================================================================
_PREFS_PATH = f'/data/data/{_PACKAGE_NAME}/shared_prefs/{_PACKAGE_NAME}_preferences.xml'


def _get_playback_state(env: interface.AsyncEnv) -> dict[str, Any]:
    """Get current playback state from SharedPreferences.
    
    Returns dict with:
        - 'state': 'STATE_STARTED' (playing), 'STATE_PAUSED', etc.
        - 'curr_pos': int, current position in nowPlayingList
        - 'now_playing_list': list of song IDs (as strings)
        - 'current_song_id': str, the current song ID or None
    """
    result = {
        'state': None,
        'curr_pos': None,
        'now_playing_list': [],
        'current_song_id': None,
    }
    
    try:
        # Read SharedPreferences XML
        response = adb_utils.issue_generic_request(
            ['shell', 'su', '0', 'cat', _PREFS_PATH],
            env.controller,
        )
        if not response or not response.generic.output:
            logging.warning('Failed to read Pi Music SharedPreferences')
            return result
        
        prefs_content = response.generic.output.decode('utf-8', errors='ignore')
        
        # Parse last_media_player_state
        state_match = re.search(r'name="last_media_player_state">([^<]+)<', prefs_content)
        if state_match:
            result['state'] = state_match.group(1)
        
        # Parse currPlayPos
        pos_match = re.search(r'name="currPlayPos" value="(\d+)"', prefs_content)
        if pos_match:
            result['curr_pos'] = int(pos_match.group(1))
        
        # Parse nowPlayingList (separator is ‚‗‚)
        list_match = re.search(r'name="nowPlayingList">([^<]+)<', prefs_content)
        if list_match:
            raw_list = list_match.group(1)
            # Split by the special separator ‚‗‚
            result['now_playing_list'] = raw_list.split('‚‗‚')
        
        # Get current song ID
        if result['curr_pos'] is not None and result['now_playing_list']:
            if 0 <= result['curr_pos'] < len(result['now_playing_list']):
                result['current_song_id'] = result['now_playing_list'][result['curr_pos']]
        
        logging.info('Playback state: state=%s, pos=%s, current_song_id=%s',
                     result['state'], result['curr_pos'], result['current_song_id'])
        
    except Exception as e:
        logging.warning('Failed to get playback state: %s', e)
    
    return result


def _get_song_info_from_mediastore(env: interface.AsyncEnv, song_id: str) -> dict[str, str]:
    """Query MediaStore to get song title and artist by ID.
    
    Returns dict with 'title' and 'artist', or empty strings if not found.
    """
    result = {'title': '', 'artist': ''}
    
    try:
        # content query --uri content://media/external/audio/media/<id> --projection title:artist
        response = adb_utils.issue_generic_request(
            ['shell', 'content', 'query', '--uri',
             f'content://media/external/audio/media/{song_id}',
             '--projection', 'title:artist'],
            env.controller,
        )
        
        if not response or not response.generic.output:
            return result
        
        output = response.generic.output.decode('utf-8', errors='ignore')
        
        if 'Row:' in output:
            # Parse: Row: 0 title=Lightship, artist=Sonny Boy
            title_match = re.search(r'title=([^,]+)', output)
            artist_match = re.search(r'artist=([^,\n]+)', output)
            
            if title_match:
                result['title'] = title_match.group(1).strip()
            if artist_match:
                result['artist'] = artist_match.group(1).strip()
            
            logging.info('MediaStore song %s: title="%s", artist="%s"',
                         song_id, result['title'], result['artist'])
    
    except Exception as e:
        logging.warning('Failed to query MediaStore for song %s: %s', song_id, e)
    
    return result


def _get_currently_playing_song(env: interface.AsyncEnv) -> dict[str, Any]:
    """Get the currently playing song info.
    
    Returns dict with:
        - 'is_playing': bool, True if STATE_STARTED
        - 'title': str, song title
        - 'artist': str, artist name
        - 'song_id': str, MediaStore song ID
    """
    result = {
        'is_playing': False,
        'title': '',
        'artist': '',
        'song_id': None,
    }
    
    # Step 1: Get playback state from SharedPreferences
    playback_state = _get_playback_state(env)
    
    result['is_playing'] = (playback_state['state'] == 'STATE_STARTED')
    result['song_id'] = playback_state['current_song_id']
    
    # Step 2: If we have a song ID, query MediaStore for title/artist
    if result['song_id']:
        song_info = _get_song_info_from_mediastore(env, result['song_id'])
        result['title'] = song_info['title']
        result['artist'] = song_info['artist']
    
    logging.info('Currently playing: is_playing=%s, title="%s", artist="%s"',
                 result['is_playing'], result['title'], result['artist'])
    
    return result


def _check_app_in_foreground(env: interface.AsyncEnv) -> bool:
    """Check if Pi Music Player is in the foreground."""
    activity = _get_current_activity(env)
    return _PACKAGE_NAME in activity


def _format_duration(ms: int) -> str:
    """Format milliseconds to MM:SS or HH:MM:SS format."""
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    if hours > 0:
        return f'{hours}:{minutes:02d}:{seconds:02d}'
    return f'{minutes}:{seconds:02d}'


# =============================================================================
# File Injection Functions
# =============================================================================
def _scan_music_directory(env: interface.AsyncEnv) -> None:
    """Scans the music directory to update the media store."""
    action = 'android.intent.action.MEDIA_SCANNER_SCAN_FILE'
    data_uri = 'file:///storage/emulated/0/Music'
    adb_utils.send_android_intent(
        command='broadcast', action=action, env=env.controller, data_uri=data_uri
    )


def _inject_default_songs(env: interface.AsyncEnv) -> None:
    """Inject all default songs to the device."""
    for title, artist, album, duration_ms in _DEFAULT_SONGS:
        file_name = f'{title.replace(" ", "_").replace(".", "")}.mp3'
        remote_path = file_utils.convert_to_posix_path(
            device_constants.MUSIC_DATA, file_name
        )
        user_data_generation.write_mp3_file_to_device(
            remote_path,
            env,
            title=title,
            artist=artist,
            duration_milliseconds=duration_ms,
        )


def _clear_music_data(env: interface.AsyncEnv) -> None:
    """Clear all music files from the device."""
    user_data_generation.clear_internal_storage(env)


# =============================================================================
# Base Classes
# =============================================================================
class _PiMusicBase(task_eval.TaskEval):
    """Base class for Pi Music Player tasks.
    
    Music files are pre-loaded in the AVD snapshot, so we just need to
    restore the app snapshot (handled by super().initialize_task()).
    """

    app_names = (_APP_NAME,)
    complexity = 1

    def initialize_task(self, env: interface.AsyncEnv) -> None:
        # Load app snapshot and return to home screen (same as Bluecoins/Maps.me)
        super().initialize_task(env)

    def tear_down(self, env: interface.AsyncEnv) -> None:
        super().tear_down(env)
        adb_utils.close_app(_PACKAGE_NAME, env.controller)


class _PiMusicQuery(_PiMusicBase, metaclass=abc.ABCMeta):
    """Base class for Pi Music Player query tasks."""

    complexity = 1

    @abc.abstractmethod
    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        """Returns the expected answer by querying the database."""

    def is_successful(self, env: interface.AsyncEnv) -> float:
        super().is_successful(env)
        expected = self._get_expected_answer(env).lower()
        response = getattr(env, 'interaction_cache', '') or ''
        response = response.lower()

        if not response:
            logging.warning('Agent did not provide an answer.')
            return 0.0

        # Strategy 1: Check if expected is contained in response (handles "You have 14 songs")
        if expected in response:
            logging.info('Found expected "%s" in response "%s"', expected, response)
            return 1.0
        
        # Strategy 2: For numeric answers, check with word boundaries
        if expected.isdigit():
            pattern = r'\b' + re.escape(expected) + r'\b'
            if re.search(pattern, response):
                logging.info('Found numeric expected "%s" in response "%s"', expected, response)
                return 1.0
        
        # Strategy 3: For duration formats like "13:30", also accept text formats
        # Handles: "13 minutes 30 seconds", "13 min 30 sec", "13m 30s", etc.
        duration_match = re.match(r'^(\d+):(\d+)$', expected)
        if duration_match:
            minutes = duration_match.group(1)
            seconds = duration_match.group(2).lstrip('0') or '0'  # Remove leading zero
            
            # Check various text formats
            duration_patterns = [
                rf'\b{minutes}\s*(?:minutes?|mins?|m)\b.*\b{seconds}\s*(?:seconds?|secs?|s)\b',
                rf'\b{minutes}\s*(?:minutes?|mins?|m)\s+(?:and\s+)?{seconds}\s*(?:seconds?|secs?|s)\b',
                rf'\b{minutes}:{seconds.zfill(2)}\b',  # Also check with leading zero
            ]
            for pattern in duration_patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    logging.info('Found duration "%s" in text format in response "%s"', expected, response)
                    return 1.0
        
        # Strategy 4: Fuzzy match as fallback
        if fuzzy_match_lib.fuzzy_match(response, expected):
            logging.info('Fuzzy match success for expected "%s" and response "%s"', expected, response)
            return 1.0
        
        logging.warning('Agent answer "%s" does not match expected "%s"', response, expected)
        return 0.0


class _PiMusicOperation(_PiMusicBase, metaclass=abc.ABCMeta):
    """Base class for Pi Music Player operation tasks."""

    complexity = 2
    
    # Store state before operation for comparison
    before_state: Any = None

    def initialize_task(self, env: interface.AsyncEnv) -> None:
        super().initialize_task(env)
        # Capture state before agent performs operation
        self.before_state = self._capture_state(env)

    def _capture_state(self, env: interface.AsyncEnv) -> Any:
        """Capture relevant state before operation. Override in subclasses."""
        return None

    def is_successful(self, env: interface.AsyncEnv) -> float:
        super().is_successful(env)
        return self._verify_operation(env)

    @abc.abstractmethod
    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """Verify if the operation was successful using database."""


# =============================================================================
# Query Tasks - Validated via SQLite or MediaStore
# =============================================================================
class PiMusicQueryTotalSongs(_PiMusicQuery):
    """Task to query the total number of songs.
    
    Validation: Pi Music SQLite (local_music_store table)
    """

    app_names = (_APP_NAME,)
    complexity = 1
    schema = {
        'type': 'object',
        'properties': {
            'total_songs': {'type': 'integer'},
        },
        'required': ['total_songs'],
    }
    template = 'In the Pi Music Player app, tell me how many songs do I have in total?'

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        # Query local_music_store table for actual count (not hardcoded)
        count = _get_songs_count(env)
        logging.info('PiMusicQueryTotalSongs: Expected answer from DB = %d', count)
        return str(count)

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {'total_songs': len(_DEFAULT_SONGS)}


class PiMusicQueryArtistSongCount(_PiMusicQuery):
    """Task to query how many songs by a specific artist.
    
    Validation: MediaStore (artist info not in Pi Music DB)
    """

    app_names = (_APP_NAME,)
    complexity = 1
    schema = {
        'type': 'object',
        'properties': {
            'artist': {'type': 'string'},
            'song_count': {'type': 'integer'},
        },
        'required': ['artist', 'song_count'],
    }
    template = "In the Pi Music Player app, help me check how many {artist}'s songs do I have?"

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        artist = self.params['artist']
        # Query MediaStore for songs by artist
        songs = _get_songs_by_artist(env, artist)
        if songs:
            return str(len(songs))
        # Fallback to expected from default songs
        count = sum(1 for s in _DEFAULT_SONGS if s[1] == artist)
        return str(count)

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        artist = 'Pink Floyd'
        count = sum(1 for s in _DEFAULT_SONGS if s[1] == artist)
        return {'artist': artist, 'song_count': count}


class PiMusicQuerySongAlbum(_PiMusicQuery):
    """Task to query the album name of a specific song.
    
    Validation: MediaStore (album info not in Pi Music DB)
    """

    app_names = (_APP_NAME,)
    complexity = 1
    schema = {
        'type': 'object',
        'properties': {
            'song_title': {'type': 'string'},
            'album_name': {'type': 'string'},
        },
        'required': ['song_title', 'album_name'],
    }
    template = 'In the Pi Music Player app, what is the album name of the song {song_title}?'

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        title = self.params['song_title']
        # Query MediaStore for song album
        song = _get_song_by_title(env, title)
        if song:
            return song.album
        return self.params['album_name']

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        song = _DEFAULT_SONGS[0]
        return {'song_title': song[0], 'album_name': song[2]}


class PiMusicQueryLongestSongDuration(_PiMusicQuery):
    """Task to query the duration of the longest song by an artist.
    
    Validation: MediaStore (artist info not in Pi Music DB)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'artist': {'type': 'string'},
            'duration_ms': {'type': 'integer'},
            'duration_formatted': {'type': 'string'},
        },
        'required': ['artist', 'duration_ms', 'duration_formatted'],
    }
    template = 'In the Pi Music Player app, what is the duration time of the longest song by {artist}?'

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        artist = self.params['artist']
        # Query MediaStore for songs by artist
        songs = _get_songs_by_artist(env, artist)
        if songs:
            longest = max(songs, key=lambda s: s.duration)
            return _format_duration(longest.duration)
        # Fallback to default songs
        artist_songs = [s for s in _DEFAULT_SONGS if s[1] == artist]
        if artist_songs:
            longest = max(artist_songs, key=lambda x: x[3])
            return _format_duration(longest[3])
        return self.params['duration_formatted']

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        artist = 'Pink Floyd'
        artist_songs = [s for s in _DEFAULT_SONGS if s[1] == artist]
        longest = max(artist_songs, key=lambda x: x[3])
        return {
            'artist': artist,
            'duration_ms': longest[3],
            'duration_formatted': _format_duration(longest[3]),
        }


class PiMusicQuerySortedSongsByTitle(_PiMusicQuery):
    """Task to sort songs by title and query specific positions.
    
    Validation: Pi Music SQLite (local_music_store.song_name)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'second_song': {'type': 'string'},
            'fourth_song': {'type': 'string'},
        },
        'required': ['second_song', 'fourth_song'],
    }
    template = 'In the Pi Music Player app, sort the songs by title in ascending order. What are the second and fourth songs?'

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        return f"{self.params['second_song']} and {self.params['fourth_song']}"

    def is_successful(self, env: interface.AsyncEnv) -> float:
        super().is_successful(env)
        response = (getattr(env, 'interaction_cache', '') or '').lower()
        
        # Get sorted song names from SQLite
        sorted_songs = _get_sorted_song_names(env)
        second = (sorted_songs[1] if len(sorted_songs) > 1 else '').lower()
        fourth = (sorted_songs[3] if len(sorted_songs) > 3 else '').lower()
        
        # Check if song names are contained in the response
        second_match = second and second in response
        fourth_match = fourth and fourth in response
        
        logging.info('Checking sorted songs: second="%s", fourth="%s" in response', second, fourth)
        
        if second_match and fourth_match:
            logging.info('Both songs found in response.')
            return 1.0
        elif second_match or fourth_match:
            logging.info('Only one song found: second=%s, fourth=%s', second_match, fourth_match)
            return 0.5
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        sorted_songs = sorted(_DEFAULT_SONGS, key=lambda x: x[0])
        second = sorted_songs[1][0] if len(sorted_songs) > 1 else ''
        fourth = sorted_songs[3][0] if len(sorted_songs) > 3 else ''
        return {'second_song': second, 'fourth_song': fourth}


class PiMusicQueryArtistTotalDuration(_PiMusicQuery):
    """Task to query total duration of all songs by an artist.
    
    Validation: MediaStore (artist info not in Pi Music DB)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'artist': {'type': 'string'},
            'total_duration_ms': {'type': 'integer'},
            'total_duration_formatted': {'type': 'string'},
        },
        'required': ['artist', 'total_duration_ms', 'total_duration_formatted'],
    }
    template = "In the Pi Music Player app, what is the total duration time of all of {artist}'s songs?"

    def _get_expected_answer(self, env: interface.AsyncEnv) -> str:
        artist = self.params['artist']
        # Query MediaStore for songs by artist
        songs = _get_songs_by_artist(env, artist)
        if songs:
            total_ms = sum(s.duration for s in songs)
            return _format_duration(total_ms)
        # Fallback to default songs
        artist_songs = [s for s in _DEFAULT_SONGS if s[1] == artist]
        total_ms = sum(s[3] for s in artist_songs)
        return _format_duration(total_ms)

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        artist = 'Eason Chan'
        artist_songs = [s for s in _DEFAULT_SONGS if s[1] == artist]
        total_ms = sum(s[3] for s in artist_songs)
        return {
            'artist': artist,
            'total_duration_ms': total_ms,
            'total_duration_formatted': _format_duration(total_ms),
        }


# =============================================================================
# Operation Tasks - Validated via SQLite or UI
# =============================================================================
class PiMusicPlayFromPlaylist(_PiMusicOperation):
    """Task to play the first song in a specific playlist.
    
    Validation: SharedPreferences (check last_media_player_state == STATE_STARTED)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'playlist_name': {'type': 'string'},
            'position': {'type': 'integer'},
        },
        'required': ['playlist_name', 'position'],
    }
    template = "In the Pi Music Player app, play the first song in '{playlist_name}' playlist."

    @property
    def goal(self) -> str:
        return f"In the Pi Music Player app, play the first song in '{self.params['playlist_name']}' playlist."

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """SharedPreferences validation: check if music is playing."""
        # Get playback state from SharedPreferences
        playback_state = _get_playback_state(env)
        
        if playback_state['state'] == 'STATE_STARTED':
            logging.info('Music is playing (STATE_STARTED).')
            return 1.0
        elif playback_state['state'] == 'STATE_PAUSED':
            # Song loaded but paused - partial success
            logging.info('Music is paused (STATE_PAUSED).')
            return 0.8
        elif playback_state['current_song_id']:
            # Song is in queue but state unclear
            logging.info('Song loaded but playback state unclear: %s', playback_state['state'])
            return 0.7
        
        # Fallback to UI check
        if _check_ui_for_text(env, 'pause'):
            return 1.0
        if _check_ui_for_text(env, 'playing') or _check_ui_for_text(env, 'now playing'):
            return 1.0
        activity = _get_current_activity(env)
        if 'player' in activity.lower() or 'playing' in activity.lower():
            return 0.8
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {'playlist_name': 'Favorite', 'position': 1}


class PiMusicSortByDurationDescending(_PiMusicOperation):
    """Task to sort an artist's songs by duration in descending order.
    
    Validation: UI-based (check for artist name and sort indicators)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'artist': {'type': 'string'},
        },
        'required': ['artist'],
    }
    template = "In the Pi Music Player app, sort {artist}'s songs by duration time in descending order."

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """UI-based validation: check for artist display and sort state."""
        # Check if viewing artist's songs
        if _check_ui_for_text(env, self.params['artist']):
            # Check for sort indicators
            if _check_ui_for_text(env, 'duration') or _check_ui_for_text(env, 'descending'):
                return 1.0
            return 0.8  # Artist visible but sort state unclear
        if _check_ui_for_text(env, 'sort'):
            return 0.5
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {'artist': 'Pink Floyd'}


class PiMusicCreatePlaylist(_PiMusicOperation):
    """Task to create a new playlist.
    
    Validation: Pi Music SQLite (pi_playlist table)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'playlist_name': {'type': 'string'},
        },
        'required': ['playlist_name'],
    }
    template = "In the Pi Music Player app, create a playlist named '{playlist_name}' for me."

    def _capture_state(self, env: interface.AsyncEnv) -> list[str]:
        """Capture existing playlist names before operation."""
        playlists = _get_all_playlists(env)
        return [p.playlist_name for p in playlists]

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """SQLite validation: check if playlist exists in pi_playlist table."""
        playlist_name = self.params['playlist_name']
        
        # Check SQLite database for new playlist
        if _playlist_exists(env, playlist_name):
            logging.info('Playlist "%s" found in pi_playlist table.', playlist_name)
            return 1.0
        
        # Fallback: check UI
        if _check_ui_for_text(env, playlist_name):
            logging.info('Playlist "%s" visible in UI (DB not updated yet).', playlist_name)
            return 0.8  # Partial credit if visible but not in DB
        
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        # Use NEW playlist name (not from defaults)
        return {'playlist_name': 'Creepy'}


class PiMusicPauseAndSeek(_PiMusicOperation):
    """Task to play a specific song, then pause and seek to a specific time.
    
    Validation: SharedPreferences (STATE_PAUSED + playerPosition) with UI fallback
    
    The task explicitly asks the agent to play a specific song first, ensuring
    there's something to pause and seek.
    """

    app_names = (_APP_NAME,)
    complexity = 2.5  # Increased: play + pause + seek
    schema = {
        'type': 'object',
        'properties': {
            'song_title': {'type': 'string'},
            'seek_minutes': {'type': 'integer'},
            'seek_seconds': {'type': 'integer'},
        },
        'required': ['song_title', 'seek_minutes', 'seek_seconds'],
    }
    template = "In the Pi Music Player app, play '{song_title}', then pause it and seek to {seek_minutes} minute and {seek_seconds} seconds."

    @property
    def goal(self) -> str:
        return f"In the Pi Music Player app, play '{self.params['song_title']}', then pause it and seek to {self.params['seek_minutes']} minute and {self.params['seek_seconds']} seconds."

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """SharedPreferences + UI validation: check for paused state and seek position."""
        expected_seek_ms = (self.params['seek_minutes'] * 60 + self.params['seek_seconds']) * 1000
        seek_time = f'{self.params["seek_minutes"]}:{self.params["seek_seconds"]:02d}'
        
        # Method 1: Check SharedPreferences for paused state
        playback_state = _get_playback_state(env)
        is_paused = playback_state['state'] == 'STATE_PAUSED'
        
        if is_paused:
            logging.info('Song is paused (STATE_PAUSED confirmed).')
            # Check seek position in UI (SharedPreferences playerPosition might have slight offset)
            if _check_ui_for_text(env, seek_time):
                logging.info('Seek position %s confirmed in UI.', seek_time)
                return 1.0
            # Paused but seek position not visible - still partial success
            logging.info('Paused but seek position %s not visible in UI.', seek_time)
            return 0.7
        
        # Method 2: Fallback to UI-based check
        if _check_ui_for_text(env, 'play'):
            logging.info('Play button visible (indicates paused state).')
            if _check_ui_for_text(env, seek_time):
                logging.info('Found paused state with seek position %s.', seek_time)
                return 1.0
            logging.info('Found paused state but seek position not visible.')
            return 0.5
        
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        # Use a long song to ensure seek time is valid
        # "Shine On You Crazy Diamond" is 13:30 (810 seconds) - the longest
        # Seek time: 1:27 (87 seconds) - safe for any song
        return {
            'song_title': 'Shine On You Crazy Diamond',
            'seek_minutes': 1,
            'seek_seconds': 27,
        }


class PiMusicPlaySongByTitleArtist(_PiMusicOperation):
    """Task to play a specific song by title and artist.
    
    Validation: SharedPreferences + MediaStore
    - Reads last_media_player_state, currPlayPos, nowPlayingList from SharedPreferences
    - Gets current song ID from nowPlayingList[currPlayPos]
    - Queries MediaStore for song title and artist
    - Verifies match with expected song
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {
            'song_title': {'type': 'string'},
            'artist': {'type': 'string'},
        },
        'required': ['song_title', 'artist'],
    }
    template = 'In the Pi Music Player app, play {song_title} by {artist}.'

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        """SharedPreferences + MediaStore validation for playback.
        
        Process:
        1. Read SharedPreferences: last_media_player_state, currPlayPos, nowPlayingList
        2. Get current song ID: nowPlayingList[currPlayPos]
        3. Query MediaStore: content://media/external/audio/media/<song_id>
        4. Compare title and artist with expected values
        """
        expected_title = self.params['song_title']
        expected_artist = self.params['artist']
        
        # Get currently playing song from SharedPreferences + MediaStore
        current_song = _get_currently_playing_song(env)
        
        actual_title = current_song['title']
        actual_artist = current_song['artist']
        is_playing = current_song['is_playing']
        
        logging.info('Validating: expected="%s" by "%s", actual="%s" by "%s", playing=%s',
                     expected_title, expected_artist, actual_title, actual_artist, is_playing)
        
        # Check if title and artist match (case-insensitive)
        title_match = expected_title.lower() == actual_title.lower()
        artist_match = expected_artist.lower() == actual_artist.lower()
        
        if title_match and artist_match:
            if is_playing:
                # Perfect: correct song is currently playing
                logging.info('SUCCESS: "%s" by "%s" is playing (STATE_STARTED).', actual_title, actual_artist)
                return 1.0
            else:
                # Correct song but paused/stopped - still success as task is to "play" the song
                logging.info('SUCCESS: "%s" by "%s" is loaded (state=%s).', 
                             actual_title, actual_artist, current_song.get('state', 'unknown'))
                return 1.0
        elif title_match:
            # Title matches but artist doesn't
            logging.info('PARTIAL: Title "%s" matches but artist "%s" != "%s".',
                         actual_title, actual_artist, expected_artist)
            return 0.7
        elif actual_title:
            # Different song is playing
            logging.info('FAIL: Wrong song playing: "%s" by "%s" instead of "%s" by "%s".',
                         actual_title, actual_artist, expected_title, expected_artist)
            return 0.0
        else:
            # Could not determine current song - fall back to UI check
            logging.info('Could not determine current song from SharedPreferences, falling back to UI.')
            if _check_ui_for_text(env, expected_title) and _check_ui_for_text(env, expected_artist):
                return 1.0
            elif _check_ui_for_text(env, expected_title):
                return 0.7
            return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {'song_title': 'Lightship', 'artist': 'Sonny Boy'}


class PiMusicSortByDurationAscending(_PiMusicOperation):
    """Task to sort all songs by duration in ascending order.
    
    Validation: UI-based (check for sort indicators)
    """

    app_names = (_APP_NAME,)
    complexity = 2
    schema = {
        'type': 'object',
        'properties': {},
        'required': [],
    }
    template = 'In the Pi Music Player app, sort the songs by duration time in ascending order.'

    def _verify_operation(self, env: interface.AsyncEnv) -> float:
        if _check_ui_for_text(env, 'duration') or _check_ui_for_text(env, 'ascending'):
            return 1.0
        if _check_ui_for_text(env, 'sort'):
            return 0.5
        return 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {}
