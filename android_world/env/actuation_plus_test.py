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

"""Unit tests for actuation_plus module."""

import time
from unittest import mock

from absl.testing import absltest
from android_world.env import actuation_plus
from android_world.env import adb_utils
from android_world.env import android_world_controller
from android_world.env import interface
from android_world.env import representation_utils


class TestGetImageWidgets(absltest.TestCase):

  def test_empty_ui_elements(self):
    """Test with no UI elements."""
    result = actuation_plus._get_image_widgets([])
    self.assertEqual(result, [])

  def test_no_image_widgets(self):
    """Test with UI elements that are not image widgets."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="android.widget.TextView",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(0, 10, 0, 10),
        ),
        representation_utils.UIElement(
            class_name="android.widget.Button",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(0, 10, 0, 10),
        ),
    ]
    result = actuation_plus._get_image_widgets(ui_elements)
    self.assertEqual(result, [])

  def test_image_button_found(self):
    """Test finding ImageButton widgets."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="android.widget.ImageButton",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(0, 50, 0, 50),
        ),
        representation_utils.UIElement(
            class_name="android.widget.TextView",
            is_clickable=False,
            bbox_pixels=representation_utils.BoundingBox(0, 10, 0, 10),
        ),
    ]
    result = actuation_plus._get_image_widgets(ui_elements)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0][0], 0)  # Index
    self.assertEqual(result[0][1].class_name, "android.widget.ImageButton")

  def test_image_button_not_clickable(self):
    """Test ImageButton that is not clickable is not included."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="android.widget.ImageButton",
            is_clickable=False,
            bbox_pixels=representation_utils.BoundingBox(0, 50, 0, 50),
        ),
    ]
    result = actuation_plus._get_image_widgets(ui_elements)
    self.assertEqual(result, [])

  def test_image_button_no_bbox(self):
    """Test ImageButton without bbox is not included."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="android.widget.ImageButton",
            is_clickable=True,
            bbox_pixels=None,
        ),
    ]
    result = actuation_plus._get_image_widgets(ui_elements)
    self.assertEqual(result, [])

  def test_custom_image_widget_classes(self):
    """Test with custom image widget classes."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="com.custom.CustomImageButton",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(0, 50, 0, 50),
        ),
    ]
    result = actuation_plus._get_image_widgets(
        ui_elements, image_widget_classes=["com.custom.CustomImageButton"]
    )
    self.assertEqual(len(result), 1)

  def test_multiple_image_widgets(self):
    """Test finding multiple image widgets."""
    ui_elements = [
        representation_utils.UIElement(
            class_name="android.widget.ImageButton",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(0, 50, 0, 50),
        ),
        representation_utils.UIElement(
            class_name="android.widget.ImageView",
            is_clickable=True,
            bbox_pixels=representation_utils.BoundingBox(100, 150, 100, 150),
        ),
    ]
    result = actuation_plus._get_image_widgets(ui_elements)
    self.assertEqual(len(result), 2)


@mock.patch.object(time, 'sleep')
@mock.patch.object(time, 'time')
@mock.patch.object(adb_utils, 'tap_screen')
class TestFindAndClickElementByImageText(absltest.TestCase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.create_autospec(
        android_world_controller.AndroidWorldController, instance=True
    )
    self.mock_env.env = mock.MagicMock()  # Mock the underlying AndroidEnvInterface

  def test_successful_find_and_click(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test successfully finding and clicking an image widget."""
    # Setup UI elements
    image_button = representation_utils.UIElement(
        class_name="android.widget.ImageButton",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=150, y_min=200, y_max=250),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [image_button]
    # Mock time.time() to return fixed values (start time, then same for loop check)
    mock_time.side_effect = [0.0, 0.0]  # start_time, then loop check

    # Execute
    actuation_plus.find_and_click_element_by_image_text(
        self.mock_env, timeout_sec=1.0
    )

    # Verify
    mock_tap_screen.assert_called_once_with(125, 225, self.mock_env.env)
    self.mock_env.get_ui_elements.assert_called()

  def test_multiple_widgets_clicks_first(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test that it clicks the first widget when multiple are found."""
    # Setup UI elements
    button1 = representation_utils.UIElement(
        class_name="android.widget.ImageButton",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=150, y_min=200, y_max=250),
    )
    button2 = representation_utils.UIElement(
        class_name="android.widget.ImageButton",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=300, x_max=350, y_min=400, y_max=450),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [button1, button2]
    # Mock time.time() to return fixed values (start time, then same for loop check)
    mock_time.side_effect = [0.0, 0.0]  # start_time, then loop check

    # Execute
    actuation_plus.find_and_click_element_by_image_text(
        self.mock_env, timeout_sec=1.0
    )

    # Should click the first one (button1)
    mock_tap_screen.assert_called_once_with(125, 225, self.mock_env.env)

  def test_timeout_no_widgets(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test timeout when no image widgets found."""
    # Setup mocks - no image widgets
    self.mock_env.get_ui_elements.return_value = []
    # Mock time.time() to simulate timeout: start at 0, then loop checks exceed timeout
    mock_time.side_effect = [0.0, 0.2]  # start_time=0.0, then loop check=0.2 (>0.1 timeout)

    # Execute and expect timeout
    with self.assertRaises(ValueError) as context:
      actuation_plus.find_and_click_element_by_image_text(
          self.mock_env, timeout_sec=0.1
      )

    self.assertIn("not found within", str(context.exception))

  def test_no_image_widgets_only_text_views(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test when no image widgets are present, only TextViews."""
    # Setup UI elements with no image widgets
    text_view = representation_utils.UIElement(
        class_name="android.widget.TextView",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=150, y_min=200, y_max=250),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [text_view]
    # Mock time.time() to simulate timeout: start at 0, then exceed timeout
    mock_time.side_effect = [0.0, 0.2]

    # Execute and expect timeout
    with self.assertRaises(ValueError):
      actuation_plus.find_and_click_element_by_image_text(
          self.mock_env, timeout_sec=0.1
      )

  def test_small_widget_not_skipped(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test that small widgets are still clicked (no size filtering)."""
    # Setup small widget
    small_button = representation_utils.UIElement(
        class_name="android.widget.ImageButton",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=105, y_min=200, y_max=205),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [small_button]
    # Mock time.time() to return fixed values
    mock_time.side_effect = [0.0, 0.0]  # start_time, then loop check

    # Execute
    actuation_plus.find_and_click_element_by_image_text(
        self.mock_env, timeout_sec=1.0
    )

    # Should click the small widget (center is at 102.5, 202.5)
    mock_tap_screen.assert_called_once_with(102, 202, self.mock_env.env)

  def test_non_clickable_widget_skipped(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test that non-clickable image widgets are skipped."""
    # Setup non-clickable image widget
    image_view = representation_utils.UIElement(
        class_name="android.widget.ImageView",
        is_clickable=False,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=150, y_min=200, y_max=250),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [image_view]
    # Mock time.time() to simulate timeout
    mock_time.side_effect = [0.0, 0.2]

    # Execute and expect timeout (non-clickable widget skipped)
    with self.assertRaises(ValueError):
      actuation_plus.find_and_click_element_by_image_text(
          self.mock_env, timeout_sec=0.1
      )
    
    # Should not click
    mock_tap_screen.assert_not_called()

  def test_widget_with_no_bbox_skipped(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test that widgets without bbox are skipped."""
    # Setup widget without bbox
    image_button = representation_utils.UIElement(
        class_name="android.widget.ImageButton",
        is_clickable=True,
        bbox_pixels=None,
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [image_button]
    # Mock time.time() to simulate timeout
    mock_time.side_effect = [0.0, 0.2]

    # Execute and expect timeout (widget without bbox skipped)
    with self.assertRaises(ValueError):
      actuation_plus.find_and_click_element_by_image_text(
          self.mock_env, timeout_sec=0.1
      )
    
    # Should not click
    mock_tap_screen.assert_not_called()

  def test_custom_image_widget_classes(
      self, mock_tap_screen, mock_time, mock_sleep
  ):
    """Test with custom image widget classes."""
    # Setup custom widget
    custom_button = representation_utils.UIElement(
        class_name="com.custom.CustomImageButton",
        is_clickable=True,
        bbox_pixels=representation_utils.BoundingBox(x_min=100, x_max=150, y_min=200, y_max=250),
    )

    # Setup mocks
    self.mock_env.get_ui_elements.return_value = [custom_button]
    # Mock time.time() to return fixed values
    mock_time.side_effect = [0.0, 0.0]  # start_time, then loop check

    # Execute with custom classes
    actuation_plus.find_and_click_element_by_image_text(
        self.mock_env,
        image_widget_classes=["com.custom.CustomImageButton"],
        timeout_sec=1.0,
    )

    # Should find and click
    mock_tap_screen.assert_called_once_with(125, 225, self.mock_env.env)


if __name__ == '__main__':
  absltest.main()

