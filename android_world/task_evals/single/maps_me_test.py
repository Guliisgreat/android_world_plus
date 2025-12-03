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

"""Tests for MAPS.ME tasks."""

from unittest import mock

from absl.testing import absltest
from android_world.task_evals.single import maps_me


# ============================================================================
# Tests for SQLite Row Types
# ============================================================================


class MapsBookmarkTest(absltest.TestCase):
  """Tests for MapsBookmark dataclass."""

  def test_create_bookmark(self):
    bookmark = maps_me.MapsBookmark(
        id='test-id-123',
        name='OpenAI HQ',
        featureName='OpenAI',
        latitude=37.7749,
        longitude=-122.4194,
    )
    self.assertEqual(bookmark.id, 'test-id-123')
    self.assertEqual(bookmark.name, 'OpenAI HQ')
    self.assertEqual(bookmark.featureName, 'OpenAI')
    self.assertAlmostEqual(bookmark.latitude, 37.7749)

  def test_default_values(self):
    bookmark = maps_me.MapsBookmark()
    self.assertIsNone(bookmark.id)
    self.assertEqual(bookmark.name, '')
    self.assertEqual(bookmark.deleted, 0)


class MapsCategoryTest(absltest.TestCase):
  """Tests for MapsCategory dataclass."""

  def test_create_category(self):
    category = maps_me.MapsCategory(
        id='cat-work-123',
        name='Work',
    )
    self.assertEqual(category.id, 'cat-work-123')
    self.assertEqual(category.name, 'Work')

  def test_default_values(self):
    category = maps_me.MapsCategory()
    self.assertEqual(category.isVisible, 1)
    self.assertEqual(category.deleted, 0)


class MapsPlaceHistoryTest(absltest.TestCase):
  """Tests for MapsPlaceHistory dataclass."""

  def test_create_place_history(self):
    place = maps_me.MapsPlaceHistory(
        name='Hilton Hotel',
        featureType='hotel',
        isHotel=1,
        latitude=37.7749,
        longitude=-122.4194,
    )
    self.assertEqual(place.name, 'Hilton Hotel')
    self.assertEqual(place.isHotel, 1)


# ============================================================================
# Tests for is_successful() validation
# ============================================================================


class MapsMeAddWorkPlaceValidationTest(absltest.TestCase):
  """Tests for MapsMeAddWorkPlace is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()
    self.mock_env.interaction_cache = None

  @mock.patch.object(maps_me, '_get_category_bookmark_relations')
  @mock.patch.object(maps_me, '_get_bookmarks')
  @mock.patch.object(maps_me, '_get_categories')
  def test_sqlite_validation_success(
      self, mock_get_categories, mock_get_bookmarks, mock_get_relations
  ):
    """Test successful SQLite validation when Work place exists."""
    # Setup mock data
    work_category = maps_me.MapsCategory(id='cat-1', name='Work')
    openai_bookmark = maps_me.MapsBookmark(
        id='bm-1', name='OpenAI', featureName='OpenAI Headquarters'
    )
    relation = maps_me.MapsCategoryBookmarkRelation(
        categoryId='cat-1', bookmarkId='bm-1'
    )

    mock_get_categories.return_value = [work_category]
    mock_get_bookmarks.return_value = [openai_bookmark]
    mock_get_relations.return_value = [relation]

    # Create and test task
    params = {'place_name': 'OpenAI'}
    task = maps_me.MapsMeAddWorkPlace(params)
    task.initialized = True  # Mark as initialized
    task.before_categories = []
    task.before_bookmarks = []

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(maps_me, '_get_category_bookmark_relations')
  @mock.patch.object(maps_me, '_get_bookmarks')
  @mock.patch.object(maps_me, '_get_categories')
  def test_sqlite_validation_no_work_category(
      self, mock_get_categories, mock_get_bookmarks, mock_get_relations
  ):
    """Test when Work category doesn't exist."""
    mock_get_categories.return_value = []  # No categories
    mock_get_bookmarks.return_value = []
    mock_get_relations.return_value = []

    self.mock_env.get_state.return_value = mock.MagicMock(ui_elements=[])

    params = {'place_name': 'OpenAI'}
    task = maps_me.MapsMeAddWorkPlace(params)
    task.initialized = True  # Mark as initialized
    task.before_categories = []
    task.before_bookmarks = []

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.0)

  @mock.patch.object(maps_me, '_get_category_bookmark_relations')
  @mock.patch.object(maps_me, '_get_bookmarks')
  @mock.patch.object(maps_me, '_get_categories')
  def test_new_bookmark_partial_credit(
      self, mock_get_categories, mock_get_bookmarks, mock_get_relations
  ):
    """Test partial credit when bookmark added but not linked to Work."""
    openai_bookmark = maps_me.MapsBookmark(
        id='bm-new', name='OpenAI', featureName='OpenAI'
    )

    mock_get_categories.return_value = []
    mock_get_bookmarks.return_value = [openai_bookmark]
    mock_get_relations.return_value = []

    self.mock_env.get_state.return_value = mock.MagicMock(ui_elements=[])

    params = {'place_name': 'OpenAI'}
    task = maps_me.MapsMeAddWorkPlace(params)
    task.initialized = True  # Mark as initialized
    task.before_categories = []
    task.before_bookmarks = []  # No bookmarks before

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.8)


class MapsMeCheckNearestPlaceValidationTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestPlace is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(maps_me, '_get_places_history')
  @mock.patch.object(maps_me, '_check_place_in_history')
  def test_agent_answer_with_sqlite_verification(
      self, mock_check_place, mock_get_places
  ):
    """Test full score when agent answer + SQLite verification."""
    self.mock_env.interaction_cache = 'The nearest restaurant is Olive Garden'
    mock_check_place.return_value = True
    mock_get_places.return_value = []

    params = {'place_type': 'restaurant', 'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestPlace(params)
    task.initialized = True  # Mark as initialized
    task.before_places_count = 0

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)

  @mock.patch.object(maps_me, '_get_places_history')
  @mock.patch.object(maps_me, '_check_place_in_history')
  def test_no_answer_but_place_in_history(
      self, mock_check_place, mock_get_places
  ):
    """Test partial credit when no answer but place found in history."""
    self.mock_env.interaction_cache = ''
    mock_check_place.return_value = True
    mock_get_places.return_value = []

    params = {'place_type': 'restaurant', 'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestPlace(params)
    task.initialized = True  # Mark as initialized
    task.before_places_count = 0

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 0.5)


class MapsMeCheckNearestHotelValidationTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestHotel is_successful() validation."""

  def setUp(self):
    self.mock_env = mock.MagicMock()

  @mock.patch.object(maps_me, '_get_places_history')
  def test_hotel_found_in_sqlite(self, mock_get_places):
    """Test when hotel is found in PlacesHistory with isHotel=1."""
    self.mock_env.interaction_cache = 'The nearest hotel is Hilton'
    hotel_place = maps_me.MapsPlaceHistory(
        name='Hilton', featureType='hotel', isHotel=1
    )
    mock_get_places.return_value = [hotel_place]

    params = {'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestHotel(params)
    task.initialized = True  # Mark as initialized
    task.before_places_count = 0

    result = task.is_successful(self.mock_env)
    self.assertEqual(result, 1.0)


class MapsMeCheckWalkingDistanceTimeTest(absltest.TestCase):
  """Tests for MapsMeCheckWalkingDistanceTime task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckWalkingDistanceTime.generate_random_params()
    self.assertIn('origin', params)
    self.assertIn('destination', params)
    self.assertNotEqual(params['origin'], params['destination'])

  def test_goal_format(self):
    params = {
        'origin': 'Bus Stop of Stanford Campus Oval',
        'destination': 'Bus Stop of Oxford Street & University Avenue',
        'expected_answer': '',
    }
    task = maps_me.MapsMeCheckWalkingDistanceTime(params)
    self.assertEqual(
        task.goal,
        'Check the walking distance and time between Bus Stop of Stanford '
        'Campus Oval and Bus Stop of Oxford Street & University Avenue',
    )


class MapsMeCheckDrivingDistanceTimeTest(absltest.TestCase):
  """Tests for MapsMeCheckDrivingDistanceTime task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckDrivingDistanceTime.generate_random_params()
    self.assertIn('origin', params)
    self.assertIn('destination', params)

  def test_goal_format(self):
    params = {
        'origin': 'Bus stop of 2700 Coast Avenue',
        'destination': 'Bus Stop Route 51',
        'expected_answer': '',
    }
    task = maps_me.MapsMeCheckDrivingDistanceTime(params)
    self.assertEqual(
        task.goal,
        'Check the driving distance and time between Bus stop of 2700 Coast '
        'Avenue and Bus Stop Route 51',
    )


class MapsMeCheckRidingTimeTest(absltest.TestCase):
  """Tests for MapsMeCheckRidingTime task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckRidingTime.generate_random_params()
    self.assertIn('origin', params)
    self.assertIn('destination', params)

  def test_goal_format(self):
    params = {
        'origin': 'Bus Stop of Stanford Campus Oval',
        'destination': 'Bus Stop of Oxford Street & University Avenue',
        'expected_answer': '',
    }
    task = maps_me.MapsMeCheckRidingTime(params)
    self.assertEqual(
        task.goal,
        'Check the riding time between Bus Stop of Stanford Campus Oval and '
        'Bus Stop of Oxford Street & University Avenue',
    )


class MapsMeCheckPublicTransportRouteTest(absltest.TestCase):
  """Tests for MapsMeCheckPublicTransportRoute task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckPublicTransportRoute.generate_random_params()
    self.assertIn('origin', params)
    self.assertIn('destination', params)

  def test_goal_format(self):
    params = {
        'origin': 'Bus stop of 2700 Coast Avenue',
        'destination': 'Bus Stop Route 51',
        'expected_answer': '',
    }
    task = maps_me.MapsMeCheckPublicTransportRoute(params)
    self.assertEqual(
        task.goal,
        'Check the route by public transportation between Bus stop of 2700 '
        'Coast Avenue and Bus Stop Route 51',
    )


class MapsMeCompareRidingVsPublicTransportTest(absltest.TestCase):
  """Tests for MapsMeCompareRidingVsPublicTransport task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCompareRidingVsPublicTransport.generate_random_params()
    self.assertIn('origin', params)
    self.assertIn('destination', params)

  def test_goal_format(self):
    params = {
        'origin': 'Bus stop of 2700 Coast Avenue',
        'destination': 'Bus Stop Route 51',
        'expected_answer': '',
    }
    task = maps_me.MapsMeCompareRidingVsPublicTransport(params)
    self.assertIn('Compare which takes less time', task.goal)
    self.assertIn('by riding or by public transportation', task.goal)


class MapsMeCheckNearestPlaceTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestPlace task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckNearestPlace.generate_random_params()
    self.assertIn('place_type', params)

  def test_goal_format(self):
    params = {'place_type': 'restaurant', 'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestPlace(params)
    self.assertEqual(
        task.goal,
        'Check the nearest restaurant and tell me what is it',
    )


class MapsMeCheckNearestPlaceWalkTimeTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestPlaceWalkTime task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckNearestPlaceWalkTime.generate_random_params()
    self.assertIn('place_type', params)

  def test_goal_format(self):
    params = {'place_type': 'restaurant', 'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestPlaceWalkTime(params)
    self.assertIn('nearest restaurant', task.goal)
    self.assertIn('time it will take to walk', task.goal)


class MapsMeCheckNearestHotelTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestHotel task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckNearestHotel.generate_random_params()
    self.assertIn('expected_answer', params)

  def test_goal_format(self):
    params = {'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestHotel(params)
    self.assertEqual(
        task.goal,
        'Check the nearest hotel, tell me what is it',
    )


class MapsMeCheckNearestPlaceDriveTimeTest(absltest.TestCase):
  """Tests for MapsMeCheckNearestPlaceDriveTime task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeCheckNearestPlaceDriveTime.generate_random_params()
    self.assertIn('place_name', params)

  def test_goal_format(self):
    params = {'place_name': 'IKEA', 'expected_answer': ''}
    task = maps_me.MapsMeCheckNearestPlaceDriveTime(params)
    self.assertIn('nearest IKEA', task.goal)
    self.assertIn('how long it will take to drive', task.goal)


class MapsMeAddWorkPlaceTest(absltest.TestCase):
  """Tests for MapsMeAddWorkPlace task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeAddWorkPlace.generate_random_params()
    self.assertIn('place_name', params)

  def test_goal_format(self):
    params = {'place_name': 'OpenAI'}
    task = maps_me.MapsMeAddWorkPlace(params)
    self.assertEqual(
        task.goal,
        'Add the address of OpenAI to my Work place',
    )

  def test_complexity(self):
    params = {'place_name': 'OpenAI'}
    task = maps_me.MapsMeAddWorkPlace(params)
    self.assertEqual(task.complexity, 3)


class MapsMeNavigateToLocationTest(absltest.TestCase):
  """Tests for MapsMeNavigateToLocation task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeNavigateToLocation.generate_random_params()
    self.assertIn('destination', params)

  def test_goal_format(self):
    params = {'destination': 'Stanford University'}
    task = maps_me.MapsMeNavigateToLocation(params)
    self.assertEqual(
        task.goal,
        'Navigate from my location to Stanford University',
    )


class MapsMeNavigateToStanfordTest(absltest.TestCase):
  """Tests for MapsMeNavigateToStanford task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeNavigateToStanford.generate_random_params()
    self.assertIsInstance(params, dict)

  def test_goal_format(self):
    params = {}
    task = maps_me.MapsMeNavigateToStanford(params)
    self.assertEqual(
        task.goal,
        'Navigate from my location to Stanford University',
    )


class MapsMeNavigateToUniversitySouthTest(absltest.TestCase):
  """Tests for MapsMeNavigateToUniversitySouth task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeNavigateToUniversitySouth.generate_random_params()
    self.assertIsInstance(params, dict)

  def test_goal_format(self):
    params = {}
    task = maps_me.MapsMeNavigateToUniversitySouth(params)
    self.assertEqual(
        task.goal,
        'Navigate from my location to University South',
    )


class MapsMeNavigateToOpenAITest(absltest.TestCase):
  """Tests for MapsMeNavigateToOpenAI task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeNavigateToOpenAI.generate_random_params()
    self.assertIsInstance(params, dict)

  def test_goal_format(self):
    params = {}
    task = maps_me.MapsMeNavigateToOpenAI(params)
    self.assertEqual(
        task.goal,
        'Navigate from my location to OpenAI',
    )


class MapsMeNavigateToBerkeleyTest(absltest.TestCase):
  """Tests for MapsMeNavigateToBerkeley task."""

  def test_generate_random_params(self):
    params = maps_me.MapsMeNavigateToBerkeley.generate_random_params()
    self.assertIsInstance(params, dict)

  def test_goal_format(self):
    params = {}
    task = maps_me.MapsMeNavigateToBerkeley(params)
    self.assertEqual(
        task.goal,
        'Navigate from my location to University of California, Berkeley',
    )


if __name__ == '__main__':
  absltest.main()

