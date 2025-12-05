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

"""Evaluators for Wikipedia app."""

import os
import xml.etree.ElementTree as ET
from typing import Any, Optional

from absl import logging
from android_env.proto import adb_pb2
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.utils import file_utils

PACKAGE_NAME = "org.wikipedia"
PREFERENCES_PATH = f"/data/data/{PACKAGE_NAME}/shared_prefs/org.wikipedia_preferences.xml"


def _read_preferences_xml(env: interface.AsyncEnv) -> Optional[ET.Element]:
  """Read and parse Wikipedia preferences XML file.

  Args:
    env: The AndroidWorld environment.

  Returns:
    Root element of the XML tree, or None if reading fails.
  """
  try:
    # Ensure root access
    adb_utils.set_root_if_needed(env.controller.env)

    # Check if file exists on device
    if not file_utils.check_file_exists(PREFERENCES_PATH, env.controller.env):
      logging.warning(
          "Preferences.xml file does not exist on device: %s", PREFERENCES_PATH
      )
      return None

    # Pull file content from device
    pull_response = env.controller.env.execute_adb_call(
        adb_pb2.AdbRequest(
            pull=adb_pb2.AdbRequest.Pull(path=PREFERENCES_PATH),
            timeout_sec=None,
        )
    )
    adb_utils.check_ok(pull_response)

    # Parse the XML content
    root = ET.fromstring(pull_response.pull.content)
    return root

  except FileNotFoundError as e:
    logging.warning("Preferences.xml file not found: %s", e)
    return None
  except ET.ParseError as e:
    logging.warning("Failed to parse Preferences.xml: %s", e)
    return None
  except Exception as e:
    logging.warning("Error reading Preferences.xml: %s", e)
    return None


def _get_text_size_multiplier(env: interface.AsyncEnv) -> Optional[str]:
  """Get the text size multiplier from preferences.

  Note: This preference only exists in XML after it has been explicitly set.
  If it doesn't exist, the app is using the default value (typically 0 = 100%).

  Args:
    env: The AndroidWorld environment.

  Returns:
    Text size multiplier value as string, or None if not found (default value).
  """
  root = _read_preferences_xml(env)
  if root is None:
    return None

  try:
    text_size_elem = root.find(".//int[@name='textSizeMultiplier']")
    if text_size_elem is not None:
      value = text_size_elem.attrib.get("value")
      if value is not None:
        logging.debug("Found textSizeMultiplier: %s", value)
        return value
    # Preference doesn't exist - means default value (0 = 100%)
    # This is normal if the text size hasn't been changed from default
    logging.debug(
        "textSizeMultiplier not found in preferences (default = 0 = 100%%)"
    )
    return None
  except Exception as e:
    logging.warning("Error getting text size multiplier: %s", e)
    return None


def _get_feed_state(env: interface.AsyncEnv) -> Optional[str]:
  """Get the feed customization state from preferences.

  The feed state is stored in the last element's text as a JSON-like array.

  Args:
    env: The AndroidWorld environment.

  Returns:
    Feed state as string (e.g., '[true,true,false,...]'), or None if not found.
  """
  root = _read_preferences_xml(env)
  if root is None:
    return None

  try:
    # The feed state is in the last element's text
    if len(root) > 0:
      return root[-1].text
    return None
  except Exception as e:
    logging.warning("Error getting feed state: %s", e)
    return None


def _get_show_link_previews(env: interface.AsyncEnv) -> Optional[bool]:
  """Get the show link previews setting from preferences.

  Args:
    env: The AndroidWorld environment.

  Returns:
    True if enabled, False if disabled, None if not found.
  """
  root = _read_preferences_xml(env)
  if root is None:
    return None

  try:
    preview_elem = root.find(".//boolean[@name='showLinkPreviews']")
    if preview_elem is not None:
      return preview_elem.attrib.get("value") == "true"
    return None
  except Exception as e:
    logging.warning("Error getting show link previews: %s", e)
    return None


def _check_tab_selected(state: interface.State, resource_id: str) -> bool:
  """Check if a specific tab is selected.

  Args:
    state: Current environment state.
    resource_id: Resource ID of the tab to check.

  Returns:
    True if the tab is selected, False otherwise.
  """
  try:
    for element in state.ui_elements:
      # Check both resource_id and resource_name for compatibility
      if (element.resource_id == resource_id or 
          element.resource_name == resource_id):
        return element.is_selected is True
    return False
  except Exception:
    return False


def _check_wikipedia_open(state: interface.State) -> bool:
  """Check if Wikipedia app is open.

  Args:
    state: Current environment state.

  Returns:
    True if Wikipedia is open, False otherwise.
  """
  try:
    for element in state.ui_elements:
      if element.package_name == PACKAGE_NAME:
        return True
    return False
  except Exception:
    return False


class _WikipediaTaskEval(task_eval.TaskEval):
  """Base class for Wikipedia-related TaskEvals."""

  app_names = ("wikipedia",)


class WikipediaOpen(_WikipediaTaskEval):
  """Task for opening the Wikipedia app."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "Open the Wikipedia app."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    if _check_wikipedia_open(state):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class WikipediaGoToSearchTab(_WikipediaTaskEval):
  """Task for navigating to the search tab in Wikipedia."""

  complexity = 1.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Wikipedia app, go to the search tab."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    if _check_tab_selected(state, "org.wikipedia:id/nav_tab_search"):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class WikipediaGoToSavedTab(_WikipediaTaskEval):
  """Task for navigating to the saved tab in Wikipedia."""

  complexity = 1.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Wikipedia app, go to the saved tab."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    if _check_tab_selected(state, "org.wikipedia:id/nav_tab_reading_lists"):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class WikipediaIncreaseTextSize180(_WikipediaTaskEval):
  """Task for increasing text size to 180% in Wikipedia."""

  complexity = 3.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Wikipedia app, increase the text size to 180%."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    text_size = _get_text_size_multiplier(env)
    if text_size == "8":  # 180% corresponds to value 8
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class WikipediaDecreaseTextSize50(_WikipediaTaskEval):
  """Task for decreasing text size to 50% in Wikipedia."""

  complexity = 3.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Wikipedia app, decrease the text size to 50%."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    text_size = _get_text_size_multiplier(env)
    # 50% corresponds to value -5
    # If text_size is None, it means default (0 = 100%), so not 50%
    if text_size == "-5":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


# class WikipediaDisableFeaturedArticleFeed(_WikipediaTaskEval):
#   """Task for disabling featured article feed and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable featured article feed, and return to the feed on Wikipedia."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Featured article feed is the first topic (index 0)
#     # Target state: [false,true,true,true,true,true,true,true,true,true]
#     target_state = "[false,true,true,true,true,true,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableTop2Topics(_WikipediaTaskEval):
#   """Task for disabling top 2 topics in feed customization and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the top 2 topics in the feed customization settings on"
#       " Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Disable first two topics (indices 0 and 1)
#     # Target state: [false,false,true,true,true,true,true,true,true,true]
#     target_state = "[false,false,true,true,true,true,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableTop1AndRandomizer(_WikipediaTaskEval):
#   """Task for disabling top 1 and randomizer topics and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the top 1 and 'randomizer' topics in the feed customization"
#       " settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Disable first topic (index 0) and randomizer (index 6)
#     # Target state: [false,true,true,true,true,true,false,true,true,true]
#     target_state = "[false,true,true,true,true,true,false,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableTop2AndRandomizer(_WikipediaTaskEval):
#   """Task for disabling top 2 and randomizer topics and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the top 2 and 'randomizer' topics in the feed customization"
#       " settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Disable first two topics (indices 0 and 1) and randomizer (index 6)
#     # Target state: [false,false,true,true,true,true,false,true,true,true]
#     target_state = "[false,false,true,true,true,true,false,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableHistoryTopics(_WikipediaTaskEval):
#   """Task for disabling topics related to 'history' and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the topics that are related to 'history' in the feed"
#       " customization settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # History-related topics are at indices 3 and 5
#     # Target state: [true,true,true,false,true,false,true,true,true,true]
#     target_state = "[true,true,true,false,true,false,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableDayTopics(_WikipediaTaskEval):
#   """Task for disabling topics that include 'day' in their names and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the topics that include 'day' in their names in the feed"
#       " customization settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Topics with 'day' in name are at indices 2 and 5
#     # Target state: [true,true,false,true,true,false,true,true,true,true]
#     target_state = "[true,true,false,true,true,false,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableEvenIndices(_WikipediaTaskEval):
#   """Task for disabling topics with even-numbered indices and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the topics with even-numbered indices in the feed"
#       " customization settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Even indices: 0, 2, 4, 6, 8 (0-indexed)
#     # Target state: [false,true,false,true,false,true,false,true,false,true]
#     target_state = "[false,true,false,true,false,true,false,true,false,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableOddIndices(_WikipediaTaskEval):
#   """Task for disabling topics with odd-numbered indices and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the topics with odd-numbered indices in the feed"
#       " customization settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Odd indices: 1, 3, 5, 7, 9 (0-indexed)
#     # Target state: [true,false,true,false,true,false,true,false,true,true]
#     target_state = "[true,false,true,false,true,false,true,false,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisablePrimeIndices(_WikipediaTaskEval):
#   """Task for disabling topics with prime-numbered indices and returning to feed."""

#   complexity = 4.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable the topics with prime-numbered indices in the feed"
#       " customization settings on Wikipedia and go back to the feed."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Prime indices: 1, 2, 3, 5, 7 (0-indexed, but Wikipedia uses 1-indexed)
#     # Actually, looking at the evaluator, primes are: 1, 2, 3, 5, 7 (1-indexed)
#     # Which in 0-indexed are: 0, 1, 2, 4, 6
#     # Target state: [false,false,false,true,false,true,false,true,true,true]
#     target_state = "[false,false,false,true,false,true,false,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if feed_state == target_state and in_feed:
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
    # return {}


class WikipediaDisablePreviewAndFeed(_WikipediaTaskEval): # Should Work 
  """Task for disabling 'show link previews' and 'top read' feed settings and returning to feed."""

  complexity = 4.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = (
      "In the Wikipedia app, disable the 'show link previews', 'top read' feed settings, and return"
      " to the feed on Wikipedia."
  )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    show_preview = _get_show_link_previews(env)
    feed_state = _get_feed_state(env)
    state = env.get_state()
    # 'top read' is the second topic (index 1)
    # Target state: [true,false,true,true,true,true,true,true,true,true]
    target_state = "[true,false,true,true,true,true,true,true,true,true]"
    in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

    if (
        show_preview is False
        and feed_state == target_state
        and in_feed
    ):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


# class WikipediaDisableFeedAndTextSize50(_WikipediaTaskEval):
#   """Task for disabling featured article feed, decreasing text size to 50%, and returning to feed."""

#   complexity = 5.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable featured article feed, decrease the text size to 50%, and return"
#       " to the feed on Wikipedia."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     text_size = _get_text_size_multiplier(env)
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Featured article feed is the first topic (index 0)
#     # Target state: [false,true,true,true,true,true,true,true,true,true]
#     target_state = "[false,true,true,true,true,true,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if (
#         text_size == "-5"
#         and feed_state == target_state
#         and in_feed
#     ):
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}


# class WikipediaDisableFeedAndTextSize180(_WikipediaTaskEval):
#   """Task for disabling featured article feed, increasing text size to 180%, and returning to feed."""

#   complexity = 5.0
#   schema = {
#       "type": "object",
#       "properties": {},
#       "required": [],
#   }
#   template = (
#       "Disable featured article feed, increase the text size to 180%, and return"
#       " to the feed on Wikipedia."
#   )

#   def is_successful(self, env: interface.AsyncEnv) -> float:
#     text_size = _get_text_size_multiplier(env)
#     feed_state = _get_feed_state(env)
#     state = env.get_state()
#     # Featured article feed is the first topic (index 0)
#     # Target state: [false,true,true,true,true,true,true,true,true,true]
#     target_state = "[false,true,true,true,true,true,true,true,true,true]"
#     in_feed = _check_tab_selected(state, "org.wikipedia:id/nav_tab_explore")

#     if (
#         text_size == "8"
#         and feed_state == target_state
#         and in_feed
#     ):
#       return super().is_successful(env)
#     return 0.0

#   @classmethod
#   def generate_random_params(cls) -> dict[str, Any]:
#     return {}

