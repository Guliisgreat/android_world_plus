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

"""Tests for Pi Music Player task evaluations."""

from unittest import mock

from absl.testing import absltest
from android_world.task_evals.single import pimusic


# ============================================================================
# Tests for is_successful() Validation
# ============================================================================


class PiMusicQueryTotalSongsValidationTest(absltest.TestCase):
  """Tests for PiMusicQueryTotalSongs is_successful() validation.
  
  Validation method: Pi Music SQLite (local_music_store table)
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_get_songs_count')
  def test_correct_count_full_score(self, mock_get_songs):
    """Test full score when agent reports correct song count."""
    mock_get_songs.return_value = 10
    # Agent response must contain the expected answer "10"
    self.mock_env.interaction_cache = '10'

    params = {'total_songs': 10}
    task = pimusic.PiMusicQueryTotalSongs(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(pimusic, '_get_songs_count')
  def test_wrong_count_zero_score(self, mock_get_songs):
    """Test zero score when agent reports wrong count."""
    mock_get_songs.return_value = 10
    self.mock_env.interaction_cache = '5'

    params = {'total_songs': 10}
    task = pimusic.PiMusicQueryTotalSongs(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.0)


class PiMusicQueryArtistSongCountValidationTest(absltest.TestCase):
  """Tests for PiMusicQueryArtistSongCount is_successful() validation.
  
  Validation method: MediaStore query
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_get_songs_by_artist')
  def test_correct_artist_count(self, mock_get_songs):
    """Test full score when agent reports correct artist song count."""
    mock_get_songs.return_value = [
        pimusic.MediaStoreSong(_id=1, title='Song1', artist='Pink Floyd'),
        pimusic.MediaStoreSong(_id=2, title='Song2', artist='Pink Floyd'),
        pimusic.MediaStoreSong(_id=3, title='Song3', artist='Pink Floyd'),
        pimusic.MediaStoreSong(_id=4, title='Song4', artist='Pink Floyd'),
        pimusic.MediaStoreSong(_id=5, title='Song5', artist='Pink Floyd'),
        pimusic.MediaStoreSong(_id=6, title='Song6', artist='Pink Floyd'),
    ]
    # Agent response must contain "6"
    self.mock_env.interaction_cache = '6'

    params = {'artist': 'Pink Floyd', 'song_count': 6}
    task = pimusic.PiMusicQueryArtistSongCount(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


class PiMusicCreatePlaylistValidationTest(absltest.TestCase):
  """Tests for PiMusicCreatePlaylist is_successful() validation.
  
  Validation method: Pi Music SQLite (pi_playlist table)
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_playlist_exists')
  def test_playlist_created_success(self, mock_playlist_exists):
    """Test full score when playlist exists in SQLite database."""
    mock_playlist_exists.return_value = True

    params = {'playlist_name': 'Creepy'}
    task = pimusic.PiMusicCreatePlaylist(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(pimusic, '_playlist_exists')
  @mock.patch.object(pimusic, '_check_ui_for_text')
  def test_playlist_not_created(self, mock_check_ui, mock_playlist_exists):
    """Test zero score when playlist not in DB and not in UI."""
    mock_playlist_exists.return_value = False
    mock_check_ui.return_value = False

    params = {'playlist_name': 'Creepy'}
    task = pimusic.PiMusicCreatePlaylist(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.0)


class PiMusicPlayFromPlaylistValidationTest(absltest.TestCase):
  """Tests for PiMusicPlayFromPlaylist is_successful() validation.
  
  Validation method: UI-based (check for pause button)
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_check_ui_for_text')
  @mock.patch.object(pimusic, '_get_current_activity')
  def test_pause_button_visible(self, mock_activity, mock_check_ui):
    """Test full score when pause button visible (song playing)."""
    mock_check_ui.side_effect = lambda env, text: text == 'pause'
    mock_activity.return_value = 'SomeActivity'

    params = {'playlist_name': 'Favorite', 'position': 1}
    task = pimusic.PiMusicPlayFromPlaylist(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


class PiMusicPauseAndSeekValidationTest(absltest.TestCase):
  """Tests for PiMusicPauseAndSeek is_successful() validation.
  
  Validation method: UI-based (check for play button and seek position)
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_check_ui_for_text')
  def test_paused_with_correct_seek(self, mock_check_ui):
    """Test full score when paused at correct seek position."""
    def check_text(env, text):
      return text in ['play', '1:27']
    mock_check_ui.side_effect = check_text

    params = {'seek_minutes': 1, 'seek_seconds': 27}
    task = pimusic.PiMusicPauseAndSeek(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


class PiMusicPlaySongByTitleArtistValidationTest(absltest.TestCase):
  """Tests for PiMusicPlaySongByTitleArtist is_successful() validation.
  
  Validation method: UI-based (check for song title and playback state)
  """

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(pimusic, '_check_ui_for_text')
  def test_song_playing(self, mock_check_ui):
    """Test full score when correct song is playing."""
    def check_text(env, text):
      return text in ['Lightship', 'pause']
    mock_check_ui.side_effect = check_text

    params = {'song_title': 'Lightship', 'artist': 'Sonny Boy'}
    task = pimusic.PiMusicPlaySongByTitleArtist(params)
    task.initialized = True

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


# ============================================================================
# Tests for Default Configuration
# ============================================================================


class DefaultSongsTest(absltest.TestCase):
    """Tests for the default songs configuration."""

    def test_default_songs_count(self):
        """Verify we have exactly 10 default songs."""
        self.assertEqual(len(pimusic._DEFAULT_SONGS), 10)

    def test_default_songs_structure(self):
        """Verify each song has (title, artist, album, duration_ms)."""
        for song in pimusic._DEFAULT_SONGS:
            self.assertEqual(len(song), 4)
            self.assertIsInstance(song[0], str)  # title
            self.assertIsInstance(song[1], str)  # artist
            self.assertIsInstance(song[2], str)  # album
            self.assertIsInstance(song[3], int)  # duration_ms

    def test_pink_floyd_songs_count(self):
        """Verify Pink Floyd has 6 songs."""
        count = sum(1 for s in pimusic._DEFAULT_SONGS if s[1] == 'Pink Floyd')
        self.assertEqual(count, 6)

    def test_eason_chan_songs_count(self):
        """Verify Eason Chan has 3 songs."""
        count = sum(1 for s in pimusic._DEFAULT_SONGS if s[1] == 'Eason Chan')
        self.assertEqual(count, 3)

    def test_sonny_boy_songs_count(self):
        """Verify Sonny Boy has 1 song."""
        count = sum(1 for s in pimusic._DEFAULT_SONGS if s[1] == 'Sonny Boy')
        self.assertEqual(count, 1)


class DefaultPlaylistsTest(absltest.TestCase):
    """Tests for the default playlists configuration."""

    def test_default_playlists_count(self):
        """Verify we have exactly 2 default playlists."""
        self.assertEqual(len(pimusic._DEFAULT_PLAYLISTS), 2)

    def test_favorite_playlist_exists(self):
        """Verify 'Favorite' playlist exists."""
        self.assertIn('Favorite', pimusic._DEFAULT_PLAYLISTS)

    def test_rock_classics_playlist_exists(self):
        """Verify 'Rock Classics' playlist exists."""
        self.assertIn('Rock Classics', pimusic._DEFAULT_PLAYLISTS)

    def test_each_playlist_has_5_songs(self):
        """Verify each playlist has 5 songs."""
        for playlist_name, songs in pimusic._DEFAULT_PLAYLISTS.items():
            self.assertEqual(len(songs), 5, f'{playlist_name} should have 5 songs')


class NewNamesTest(absltest.TestCase):
    """Tests for new song/playlist names used in add operations."""

    def test_new_playlist_names_not_in_defaults(self):
        """Verify new playlist names don't overlap with defaults."""
        for name in pimusic._NEW_PLAYLIST_NAMES:
            self.assertNotIn(name, pimusic._DEFAULT_PLAYLISTS)


class SQLiteRowTypesTest(absltest.TestCase):
    """Tests for SQLite row dataclasses."""

    def test_song_row_creation(self):
        """Test SongRow dataclass creation (local_music_store table)."""
        song = pimusic.SongRow(
            _id=1,
            song_name='Test Song',
            duration=300000,
            file_size=1024000
        )
        self.assertEqual(song.song_name, 'Test Song')
        self.assertEqual(song.duration, 300000)

    def test_playlist_row_creation(self):
        """Test PlaylistRow dataclass creation (pi_playlist table)."""
        playlist = pimusic.PlaylistRow(
            _id=1,
            playlist_name='My Playlist',
            created_date=1234567890
        )
        self.assertEqual(playlist.playlist_name, 'My Playlist')

    def test_mediastore_song_creation(self):
        """Test MediaStoreSong dataclass creation."""
        song = pimusic.MediaStoreSong(
            _id=1,
            title='Test Song',
            artist='Test Artist',
            album='Test Album',
            duration=300000
        )
        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(song.artist, 'Test Artist')
        self.assertEqual(song.album, 'Test Album')


class FormatDurationTest(absltest.TestCase):
    """Tests for the _format_duration helper function."""

    def test_format_duration_minutes_seconds(self):
        # 5 minutes 30 seconds = 330000 ms
        self.assertEqual(pimusic._format_duration(330000), '5:30')

    def test_format_duration_with_hours(self):
        # 1 hour 5 minutes 30 seconds = 3930000 ms
        self.assertEqual(pimusic._format_duration(3930000), '1:05:30')

    def test_format_duration_zero(self):
        self.assertEqual(pimusic._format_duration(0), '0:00')

    def test_format_duration_short(self):
        # 45 seconds = 45000 ms
        self.assertEqual(pimusic._format_duration(45000), '0:45')

    def test_format_duration_exact_minute(self):
        # 3 minutes = 180000 ms
        self.assertEqual(pimusic._format_duration(180000), '3:00')


class PiMusicQueryTotalSongsTest(absltest.TestCase):
    """Tests for PiMusicQueryTotalSongs task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQueryTotalSongs.generate_random_params()
        self.assertIn('total_songs', params)
        self.assertEqual(params['total_songs'], 10)

    def test_template(self):
        task = pimusic.PiMusicQueryTotalSongs(params={'total_songs': 10})
        self.assertEqual(task.template, 'In Pi Music Player, tell me how many songs do I have in total?')


class PiMusicQueryArtistSongCountTest(absltest.TestCase):
    """Tests for PiMusicQueryArtistSongCount task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQueryArtistSongCount.generate_random_params()
        self.assertIn('artist', params)
        self.assertIn('song_count', params)
        self.assertEqual(params['artist'], 'Pink Floyd')
        self.assertEqual(params['song_count'], 6)


class PiMusicQuerySongAlbumTest(absltest.TestCase):
    """Tests for PiMusicQuerySongAlbum task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQuerySongAlbum.generate_random_params()
        self.assertIn('song_title', params)
        self.assertIn('album_name', params)
        self.assertEqual(params['song_title'], 'Wish You Were Here')
        self.assertEqual(params['album_name'], 'Wish You Were Here')


class PiMusicQueryLongestSongDurationTest(absltest.TestCase):
    """Tests for PiMusicQueryLongestSongDuration task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQueryLongestSongDuration.generate_random_params()
        self.assertIn('artist', params)
        self.assertIn('duration_ms', params)
        self.assertIn('duration_formatted', params)
        self.assertEqual(params['artist'], 'Pink Floyd')
        self.assertEqual(params['duration_ms'], 810000)
        self.assertEqual(params['duration_formatted'], '13:30')


class PiMusicQuerySortedSongsByTitleTest(absltest.TestCase):
    """Tests for PiMusicQuerySortedSongsByTitle task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQuerySortedSongsByTitle.generate_random_params()
        self.assertIn('second_song', params)
        self.assertIn('fourth_song', params)
        self.assertIsInstance(params['second_song'], str)
        self.assertIsInstance(params['fourth_song'], str)


class PiMusicQueryArtistTotalDurationTest(absltest.TestCase):
    """Tests for PiMusicQueryArtistTotalDuration task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicQueryArtistTotalDuration.generate_random_params()
        self.assertIn('artist', params)
        self.assertIn('total_duration_ms', params)
        self.assertIn('total_duration_formatted', params)
        self.assertEqual(params['artist'], 'Eason Chan')
        self.assertEqual(params['total_duration_ms'], 757000)


class PiMusicPlayFromPlaylistTest(absltest.TestCase):
    """Tests for PiMusicPlayFromPlaylist task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicPlayFromPlaylist.generate_random_params()
        self.assertIn('playlist_name', params)
        self.assertIn('position', params)
        self.assertEqual(params['playlist_name'], 'Favorite')
        self.assertEqual(params['position'], 1)

    def test_goal(self):
        task = pimusic.PiMusicPlayFromPlaylist(
            params={'playlist_name': 'Favorite', 'position': 1}
        )
        self.assertEqual(task.goal, "In Pi Music Player, play the first song in 'Favorite' playlist.")


class PiMusicSortByDurationDescendingTest(absltest.TestCase):
    """Tests for PiMusicSortByDurationDescending task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicSortByDurationDescending.generate_random_params()
        self.assertIn('artist', params)
        self.assertEqual(params['artist'], 'Pink Floyd')


class PiMusicCreatePlaylistTest(absltest.TestCase):
    """Tests for PiMusicCreatePlaylist task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicCreatePlaylist.generate_random_params()
        self.assertIn('playlist_name', params)
        self.assertEqual(params['playlist_name'], 'Creepy')
        self.assertNotIn(params['playlist_name'], pimusic._DEFAULT_PLAYLISTS)


class PiMusicPauseAndSeekTest(absltest.TestCase):
    """Tests for PiMusicPauseAndSeek task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicPauseAndSeek.generate_random_params()
        self.assertIn('seek_minutes', params)
        self.assertIn('seek_seconds', params)
        self.assertEqual(params['seek_minutes'], 1)
        self.assertEqual(params['seek_seconds'], 27)

    def test_goal(self):
        task = pimusic.PiMusicPauseAndSeek(
            params={'seek_minutes': 1, 'seek_seconds': 27}
        )
        self.assertEqual(
            task.goal,
            'In Pi Music Player, pause the currently playing song and seek to 1 minute and 27 seconds.',
        )


class PiMusicPlaySongByTitleArtistTest(absltest.TestCase):
    """Tests for PiMusicPlaySongByTitleArtist task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicPlaySongByTitleArtist.generate_random_params()
        self.assertIn('song_title', params)
        self.assertIn('artist', params)
        self.assertEqual(params['song_title'], 'Lightship')
        self.assertEqual(params['artist'], 'Sonny Boy')


class PiMusicSortByDurationAscendingTest(absltest.TestCase):
    """Tests for PiMusicSortByDurationAscending task."""

    def test_generate_random_params(self):
        params = pimusic.PiMusicSortByDurationAscending.generate_random_params()
        self.assertEqual(params, {})


class TaskComplexityTest(absltest.TestCase):
    """Tests to verify task complexity values are set."""

    def test_query_tasks_have_complexity(self):
        query_tasks = [
            pimusic.PiMusicQueryTotalSongs,
            pimusic.PiMusicQueryArtistSongCount,
            pimusic.PiMusicQuerySongAlbum,
            pimusic.PiMusicQueryLongestSongDuration,
            pimusic.PiMusicQuerySortedSongsByTitle,
            pimusic.PiMusicQueryArtistTotalDuration,
        ]
        for task_cls in query_tasks:
            self.assertIsInstance(task_cls.complexity, (int, float))
            self.assertGreater(task_cls.complexity, 0)

    def test_operation_tasks_have_complexity(self):
        operation_tasks = [
            pimusic.PiMusicPlayFromPlaylist,
            pimusic.PiMusicSortByDurationDescending,
            pimusic.PiMusicCreatePlaylist,
            pimusic.PiMusicPauseAndSeek,
            pimusic.PiMusicPlaySongByTitleArtist,
            pimusic.PiMusicSortByDurationAscending,
        ]
        for task_cls in operation_tasks:
            self.assertIsInstance(task_cls.complexity, (int, float))
            self.assertGreater(task_cls.complexity, 0)


class TaskAppNamesTest(absltest.TestCase):
    """Tests to verify all tasks have correct app_names."""

    def test_all_tasks_have_app_names(self):
        all_tasks = [
            pimusic.PiMusicQueryTotalSongs,
            pimusic.PiMusicQueryArtistSongCount,
            pimusic.PiMusicQuerySongAlbum,
            pimusic.PiMusicQueryLongestSongDuration,
            pimusic.PiMusicQuerySortedSongsByTitle,
            pimusic.PiMusicQueryArtistTotalDuration,
            pimusic.PiMusicPlayFromPlaylist,
            pimusic.PiMusicSortByDurationDescending,
            pimusic.PiMusicCreatePlaylist,
            pimusic.PiMusicPauseAndSeek,
            pimusic.PiMusicPlaySongByTitleArtist,
            pimusic.PiMusicSortByDurationAscending,
        ]
        for task_cls in all_tasks:
            self.assertIn('pi music player', task_cls.app_names)


if __name__ == '__main__':
    absltest.main()
