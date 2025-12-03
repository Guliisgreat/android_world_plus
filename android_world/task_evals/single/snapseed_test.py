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

"""Tests for Snapseed task evaluations."""

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
from android_world.task_evals.single import snapseed
from android_world.utils import test_utils


class CheckDarkThemeTest(absltest.TestCase):
    """Tests for check_dark_theme function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_dark_theme_enabled(self, mock_read_xml):
        """Test when dark theme is enabled."""
        root = ET.Element('map')
        boolean_elem = ET.SubElement(root, 'boolean')
        boolean_elem.set('name', 'pref_appearance_use_dark_theme')
        boolean_elem.set('value', 'true')
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_dark_theme(self.mock_env)
        self.assertTrue(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_dark_theme_disabled(self, mock_read_xml):
        """Test when dark theme is disabled."""
        root = ET.Element('map')
        boolean_elem = ET.SubElement(root, 'boolean')
        boolean_elem.set('name', 'pref_appearance_use_dark_theme')
        boolean_elem.set('value', 'false')
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_dark_theme(self.mock_env)
        self.assertFalse(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_dark_theme_not_found(self, mock_read_xml):
        """Test when dark theme preference doesn't exist."""
        root = ET.Element('map')
        # Add other preferences but not dark theme
        other_elem = ET.SubElement(root, 'boolean')
        other_elem.set('name', 'other_pref')
        other_elem.set('value', 'true')
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_dark_theme(self.mock_env)
        self.assertFalse(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_dark_theme_empty_xml(self, mock_read_xml):
        """Test with empty XML."""
        root = ET.Element('map')
        mock_read_xml.return_value = root
        
        result = snapseed.check_dark_theme(self.mock_env)
        self.assertFalse(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_dark_theme_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = snapseed.check_dark_theme(self.mock_env)
        self.assertFalse(result)


class CheckFormatQualityTest(absltest.TestCase):
    """Tests for check_format_quality function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_format_quality_100(self, mock_read_xml):
        """Test when format quality is 100."""
        root = ET.Element('map')
        string_elem = ET.SubElement(root, 'string')
        string_elem.set('name', 'pref_export_setting_compression')
        string_elem.text = '100'
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_format_quality(self.mock_env)
        self.assertEqual(result, '100')

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_format_quality_other_value(self, mock_read_xml):
        """Test when format quality is a different value."""
        root = ET.Element('map')
        string_elem = ET.SubElement(root, 'string')
        string_elem.set('name', 'pref_export_setting_compression')
        string_elem.text = '90'
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_format_quality(self.mock_env)
        self.assertEqual(result, '90')

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_format_quality_not_found(self, mock_read_xml):
        """Test when format quality preference doesn't exist."""
        root = ET.Element('map')
        mock_read_xml.return_value = root
        
        result = snapseed.check_format_quality(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_format_quality_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = snapseed.check_format_quality(self.mock_env)
        self.assertIsNone(result)


class CheckImageSizingTest(absltest.TestCase):
    """Tests for check_image_sizing function."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_image_sizing_2000(self, mock_read_xml):
        """Test when image sizing is 2000."""
        root = ET.Element('map')
        string_elem = ET.SubElement(root, 'string')
        string_elem.set('name', 'pref_export_setting_long_edge')
        string_elem.text = '2000'
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_image_sizing(self.mock_env)
        self.assertEqual(result, '2000')

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_image_sizing_other_value(self, mock_read_xml):
        """Test when image sizing is a different value."""
        root = ET.Element('map')
        string_elem = ET.SubElement(root, 'string')
        string_elem.set('name', 'pref_export_setting_long_edge')
        string_elem.text = '1920'
        
        mock_read_xml.return_value = root
        
        result = snapseed.check_image_sizing(self.mock_env)
        self.assertEqual(result, '1920')

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_image_sizing_not_found(self, mock_read_xml):
        """Test when image sizing preference doesn't exist."""
        root = ET.Element('map')
        mock_read_xml.return_value = root
        
        result = snapseed.check_image_sizing(self.mock_env)
        self.assertIsNone(result)

    @mock.patch('android_world.task_evals.single.snapseed._read_preferences_xml')
    def test_image_sizing_read_fails(self, mock_read_xml):
        """Test when reading preferences fails."""
        mock_read_xml.return_value = None
        
        result = snapseed.check_image_sizing(self.mock_env)
        self.assertIsNone(result)


class CheckSnapseedOpenTest(absltest.TestCase):
    """Tests for check_snapseed_open function."""

    def test_snapseed_open(self):
        """Test when Snapseed logo_view element exists."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/logo_view"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_snapseed_open(state)
        self.assertTrue(result)

    def test_snapseed_not_open(self):
        """Test when Snapseed logo_view element doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.other.app:id/something"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_snapseed_open(state)
        self.assertFalse(result)

    def test_snapseed_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result = snapseed.check_snapseed_open(state)
        self.assertFalse(result)


class CheckImageOpenTest(absltest.TestCase):
    """Tests for check_image_open function."""

    def test_image_open_selected(self):
        """Test when looks_button is selected."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_image_open(state)
        self.assertTrue(result)

    def test_image_open_not_selected(self):
        """Test when looks_button exists but is not selected."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_image_open(state)
        self.assertFalse(result)

    def test_image_not_open(self):
        """Test when looks_button doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/other_button"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_image_open(state)
        self.assertFalse(result)


class CheckToolsTabTest(absltest.TestCase):
    """Tests for check_tools_tab function."""

    def test_tools_tab_selected(self):
        """Test when tools_button is selected."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/tools_button",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_tools_tab(state)
        self.assertTrue(result)

    def test_tools_tab_not_selected(self):
        """Test when tools_button exists but is not selected."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/tools_button",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_tools_tab(state)
        self.assertFalse(result)

    def test_tools_tab_not_found(self):
        """Test when tools_button doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/other_button"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_tools_tab(state)
        self.assertFalse(result)


class CheckFilterSelectedTest(absltest.TestCase):
    """Tests for check_filter_selected function."""

    def test_filter_selected(self):
        """Test when filter is selected."""
        ui_elements = [
            representation_utils.UIElement(
                text="S03",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_filter_selected(state, "S03")
        self.assertTrue(result)

    def test_filter_not_selected(self):
        """Test when filter exists but is not selected."""
        ui_elements = [
            representation_utils.UIElement(
                text="S03",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_filter_selected(state, "S03")
        self.assertFalse(result)

    def test_filter_not_found(self):
        """Test when filter doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                text="Portrait"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_filter_selected(state, "S03")
        self.assertFalse(result)

    def test_filter_text_with_whitespace(self):
        """Test when filter text has whitespace that needs stripping."""
        ui_elements = [
            representation_utils.UIElement(
                text="  S03  ",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_filter_selected(state, "S03")
        self.assertTrue(result)

    def test_filter_text_none(self):
        """Test when element text is None."""
        ui_elements = [
            representation_utils.UIElement(
                text=None,
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = snapseed.check_filter_selected(state, "S03")
        self.assertFalse(result)


class SnapseedTask1Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask1 (Open Snapseed)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_snapseed_open(self):
        """Test task succeeds when Snapseed is open."""
        task = snapseed.SnapseedTask1({"task": "Open Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/logo_view"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_snapseed_not_open(self):
        """Test task fails when Snapseed is not open."""
        task = snapseed.SnapseedTask1({"task": "Open Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.other.app:id/something"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedTask2Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask2 (Open image in Snapseed)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_image_open(self):
        """Test task succeeds when image is open."""
        task = snapseed.SnapseedTask2({"task": "Open image in Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_image_not_open(self):
        """Test task fails when image is not open."""
        task = snapseed.SnapseedTask2({"task": "Open image in Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=False
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedTask3Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask3 (Open image and apply noir S03 filter)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_both_conditions_met(self):
        """Test task succeeds when image is open and filter is applied."""
        task = snapseed.SnapseedTask3({"task": "Open image and apply noir S03 filter in Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=True
            ),
            representation_utils.UIElement(
                text="S03",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_image_not_open(self):
        """Test task fails when image is not open."""
        task = snapseed.SnapseedTask3({"task": "Open image and apply noir S03 filter in Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=False
            ),
            representation_utils.UIElement(
                text="S03",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    def test_is_successful_when_filter_not_applied(self):
        """Test task fails when filter is not applied."""
        task = snapseed.SnapseedTask3({"task": "Open image and apply noir S03 filter in Snapseed"})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.niksoftware.snapseed:id/looks_button",
                is_selected=True
            ),
            representation_utils.UIElement(
                text="Portrait",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedTask6Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask6 (Set dark theme)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed.check_dark_theme')
    def test_is_successful_when_dark_theme_enabled(self, mock_check):
        """Test task succeeds when dark theme is enabled."""
        task = snapseed.SnapseedTask6({"task": "Set dark theme in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check.return_value = True
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.snapseed.check_dark_theme')
    def test_is_successful_when_dark_theme_disabled(self, mock_check):
        """Test task fails when dark theme is disabled."""
        task = snapseed.SnapseedTask6({"task": "Set dark theme in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check.return_value = False
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedTask7Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask7 (Set format quality to JPG 100%)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed.check_format_quality')
    def test_is_successful_when_quality_100(self, mock_check):
        """Test task succeeds when quality is 100."""
        task = snapseed.SnapseedTask7({"task": "Set format quality to JPG 100% in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check.return_value = "100"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.snapseed.check_format_quality')
    def test_is_successful_when_quality_not_100(self, mock_check):
        """Test task fails when quality is not 100."""
        task = snapseed.SnapseedTask7({"task": "Set format quality to JPG 100% in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check.return_value = "90"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.snapseed.check_format_quality')
    def test_is_successful_when_quality_none(self, mock_check):
        """Test task fails when quality is None."""
        task = snapseed.SnapseedTask7({"task": "Set format quality to JPG 100% in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check.return_value = None
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedTask9Test(test_utils.AdbEvalTestBase):
    """Tests for SnapseedTask9 (Apply noir S03 filter after setting dark theme)."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.snapseed.check_dark_theme')
    def test_is_successful_when_both_conditions_met(self, mock_check_theme):
        """Test task succeeds when dark theme is set and filter is applied."""
        task = snapseed.SnapseedTask9({"task": "Apply noir S03 filter to an image after setting dark theme in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check_theme.return_value = True
        
        ui_elements = [
            representation_utils.UIElement(
                text="S03",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.snapseed.check_dark_theme')
    def test_is_successful_when_dark_theme_not_set(self, mock_check_theme):
        """Test task fails when dark theme is not set."""
        task = snapseed.SnapseedTask9({"task": "Apply noir S03 filter to an image after setting dark theme in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check_theme.return_value = False
        
        ui_elements = [
            representation_utils.UIElement(
                text="S03",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)

    @mock.patch('android_world.task_evals.single.snapseed.check_dark_theme')
    def test_is_successful_when_filter_not_applied(self, mock_check_theme):
        """Test task fails when filter is not applied."""
        task = snapseed.SnapseedTask9({"task": "Apply noir S03 filter to an image after setting dark theme in Snapseed"})
        task.initialize_task(self.mock_env)
        
        mock_check_theme.return_value = True
        
        ui_elements = [
            representation_utils.UIElement(
                text="Portrait",
                is_selected=True
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class SnapseedGenerateRandomParamsTest(absltest.TestCase):
    """Tests for generate_random_params methods."""

    def test_snapseed_task1_generate_random_params(self):
        """Test generate_random_params for SnapseedTask1."""
        params = snapseed.SnapseedTask1.generate_random_params()
        self.assertEqual(params, {"task": "Open Snapseed"})

    def test_snapseed_task6_generate_random_params(self):
        """Test generate_random_params for SnapseedTask6."""
        params = snapseed.SnapseedTask6.generate_random_params()
        self.assertEqual(params, {"task": "Set dark theme in Snapseed"})

    def test_snapseed_task9_generate_random_params(self):
        """Test generate_random_params for SnapseedTask9."""
        params = snapseed.SnapseedTask9.generate_random_params()
        expected_template = "Apply noir S03 filter to an image after setting dark theme in Snapseed"
        self.assertEqual(params, {"task": expected_template})


if __name__ == "__main__":
    absltest.main()
