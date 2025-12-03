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

"""Tests for Wikipedia task evaluations."""

# Fix import shadowing: The local calendar package shadows stdlib calendar used by requests.
# Solution: Load stdlib calendar directly from its file path before any imports.
import sys
import importlib.util
import os

def _load_stdlib_calendar():
    """Load standard library calendar module directly from Python installation."""
    # Remove local calendar package if cached
    if 'calendar' in sys.modules:
        cal = sys.modules['calendar']
        if hasattr(cal, '__file__') and cal.__file__:
            if 'android_world/task_evals/single/calendar' in cal.__file__:
                del sys.modules['calendar']
        # Also check if it's a package (has __path__) - that means it's the local one
        elif hasattr(cal, '__path__'):
            del sys.modules['calendar']
    
    # Try loading from stdlib directory using sysconfig and importlib
    try:
        import sysconfig
        import importlib
        stdlib_dir = sysconfig.get_path('stdlib')
        calendar_path = os.path.join(stdlib_dir, 'calendar.py')
        
        if os.path.exists(calendar_path):
            # Temporarily remove project paths to avoid finding local calendar package
            project_paths = []
            original_path = sys.path[:]
            for path in original_path:
                if 'android_world' in path or os.getcwd() in path:
                    if path in sys.path:
                        sys.path.remove(path)
                        project_paths.append(path)
            
            try:
                # Now import calendar - should find stdlib version
                stdlib_cal = importlib.import_module('calendar')
                # Verify it's the stdlib module (not a package - no __path__)
                if not hasattr(stdlib_cal, '__path__'):
                    sys.modules['calendar'] = stdlib_cal
                    return True
            finally:
                # Restore project paths
                sys.path[:] = original_path
    except Exception as e:
        pass
    
    # Fallback: Try using spec_from_file_location with a temp name
    try:
        import sysconfig
        stdlib_dir = sysconfig.get_path('stdlib')
        calendar_path = os.path.join(stdlib_dir, 'calendar.py')
        if os.path.exists(calendar_path):
            # Load with a temporary name first
            spec = importlib.util.spec_from_file_location('_stdlib_calendar_temp', calendar_path)
            if spec and spec.loader:
                stdlib_cal = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(stdlib_cal)
                # Now assign to calendar in sys.modules
                sys.modules['calendar'] = stdlib_cal
                return True
    except Exception:
        pass
    
    return False

# Load stdlib calendar now - must be before any android_world imports
_load_stdlib_calendar()

# Install meta_path hook to intercept calendar imports during import chain
class StdlibCalendarImporter:
    """Meta path finder that ensures stdlib calendar is always returned."""
    
    def find_spec(self, name, path, target=None):
        if name == 'calendar':
            # Ensure stdlib calendar is loaded
            if 'calendar' not in sys.modules:
                _load_stdlib_calendar()
            else:
                cal = sys.modules.get('calendar')
                if cal and hasattr(cal, '__file__') and cal.__file__:
                    if 'android_world/task_evals/single/calendar' in cal.__file__:
                        _load_stdlib_calendar()
        # Return None to let other finders handle non-calendar imports
        return None

# Add meta_path hook at the beginning (before any imports)
if not any(isinstance(f, StdlibCalendarImporter) for f in sys.meta_path):
    sys.meta_path.insert(0, StdlibCalendarImporter())

# Now we can safely import other modules
import xml.etree.ElementTree as ET
from unittest import mock
from absl.testing import absltest
from android_world.env import interface
from android_world.env import representation_utils
from android_world.task_evals.single import wikipedia
from android_world.utils import test_utils


class GetTextSizeMultiplierTest(absltest.TestCase):
    """Tests for _get_text_size_multiplier function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_text_size_multiplier_8(self, mock_read_xml):
        """Test when text size multiplier is 8 (180%)."""
        root = ET.Element('map')
        int_elem = ET.SubElement(root, 'int')
        int_elem.set('name', 'textSizeMultiplier')
        int_elem.set('value', '8')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_text_size_multiplier(self.mock_env)
        self.assertEqual(result, '8')

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_text_size_multiplier_minus5(self, mock_read_xml):
        """Test when text size multiplier is -5 (50%)."""
        root = ET.Element('map')
        int_elem = ET.SubElement(root, 'int')
        int_elem.set('name', 'textSizeMultiplier')
        int_elem.set('value', '-5')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_text_size_multiplier(self.mock_env)
        self.assertEqual(result, '-5')

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_text_size_multiplier_not_found(self, mock_read_xml):
        """Test when text size multiplier preference doesn't exist."""
        root = ET.Element('map')
        # Add other preferences but not textSizeMultiplier
        other_elem = ET.SubElement(root, 'boolean')
        other_elem.set('name', 'other_pref')
        other_elem.set('value', 'true')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_text_size_multiplier(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_text_size_multiplier_empty_xml(self, mock_read_xml):
        """Test with empty XML."""
        root = ET.Element('map')
        mock_read_xml.return_value = root
        
        result = wikipedia._get_text_size_multiplier(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_text_size_multiplier_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = wikipedia._get_text_size_multiplier(self.mock_env)
        self.assertIsNone(result)


class GetFeedStateTest(absltest.TestCase):
    """Tests for _get_feed_state function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_feed_state_found(self, mock_read_xml):
        """Test when feed state is found."""
        root = ET.Element('map')
        # Add some elements
        elem1 = ET.SubElement(root, 'boolean')
        elem1.set('name', 'pref1')
        elem2 = ET.SubElement(root, 'string')
        elem2.set('name', 'feed_state')
        elem2.text = '[true,false,true,true,true,true,true,true,true,true]'
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_feed_state(self.mock_env)
        self.assertEqual(result, '[true,false,true,true,true,true,true,true,true,true]')

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_feed_state_empty_xml(self, mock_read_xml):
        """Test with empty XML."""
        root = ET.Element('map')
        mock_read_xml.return_value = root
        
        result = wikipedia._get_feed_state(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_feed_state_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = wikipedia._get_feed_state(self.mock_env)
        self.assertIsNone(result)


class GetShowLinkPreviewsTest(absltest.TestCase):
    """Tests for _get_show_link_previews function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_show_link_previews_enabled(self, mock_read_xml):
        """Test when show link previews is enabled."""
        root = ET.Element('map')
        boolean_elem = ET.SubElement(root, 'boolean')
        boolean_elem.set('name', 'showLinkPreviews')
        boolean_elem.set('value', 'true')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_show_link_previews(self.mock_env)
        self.assertTrue(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_show_link_previews_disabled(self, mock_read_xml):
        """Test when show link previews is disabled."""
        root = ET.Element('map')
        boolean_elem = ET.SubElement(root, 'boolean')
        boolean_elem.set('name', 'showLinkPreviews')
        boolean_elem.set('value', 'false')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_show_link_previews(self.mock_env)
        self.assertFalse(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_show_link_previews_not_found(self, mock_read_xml):
        """Test when show link previews preference doesn't exist."""
        root = ET.Element('map')
        # Add other preferences but not showLinkPreviews
        other_elem = ET.SubElement(root, 'boolean')
        other_elem.set('name', 'other_pref')
        other_elem.set('value', 'true')
        
        mock_read_xml.return_value = root
        
        result = wikipedia._get_show_link_previews(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.wikipedia._read_preferences_xml')
    def test_show_link_previews_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = wikipedia._get_show_link_previews(self.mock_env)
        self.assertIsNone(result)


class CheckTabSelectedTest(absltest.TestCase):
    """Tests for _check_tab_selected function."""

    def test_tab_selected_by_resource_id(self):
        """Test when tab is selected by resource_id."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_search",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_tab_selected(state, "org.wikipedia:id/nav_tab_search")
        self.assertTrue(result)

    def test_tab_selected_by_resource_name(self):
        """Test when tab is selected by resource_name."""
        ui_elements = [
            representation_utils.UIElement(
                resource_name="org.wikipedia:id/nav_tab_search",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_tab_selected(state, "org.wikipedia:id/nav_tab_search")
        self.assertTrue(result)

    def test_tab_not_selected(self):
        """Test when tab exists but is not selected."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_search",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_tab_selected(state, "org.wikipedia:id/nav_tab_search")
        self.assertFalse(result)

    def test_tab_not_found(self):
        """Test when tab doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/other_tab"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_tab_selected(state, "org.wikipedia:id/nav_tab_search")
        self.assertFalse(result)

    def test_tab_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result = wikipedia._check_tab_selected(state, "org.wikipedia:id/nav_tab_search")
        self.assertFalse(result)


class CheckWikipediaOpenTest(absltest.TestCase):
    """Tests for _check_wikipedia_open function."""

    def test_wikipedia_open(self):
        """Test when Wikipedia app is open."""
        ui_elements = [
            representation_utils.UIElement(
                package_name="org.wikipedia"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_wikipedia_open(state)
        self.assertTrue(result)

    def test_wikipedia_not_open(self):
        """Test when Wikipedia app is not open."""
        ui_elements = [
            representation_utils.UIElement(
                package_name="com.other.app"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = wikipedia._check_wikipedia_open(state)
        self.assertFalse(result)

    def test_wikipedia_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result = wikipedia._check_wikipedia_open(state)
        self.assertFalse(result)


class WikipediaOpenTest(test_utils.AdbEvalTestBase):
    """Tests for WikipediaOpen task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_wikipedia_open(self):
        """Test task succeeds when Wikipedia is open."""
        task = wikipedia.WikipediaOpen({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                package_name="org.wikipedia"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_wikipedia_not_open(self):
        """Test task fails when Wikipedia is not open."""
        task = wikipedia.WikipediaOpen({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                package_name="com.other.app"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaGoToSearchTabTest(test_utils.AdbEvalTestBase):
    """Tests for WikipediaGoToSearchTab task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_tab_selected(self):
        """Test task succeeds when search tab is selected."""
        task = wikipedia.WikipediaGoToSearchTab({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_search",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_tab_not_selected(self):
        """Test task fails when search tab is not selected."""
        task = wikipedia.WikipediaGoToSearchTab({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_search",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaGoToSavedTabTest(test_utils.AdbEvalTestBase):
    """Tests for WikipediaGoToSavedTab task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_tab_selected(self):
        """Test task succeeds when saved tab is selected."""
        task = wikipedia.WikipediaGoToSavedTab({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_reading_lists",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_tab_not_selected(self):
        """Test task fails when saved tab is not selected."""
        task = wikipedia.WikipediaGoToSavedTab({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="org.wikipedia:id/nav_tab_reading_lists",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaIncreaseTextSize180Test(test_utils.AdbEvalTestBase):
    """Tests for WikipediaIncreaseTextSize180 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_180(self, mock_get_text_size):
        """Test task succeeds when text size is 180%."""
        task = wikipedia.WikipediaIncreaseTextSize180({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = "8"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_not_180(self, mock_get_text_size):
        """Test task fails when text size is not 180%."""
        task = wikipedia.WikipediaIncreaseTextSize180({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = "0"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_none(self, mock_get_text_size):
        """Test task fails when text size is None (default)."""
        task = wikipedia.WikipediaIncreaseTextSize180({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = None
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaDecreaseTextSize50Test(test_utils.AdbEvalTestBase):
    """Tests for WikipediaDecreaseTextSize50 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_50(self, mock_get_text_size):
        """Test task succeeds when text size is 50%."""
        task = wikipedia.WikipediaDecreaseTextSize50({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = "-5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_not_50(self, mock_get_text_size):
        """Test task fails when text size is not 50%."""
        task = wikipedia.WikipediaDecreaseTextSize50({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = "0"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.wikipedia._get_text_size_multiplier')
    def test_is_successful_when_text_size_none(self, mock_get_text_size):
        """Test task fails when text size is None (default)."""
        task = wikipedia.WikipediaDecreaseTextSize50({})
        task.initialize_task(self.mock_env)
        
        mock_get_text_size.return_value = None
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaDisablePreviewAndFeedTest(test_utils.AdbEvalTestBase):
    """Tests for WikipediaDisablePreviewAndFeed task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.wikipedia._check_tab_selected')
    @mock.patch('android_world.task_evals.single.wikipedia._get_feed_state')
    @mock.patch('android_world.task_evals.single.wikipedia._get_show_link_previews')
    def test_is_successful_when_all_conditions_met(self, mock_get_preview, mock_get_feed, mock_check_tab):
        """Test task succeeds when all conditions are met."""
        task = wikipedia.WikipediaDisablePreviewAndFeed({})
        task.initialize_task(self.mock_env)
        
        mock_get_preview.return_value = False
        mock_get_feed.return_value = "[true,false,true,true,true,true,true,true,true,true]"
        mock_check_tab.return_value = True
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.wikipedia._check_tab_selected')
    @mock.patch('android_world.task_evals.single.wikipedia._get_feed_state')
    @mock.patch('android_world.task_evals.single.wikipedia._get_show_link_previews')
    def test_is_successful_when_preview_enabled(self, mock_get_preview, mock_get_feed, mock_check_tab):
        """Test task fails when preview is enabled."""
        task = wikipedia.WikipediaDisablePreviewAndFeed({})
        task.initialize_task(self.mock_env)
        
        mock_get_preview.return_value = True
        mock_get_feed.return_value = "[true,false,true,true,true,true,true,true,true,true]"
        mock_check_tab.return_value = True
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.wikipedia._check_tab_selected')
    @mock.patch('android_world.task_evals.single.wikipedia._get_feed_state')
    @mock.patch('android_world.task_evals.single.wikipedia._get_show_link_previews')
    def test_is_successful_when_feed_state_wrong(self, mock_get_preview, mock_get_feed, mock_check_tab):
        """Test task fails when feed state is wrong."""
        task = wikipedia.WikipediaDisablePreviewAndFeed({})
        task.initialize_task(self.mock_env)
        
        mock_get_preview.return_value = False
        mock_get_feed.return_value = "[true,true,true,true,true,true,true,true,true,true]"
        mock_check_tab.return_value = True
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.wikipedia._check_tab_selected')
    @mock.patch('android_world.task_evals.single.wikipedia._get_feed_state')
    @mock.patch('android_world.task_evals.single.wikipedia._get_show_link_previews')
    def test_is_successful_when_not_in_feed(self, mock_get_preview, mock_get_feed, mock_check_tab):
        """Test task fails when not in feed tab."""
        task = wikipedia.WikipediaDisablePreviewAndFeed({})
        task.initialize_task(self.mock_env)
        
        mock_get_preview.return_value = False
        mock_get_feed.return_value = "[true,false,true,true,true,true,true,true,true,true]"
        mock_check_tab.return_value = False
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class WikipediaGenerateRandomParamsTest(absltest.TestCase):
    """Tests for generate_random_params methods."""

    def test_wikipedia_open_generate_random_params(self):
        """Test generate_random_params for WikipediaOpen."""
        params = wikipedia.WikipediaOpen.generate_random_params()
        self.assertEqual(params, {})

    def test_wikipedia_go_to_search_tab_generate_random_params(self):
        """Test generate_random_params for WikipediaGoToSearchTab."""
        params = wikipedia.WikipediaGoToSearchTab.generate_random_params()
        self.assertEqual(params, {})

    def test_wikipedia_increase_text_size_180_generate_random_params(self):
        """Test generate_random_params for WikipediaIncreaseTextSize180."""
        params = wikipedia.WikipediaIncreaseTextSize180.generate_random_params()
        self.assertEqual(params, {})

    def test_wikipedia_disable_preview_and_feed_generate_random_params(self):
        """Test generate_random_params for WikipediaDisablePreviewAndFeed."""
        params = wikipedia.WikipediaDisablePreviewAndFeed.generate_random_params()
        self.assertEqual(params, {})


if __name__ == "__main__":
    absltest.main()

