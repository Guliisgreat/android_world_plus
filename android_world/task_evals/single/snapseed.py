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

"""Tasks for Snapseed app - Native AndroidWorld implementation."""

import abc
import os
import xml.etree.ElementTree as ET
from typing import Any

from absl import logging
from android_env.proto import adb_pb2
from android_world.env import adb_utils
from android_world.env import interface
from android_world.task_evals import task_eval
from android_world.utils import file_utils

PACKAGE_NAME = "com.niksoftware.snapseed"
PREFERENCES_PATH = f"/data/data/{PACKAGE_NAME}/shared_prefs/Preferences.xml"
# Debug file location (optional - validation works even if this fails)
DEBUG_PREFERENCES_FILE = "/tmp/snapseed_preferences.xml"


def _read_preferences_xml(env: interface.AsyncEnv) -> ET.Element | None:
    """Read and parse Snapseed Preferences.xml file.
    
    Optionally saves a copy to DEBUG_PREFERENCES_FILE for debugging.
    
    Args:
        env: The AndroidWorld environment.
        
    Returns:
        Root element of the XML tree, or None if reading fails.
    """
    try:
        # Ensure root access - after this, ADB is in root mode
        adb_utils.set_root_if_needed(env.controller.env)
        
        # Check if file exists on device
        if not file_utils.check_file_exists(PREFERENCES_PATH, env.controller.env):
            logging.warning("Preferences.xml file does not exist on device: %s", PREFERENCES_PATH)
            return None
        
        # Pull file content from device
        pull_response = env.controller.env.execute_adb_call(
            adb_pb2.AdbRequest(
                pull=adb_pb2.AdbRequest.Pull(path=PREFERENCES_PATH),
                timeout_sec=None,
            )
        )
        adb_utils.check_ok(pull_response)
        
        # Try to save to debug file (optional - won't break validation if it fails)
        try:
            os.makedirs(os.path.dirname(DEBUG_PREFERENCES_FILE), exist_ok=True)
            with open(DEBUG_PREFERENCES_FILE, "wb") as f:
                f.write(pull_response.pull.content)
            logging.info("Saved Preferences.xml to debug location: %s", DEBUG_PREFERENCES_FILE)
        except Exception as e:
            logging.debug("Could not save debug file (non-critical): %s", e)
        
        # Parse the XML content directly in memory
        root = ET.fromstring(pull_response.pull.content)
        
        logging.info("Successfully read Preferences.xml (root tag: %s, %d children)", 
                     root.tag, len(root))
        
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


def check_snapseed_open(state: interface.State) -> bool:
    """Check if Snapseed main screen is open.
    
    Args:
        state: Current environment state.
        
    Returns:
        True if Snapseed logo_view element exists.
    """
    try:
        for element in state.ui_elements:
            if element.resource_name == "com.niksoftware.snapseed:id/tap_to_open_hint":
                return True
        return False
    except Exception:
        return False


def check_image_open(state: interface.State) -> bool:
    """Check if an image is loaded in Snapseed.
    
    Args:
        state: Current environment state.
        
    Returns:
        True if looks_button is selected.
    """
    try:
        for element in state.ui_elements:
            if element.resource_name == "com.niksoftware.snapseed:id/looks_button":
                return element.is_selected is True
        return False
    except Exception:
        return False


def check_tools_tab(state: interface.State) -> bool:
    """Check if tools tab is active.
    
    Args:
        state: Current environment state.
        
    Returns:
        True if tools_button is selected.
    """
    try:
        for element in state.ui_elements:
            if element.resource_name == "com.niksoftware.snapseed:id/tools_button":
                return element.is_selected is True
        return False
    except Exception:
        return False


def check_filter_selected(state: interface.State, filter_name: str) -> bool:
    """Check if a specific filter is selected.
    
    Args:
        state: Current environment state.
        filter_name: Name of the filter to check (e.g., "Pop", "Portrait").
        
    Returns:
        True if the filter is selected.
    """
    try:
        for element in state.ui_elements:
            element_text = (element.text or "").strip()
            if element_text == filter_name:
                # Check if the element is selected
                if element.is_selected is True:
                    return True
        return False
    except Exception:
        return False


def check_dark_theme(env: interface.AsyncEnv) -> bool:
    """Check if dark theme is enabled.
    
    Args:
        env: The AndroidWorld environment.
        
    Returns:
        True if dark theme is enabled.
    """
    try:
        root = _read_preferences_xml(env)
        if root is None:
            return False
        
        # Search for the dark theme preference
        # Android SharedPreferences XML has <map> as root with child elements like <boolean>
        for elem in root.findall("boolean"):
            if elem.get("name") == "pref_appearance_use_dark_theme":
                return elem.get("value") == "true"
        
        return False
    except Exception as e:
        logging.warning("Error checking dark theme: %s", e)
        return False


def check_format_quality(env: interface.AsyncEnv) -> str | None:
    """Check the format quality setting.
    
    Args:
        env: The AndroidWorld environment.
        
    Returns:
        Quality value as string (e.g., "100"), or None if not found.
    """
    try:
        root = _read_preferences_xml(env)
        if root is None:
            return None
        
        for elem in root.findall("string"):
            if elem.get("name") == "pref_export_setting_compression":
                return elem.text
        return None
    except Exception:
        return None


def check_image_sizing(env: interface.AsyncEnv) -> str | None:
    """Check the image sizing setting.
    
    Args:
        env: The AndroidWorld environment.
        
    Returns:
        Sizing value as string (e.g., "2000"), or None if not found.
    """
    try:
        root = _read_preferences_xml(env)
        if root is None:
            return None
        
        for elem in root.findall("string"):
            if elem.get("name") == "pref_export_setting_long_edge":
                return elem.text
        return None
    except Exception:
        return None


class _Snapseed(task_eval.TaskEval, abc.ABC):
    """Base class for Snapseed task evaluations."""

    app_names = ("snapseed",)
    schema = {}
    template = ""

    def __init__(self, params: dict[str, Any]):
        """Initialize the task."""
        # Use task description from yaml if not provided
        if "task" in params:
            self.template = params["task"]
        super().__init__(params)

    @property
    def goal(self) -> str:
        """Returns the task goal."""
        if self.template:
            return self.template
        return self.params.get("task", "")


# Task 1: Open Snapseed
class SnapseedTask1(_Snapseed):
    """Open Snapseed."""

    complexity = 1.0
    template = "Open the Snapseed app."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if Snapseed is open."""
        state = env.get_state()
        return 1.0 if check_snapseed_open(state) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 2: Open image in Snapseed
class SnapseedTask2(_Snapseed):
    """Open image in Snapseed."""

    complexity = 1.5
    template = "In the Snapseed app, open an image."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if image is open."""
        state = env.get_state()
        return 1.0 if check_image_open(state) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 3: Open image and apply noir Pop filter
class SnapseedTask3(_Snapseed):
    """Open image and apply noir Pop filter in Snapseed."""

    complexity = 2.0
    template = "In the Snapseed app, open an image and apply noir Pop filter."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if image is open and Pop filter is applied."""
        state = env.get_state()
        image_open = check_image_open(state)
        filter_applied = check_filter_selected(state, "Pop")
        return 1.0 if (image_open and filter_applied) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 4: Open image and apply portrait filter
class SnapseedTask4(_Snapseed):
    """Open image and apply portrait filter in Snapseed."""

    complexity = 2.0
    template = "In the Snapseed app, open an image and apply portrait filter."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if image is open and Portrait filter is applied."""
        state = env.get_state()
        image_open = check_image_open(state)
        filter_applied = check_filter_selected(state, "Portrait")
        return 1.0 if (image_open and filter_applied) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 5: Open image and go to tools tab
class SnapseedTask5(_Snapseed):
    """Open image and go to tools tab in Snapseed."""

    complexity = 1.5
    template = "In the Snapseed app, open an image and go to tools tab."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if image is open and tools tab is active."""
        state = env.get_state()
        image_open = check_image_open(state)
        tools_active = check_tools_tab(state)
        return 1.0 if (image_open and tools_active) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 6: Set dark theme
class SnapseedTask6(_Snapseed):
    """Set dark theme in Snapseed."""

    complexity = 2.0
    template = "In the Snapseed app, set dark theme."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if dark theme is enabled."""
        return 1.0 if check_dark_theme(env) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 7: Set format quality to JPG 100%
class SnapseedTask7(_Snapseed):
    """Set format quality to JPG 100% in Snapseed."""

    complexity = 2.0
    template = "In the Snapseed app, set format quality to JPG 100%."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if format quality is set to 100."""
        quality = check_format_quality(env)
        return 1.0 if (quality == "100") else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 8: Set image sizing to 2000 px
class SnapseedTask8(_Snapseed):
    """Set image sizing to 2000 px in Snapseed."""

    complexity = 2.0
    template = "In the Snapseed app, set image sizing to 2000 px."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if image sizing is set to 2000."""
        sizing = check_image_sizing(env)
        return 1.0 if (sizing == "2000") else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 9: Apply noir Pop filter after setting dark theme
class SnapseedTask9(_Snapseed):
    """Apply noir Pop filter to an image after setting dark theme in Snapseed."""

    complexity = 3.0
    template = "In the Snapseed app, apply noir Pop filter to an image after setting dark theme."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if dark theme is set and Pop filter is applied."""
        state = env.get_state()
        dark_theme_enabled = check_dark_theme(env)
        filter_applied = check_filter_selected(state, "Pop")
        return 1.0 if (dark_theme_enabled and filter_applied) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 10: Apply noir Pop filter after setting format quality to JPG 100%
class SnapseedTask10(_Snapseed):
    """Apply noir Pop filter to an image after setting format quality to JPG 100% in Snapseed."""

    complexity = 3.0
    template = "In the Snapseed app, apply noir Pop filter to an image after setting format quality to JPG 100%."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if quality is 100 and Pop filter is applied."""
        state = env.get_state()
        quality = check_format_quality(env)
        filter_applied = check_filter_selected(state, "Pop")
        return 1.0 if (quality == "100" and filter_applied) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}


# Task 11: Apply noir Pop filter after setting image sizing to 2000 px
class SnapseedTask11(_Snapseed):
    """Apply noir Pop filter to an image after setting image sizing to 2000 px in Snapseed."""

    complexity = 3.0
    template = "In the Snapseed app, apply noir Pop filter to an image after setting image sizing to 2000 px."

    def is_successful(self, env: interface.AsyncEnv) -> float:
        """Check if sizing is 2000 and Pop filter is applied."""
        state = env.get_state()
        sizing = check_image_sizing(env)
        filter_applied = check_filter_selected(state, "Pop")
        return 1.0 if (sizing == "2000" and filter_applied) else 0.0

    @classmethod
    def generate_random_params(cls) -> dict[str, Any]:
        return {"task": cls.template}

