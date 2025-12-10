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

"""Tasks for MAPS.ME navigation app."""

import abc
import dataclasses
import random
from typing import Any, Optional

from absl import logging
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.task_evals.utils import sqlite_schema_utils
from android_world.task_evals.utils import sqlite_utils
from android_world.utils import fuzzy_match_lib


_APP_NAME = 'maps.me'
_PACKAGE_NAME = 'com.mapswithme.maps.pro'

# Database paths
_FAVORITES_DB_PATH = f'/data/data/{_PACKAGE_NAME}/databases/favorites'
_SEARCH_HISTORY_DB_PATH = f'/data/data/{_PACKAGE_NAME}/databases/search-history'


# ============================================================================
# SQLite Row Types for MAPS.ME databases
# ============================================================================


@dataclasses.dataclass(frozen=True)
class MapsBookmark(sqlite_schema_utils.SQLiteRow):
  """Represents a bookmark in the favorites database.

  Schema from: PRAGMA table_info(Bookmark)
  """
  id: Optional[str] = None
  name: str = ''
  featureName: str = ''
  createdAt: int = 0
  description: str = ''
  featureTypes: str = ''
  scale: int = 0
  color: str = ''
  icon: str = ''
  latitude: float = 0.0
  longitude: float = 0.0
  deleted: int = 0
  updated: int = 1
  sortOrder: int = 0


@dataclasses.dataclass(frozen=True)
class MapsCategory(sqlite_schema_utils.SQLiteRow):
  """Represents a category in the favorites database.

  Schema from: PRAGMA table_info(Category)
  """
  id: Optional[str] = None
  name: str = ''
  imageUrl: str = ''
  modifiedAt: int = 0
  description: str = ''
  creatorId: str = ''
  isVisible: int = 1
  deleted: int = 0
  updated: int = 1
  sortOrder: int = 0


@dataclasses.dataclass(frozen=True)
class MapsCategoryBookmarkRelation(sqlite_schema_utils.SQLiteRow):
  """Represents a category-bookmark relation.

  Schema from: PRAGMA table_info(CategoryBookmarkRelations)
  """
  categoryId: str = ''
  bookmarkId: str = ''


@dataclasses.dataclass(frozen=True)
class MapsPlaceHistory(sqlite_schema_utils.SQLiteRow):
  """Represents a place in search history.

  Schema from: PRAGMA table_info(PlacesHistory)
  """
  mwmName: str = ''
  featureIndex: int = 0
  name: str = ''
  latitude: float = 0.0
  longitude: float = 0.0
  featureType: str = ''
  hotelPricing: str = ''
  hotelRating: float = 0.0
  hotelStars: int = 0
  isHotel: int = 0
  categories: str = ''
  createdAt: int = 0


@dataclasses.dataclass(frozen=True)
class MapsQueryHistory(sqlite_schema_utils.SQLiteRow):
  """Represents a search query in history.

  Schema from: PRAGMA table_info(QueryHistory)
  """
  query: str = ''
  createdAt: int = 0


# Sample locations for generating random params
_LOCATIONS = [
    'Bus Stop of Stanford Campus Oval',
    'Bus Stop of Oxford Street & University Avenue',
    'Bus stop of 2700 Coast Avenue',
    'Bus Stop Route 51',
    'Stanford University',
    'University of California, Berkeley',
    'OpenAI',
    'University South',
]

_PLACE_TYPES = [
    'restaurant',
    'cafe',
    'gas station',
    'pharmacy',
    'supermarket',
    'hospital',
    'bank',
]  # Note: 'hotel' removed - use MapsMeCheckNearestHotel for hotel queries

_TRANSPORT_MODES = ['walking', 'driving', 'riding', 'public transportation']


# ============================================================================
# SQLite Helper Functions
# ============================================================================


def _get_categories(env: interface.AsyncEnv) -> list[MapsCategory]:
  """Get all categories from the favorites database."""
  try:
    return sqlite_utils.get_rows_from_remote_device(
        'Category',
        _FAVORITES_DB_PATH,
        MapsCategory,
        env,
    )
  except Exception as e:
    logging.warning('Failed to get categories: %s', e)
    return []


def _get_bookmarks(env: interface.AsyncEnv) -> list[MapsBookmark]:
  """Get all bookmarks from the favorites database."""
  try:
    return sqlite_utils.get_rows_from_remote_device(
        'Bookmark',
        _FAVORITES_DB_PATH,
        MapsBookmark,
        env,
    )
  except Exception as e:
    logging.warning('Failed to get bookmarks: %s', e)
    return []


def _get_category_bookmark_relations(
    env: interface.AsyncEnv,
) -> list[MapsCategoryBookmarkRelation]:
  """Get all category-bookmark relations from the favorites database."""
  try:
    return sqlite_utils.get_rows_from_remote_device(
        'CategoryBookmarkRelations',
        _FAVORITES_DB_PATH,
        MapsCategoryBookmarkRelation,
        env,
    )
  except Exception as e:
    logging.warning('Failed to get category-bookmark relations: %s', e)
    return []


def _get_places_history(env: interface.AsyncEnv) -> list[MapsPlaceHistory]:
  """Get all places from search history database."""
  try:
    return sqlite_utils.get_rows_from_remote_device(
        'PlacesHistory',
        _SEARCH_HISTORY_DB_PATH,
        MapsPlaceHistory,
        env,
    )
  except Exception as e:
    logging.warning('Failed to get places history: %s', e)
    return []


def _get_query_history(env: interface.AsyncEnv) -> list[MapsQueryHistory]:
  """Get all queries from search history database."""
  try:
    return sqlite_utils.get_rows_from_remote_device(
        'QueryHistory',
        _SEARCH_HISTORY_DB_PATH,
        MapsQueryHistory,
        env,
    )
  except Exception as e:
    logging.warning('Failed to get query history: %s', e)
    return []


def _check_work_place_exists(
    env: interface.AsyncEnv,
    place_name: str,
) -> bool:
  """Check if a Work place with the given name exists in favorites.

  Checks if:
  1. A Category named "Work" exists
  2. A Bookmark containing the place name exists
  3. They are linked via CategoryBookmarkRelations
  """
  categories = _get_categories(env)
  bookmarks = _get_bookmarks(env)
  relations = _get_category_bookmark_relations(env)

  # Find "Work" category
  work_category = None
  for cat in categories:
    if cat.name and 'work' in cat.name.lower():
      work_category = cat
      break

  if not work_category:
    logging.info('No Work category found.')
    return False

  # Find bookmark with place name
  place_name_lower = place_name.lower()
  matching_bookmarks = []
  for bm in bookmarks:
    bm_name = (bm.name or '').lower()
    bm_feature = (bm.featureName or '').lower()
    if place_name_lower in bm_name or place_name_lower in bm_feature:
      matching_bookmarks.append(bm)

  if not matching_bookmarks:
    logging.info('No bookmark found containing: %s', place_name)
    return False

  # Check if any matching bookmark is linked to Work category
  work_bookmark_ids = {
      rel.bookmarkId for rel in relations if rel.categoryId == work_category.id
  }
  for bm in matching_bookmarks:
    if bm.id in work_bookmark_ids:
      logging.info('Found Work place with bookmark: %s', bm.name)
      return True

  logging.info('Bookmark found but not linked to Work category.')
  return False


def _check_place_in_history(
    env: interface.AsyncEnv,
    place_type: str,
) -> bool:
  """Check if a place of the given type was recently viewed."""
  places = _get_places_history(env)
  place_type_lower = place_type.lower()

  for place in places:
    # Check featureType and categories
    feature_type = (place.featureType or '').lower()
    categories = (place.categories or '').lower()
    name = (place.name or '').lower()

    if place_type_lower in feature_type or place_type_lower in categories:
      logging.info('Found place in history: %s (type: %s)', place.name, place.featureType)
      return True
    if place_type_lower in name:
      logging.info('Found place in history by name: %s', place.name)
      return True

  return False


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


def _check_navigation_active(env: interface.AsyncEnv) -> bool:
  """Check if navigation mode appears to be active."""
  activity = _get_current_activity(env)
  # Check if we're in a navigation-related activity
  if 'route' in activity.lower() or 'navigation' in activity.lower():
    return True
  # Check UI for navigation indicators
  navigation_indicators = ['route', 'direction', 'navigate', 'start', 'go']
  for indicator in navigation_indicators:
    if _check_ui_for_text(env, indicator):
      return True
  return False


# ============================================================================
# Base class for MAPS.ME tasks
# ============================================================================


class _MapsMe(task_eval.TaskEval, abc.ABC):
  """Base class for MAPS.ME task evaluations."""

  schema = {}
  app_names = (_APP_NAME,)
  template = ''

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)


# ============================================================================
# Query Tasks - Route Distance and Time
# ============================================================================


class _MapsMeQuery(_MapsMe):
  """Base class for MAPS.ME query tasks.

  For query tasks, we check if the agent's answer contains the expected
  information. The agent should use the 'answer' action to provide their
  response after looking up the information in the app.
  """

  complexity = 2.5

  @property
  @abc.abstractmethod
  def expected_answer(self) -> str:
    """The expected answer to the query."""

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the agent provided a valid answer.

    The agent's answer is stored in env.interaction_cache when they use
    the 'answer' action.
    """
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''

    if not agent_answer:
      logging.warning('Agent did not provide an answer via the answer action.')
      return 0.0

    expected = self.expected_answer.lower()

    # For queries with expected answers, check if it matches
    if expected:
      if fuzzy_match_lib.fuzzy_match(expected, agent_answer):
        logging.info('Agent answer matches expected: %s', agent_answer)
        return 1.0
      # Also check if the expected value is contained in the answer
      if expected in agent_answer:
        logging.info('Expected answer found in agent response.')
        return 1.0

    # For queries without predefined answers (e.g., distance/time queries),
    # check if the answer contains relevant information
    relevant_terms = ['km', 'mi', 'mile', 'meter', 'min', 'hour', 'hr', 'minute']
    for term in relevant_terms:
      if term in agent_answer:
        logging.info('Agent provided distance/time information: %s', agent_answer)
        return 1.0

    logging.warning('Agent answer does not contain expected information: %s', agent_answer)
    return 0.0


class MapsMeCheckWalkingDistanceTime(_MapsMeQuery):
  """Query: Check walking distance and time between two locations."""

  template = 'In the MAPS.ME app, check the walking distance and time between {origin} and {destination}'
  complexity = 2.5

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    locations = random.sample(_LOCATIONS, 2)
    return {'origin': locations[0], 'destination': locations[1], 'expected_answer': ''}


class MapsMeCheckDrivingDistanceTime(_MapsMeQuery):
  """Query: Check driving distance and time between two locations."""

  template = 'In the MAPS.ME app, check the driving distance and time between {origin} and {destination}'
  complexity = 2.5

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    locations = random.sample(_LOCATIONS, 2)
    return {'origin': locations[0], 'destination': locations[1], 'expected_answer': ''}


class MapsMeCheckRidingTime(_MapsMeQuery):
  """Query: Check riding/cycling time between two locations."""

  template = 'In the MAPS.ME app, check the riding time between {origin} and {destination}'
  complexity = 2.5

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    locations = random.sample(_LOCATIONS, 2)
    return {'origin': locations[0], 'destination': locations[1], 'expected_answer': ''}


class MapsMeCheckPublicTransportRoute(_MapsMeQuery):
  """Query: Check route by public transportation between two locations."""

  template = 'In the MAPS.ME app, check the route by public transportation between {origin} and {destination}'
  complexity = 3

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    locations = random.sample(_LOCATIONS, 2)
    return {'origin': locations[0], 'destination': locations[1], 'expected_answer': ''}


class MapsMeCompareRidingVsPublicTransport(_MapsMeQuery):
  """Query: Compare travel time between riding and public transportation."""

  template = (
      'In the MAPS.ME app, compare which takes less time to travel between {origin} and '
      '{destination}, by riding or by public transportation?'
  )
  complexity = 3.5

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if the agent provided a comparison answer."""
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''

    if not agent_answer:
      return 0.0

    # Check if the answer mentions either transport mode
    if 'riding' in agent_answer or 'bike' in agent_answer or 'cycling' in agent_answer:
      logging.info('Agent answered with riding/cycling.')
      return 1.0
    if 'public' in agent_answer or 'transit' in agent_answer or 'bus' in agent_answer:
      logging.info('Agent answered with public transportation.')
      return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    locations = random.sample(_LOCATIONS, 2)
    return {'origin': locations[0], 'destination': locations[1], 'expected_answer': ''}


# ============================================================================
# Query Tasks - Nearby Places
# ============================================================================


class MapsMeCheckNearestPlace(_MapsMeQuery):
  """Query: Check the nearest place of a specific type.

  Validates success by:
  1. Checking agent's answer for place information
  2. Optionally verifying via PlacesHistory in search-history database
  """

  template = 'In the MAPS.ME app, check the nearest {place_type} and tell me what is it'
  complexity = 2

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_places_count = 0

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    # Store initial places history count
    places = _get_places_history(env)
    self.before_places_count = len(places)
    logging.info('Before: %d places in history', self.before_places_count)

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if agent found and reported a place."""
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''
    place_type = self.params['place_type'].lower()

    if not agent_answer:
      # Check if place was viewed (appears in history) even without answer
      if _check_place_in_history(env, place_type):
        logging.info('Place found in history but no agent answer.')
        return 0.5
      return 0.0

    # Primary: Check if agent answer contains relevant info
    if place_type in agent_answer or len(agent_answer) > 10:
      # Bonus: Also verify via database if possible
      if _check_place_in_history(env, place_type):
        logging.info('Agent answer + SQLite verification: %s', agent_answer)
        return 1.0
      logging.info('Agent provided place information: %s', agent_answer)
      return 1.0

    # Secondary: Check if new places were added to history
    after_places = _get_places_history(env)
    if len(after_places) > self.before_places_count:
      logging.info('New places added to history during task.')
      return 0.7

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'place_type': random.choice(_PLACE_TYPES), 'expected_answer': ''}


class MapsMeCheckNearestPlaceWalkTime(_MapsMeQuery):
  """Query: Check nearest place and walking time to it.

  Validates via agent answer + optional PlacesHistory verification.
  """

  template = (
      'In the MAPS.ME app, check the nearest {place_type}, and tell me the time it will take '
      'to walk to the {place_type}.'
  )
  complexity = 2.5

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_places_count = 0

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    places = _get_places_history(env)
    self.before_places_count = len(places)

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if agent found place and reported walking time."""
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''
    place_type = self.params['place_type'].lower()

    if not agent_answer:
      return 0.0

    # Check for time units in answer
    time_terms = ['min', 'minute', 'hour', 'hr', 'sec']
    has_time = any(term in agent_answer for term in time_terms)

    if has_time:
      # Bonus: Verify place was viewed
      if _check_place_in_history(env, place_type):
        logging.info('Agent answer with time + SQLite verification.')
        return 1.0
      logging.info('Agent provided walking time: %s', agent_answer)
      return 1.0

    # Partial credit if place type mentioned
    if place_type in agent_answer:
      logging.info('Agent mentioned place type but no time: %s', agent_answer)
      return 0.5

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    place = random.choice(_PLACE_TYPES)
    return {'place_type': place, 'expected_answer': ''}


class MapsMeCheckNearestHotel(_MapsMeQuery):
  """Query: Check the nearest hotel.

  Validates via agent answer + PlacesHistory verification for hotels.
  """

  template = 'In the MAPS.ME app, check the nearest hotel, tell me what is it'
  complexity = 2

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_places_count = 0

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    places = _get_places_history(env)
    self.before_places_count = len(places)

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if agent found and reported a hotel."""
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''

    if not agent_answer:
      # Check if hotel was viewed in history
      places = _get_places_history(env)
      for place in places:
        if place.isHotel == 1:
          logging.info('Hotel found in history: %s', place.name)
          return 0.5
      return 0.0

    # Check for hotel-related terms in answer
    if 'hotel' in agent_answer or len(agent_answer) > 10:
      # Verify via SQLite if possible
      places = _get_places_history(env)
      for place in places:
        if place.isHotel == 1:
          logging.info('Agent answer + hotel found in SQLite: %s', place.name)
          return 1.0
      logging.info('Agent provided hotel information: %s', agent_answer)
      return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {'expected_answer': ''}


class MapsMeCheckNearestPlaceDriveTime(_MapsMeQuery):
  """Query: Check nearest specific place and driving time to it.

  Validates via agent answer + optional PlacesHistory verification.
  """

  template = (
      'In the MAPS.ME app, check the nearest {place_name}, and tell me how long it will take '
      'to drive to the {place_name}'
  )
  complexity = 2.5

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_places_count = 0

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    places = _get_places_history(env)
    self.before_places_count = len(places)

  @property
  def expected_answer(self) -> str:
    return self.params.get('expected_answer', '')

  def is_successful(self, env: interface.AsyncEnv) -> float:
    """Check if agent found place and reported driving time."""
    super().is_successful(env)
    agent_answer = env.interaction_cache.lower() if env.interaction_cache else ''
    place_name = self.params['place_name'].lower()

    if not agent_answer:
      return 0.0

    # Check for time units in answer
    time_terms = ['min', 'minute', 'hour', 'hr']
    has_time = any(term in agent_answer for term in time_terms)

    if has_time:
      # Verify place was viewed in history
      places = _get_places_history(env)
      for place in places:
        if place_name in (place.name or '').lower():
          logging.info('Agent answer with time + place in SQLite: %s', place.name)
          return 1.0
      logging.info('Agent provided driving time: %s', agent_answer)
      return 1.0

    # Partial credit if place name mentioned
    if place_name in agent_answer:
      logging.info('Agent mentioned place but no time: %s', agent_answer)
      return 0.5

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    places = ['IKEA', 'Costco', 'Walmart', 'Target', 'Home Depot']
    return {'place_name': random.choice(places), 'expected_answer': ''}


# ============================================================================
# Operation Tasks - Add Places and Navigate
# ============================================================================


class _MapsMeOperation(_MapsMe):
  """Base class for MAPS.ME operation tasks.

  These tasks verify success by checking:
  1. The app's current activity/state
  2. UI elements indicating the operation was performed
  3. The agent's completion status
  """

  complexity = 2

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.initial_activity = ''

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    self.initial_activity = _get_current_activity(env)

  @abc.abstractmethod
  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    """Validate that the operation was performed successfully."""


class MapsMeAddWorkPlace(_MapsMeOperation):
  """Operation: Add an address to Work place.

  Validates success by querying the favorites SQLite database to check if:
  1. A "Work" category exists
  2. A bookmark with the place name exists
  3. The bookmark is linked to the Work category
  """

  template = 'In the MAPS.ME app, add the address of {place_name} to my Work place'
  complexity = 3

  def __init__(self, params: dict[str, Any]):
    super().__init__(params)
    self.before_categories: list[MapsCategory] = []
    self.before_bookmarks: list[MapsBookmark] = []

  def initialize_task(self, env: interface.AsyncEnv) -> None:
    super().initialize_task(env)
    # Store state before task for comparison
    self.before_categories = _get_categories(env)
    self.before_bookmarks = _get_bookmarks(env)
    logging.info(
        'Before: %d categories, %d bookmarks',
        len(self.before_categories),
        len(self.before_bookmarks),
    )

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    """Check if the workplace was added using SQLite database query."""
    place_name = self.params['place_name']

    # Primary validation: Check SQLite database
    if _check_work_place_exists(env, place_name):
      logging.info('SQLite validation: Work place with %s found.', place_name)
      return 1.0

    # Check if any new bookmarks were added
    after_bookmarks = _get_bookmarks(env)
    before_ids = {b.id for b in self.before_bookmarks}
    new_bookmarks = [b for b in after_bookmarks if b.id not in before_ids]

    if new_bookmarks:
      # Check if any new bookmark matches the place name
      place_name_lower = place_name.lower()
      for bm in new_bookmarks:
        bm_name = (bm.name or '').lower()
        bm_feature = (bm.featureName or '').lower()
        if place_name_lower in bm_name or place_name_lower in bm_feature:
          logging.info('Found new bookmark matching place: %s', bm.name)
          return 0.8  # Partial credit - bookmark added but maybe not linked to Work

    # Fallback: Check UI for the place name or 'work' indicator
    if _check_ui_for_text(env, 'work') or _check_ui_for_text(env, place_name.lower()):
      logging.info('UI validation: Found Work place or place name in UI.')
      return 0.7

    # Last resort: If agent indicated completion
    if env.interaction_cache:
      logging.info('Agent indicated completion: %s', env.interaction_cache)
      return 0.5

    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    places = ['OpenAI', 'Google', 'Apple', 'Meta', 'Microsoft', 'Stanford University']
    return {'place_name': random.choice(places)}


class MapsMeNavigateToLocation(_MapsMeOperation):
  """Operation: Navigate from current location to a destination."""

  template = 'In the MAPS.ME app, navigate from my location to {destination}'
  complexity = 2

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    """Check if navigation was started to the correct destination."""
    destination = self.params['destination'].lower()

    # Must have destination visible AND navigation active
    if _check_ui_for_text(env, destination) and _check_navigation_active(env):
      logging.info('Navigation active with destination: %s', destination)
      return 1.0

    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    destinations = [
        'Stanford University',
        'University South',
        'OpenAI',
        'University of California, Berkeley',
        'San Francisco Airport',
        'Golden Gate Bridge',
    ]
    return {'destination': random.choice(destinations)}


class MapsMeNavigateToStanford(_MapsMeOperation):
  """Operation: Navigate to Stanford University."""

  template = 'In the MAPS.ME app, navigate from my location to Stanford University'
  complexity = 2

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    # Must have "stanford" visible AND navigation active
    if _check_ui_for_text(env, 'stanford') and _check_navigation_active(env):
      return 1.0
    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class MapsMeNavigateToUniversitySouth(_MapsMeOperation):
  """Operation: Navigate to University South."""

  template = 'In the MAPS.ME app, navigate from my location to University South'
  complexity = 2

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    # Must have "university south" visible AND navigation active
    if _check_ui_for_text(env, 'university south') and _check_navigation_active(env):
      return 1.0
    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class MapsMeNavigateToOpenAI(_MapsMeOperation):
  """Operation: Navigate to OpenAI."""

  template = 'In the MAPS.ME app, navigate from my location to OpenAI'
  complexity = 2

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    # Must have "openai" visible AND navigation active
    if _check_ui_for_text(env, 'openai') and _check_navigation_active(env):
      return 1.0
    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class MapsMeNavigateToBerkeley(_MapsMeOperation):
  """Operation: Navigate to University of California, Berkeley."""

  template = 'In the MAPS.ME app, navigate from my location to University of California, Berkeley'
  complexity = 2

  def _validate_operation(self, env: interface.AsyncEnv) -> float:
    # Must have "berkeley" or "california" visible AND navigation active
    has_destination = _check_ui_for_text(env, 'berkeley') or _check_ui_for_text(env, 'california')
    if has_destination and _check_navigation_active(env):
      return 1.0
    return 0.0

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    return self._validate_operation(env)

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}
