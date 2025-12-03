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

"""Extended actuation utilities for finding and clicking image widgets."""

import logging
import time

from android_world.env import adb_utils
from android_world.env import android_world_controller
from android_world.env import interface
from android_world.env import representation_utils


# Default image widget classes to search for
_DEFAULT_IMAGE_WIDGET_CLASSES = [
    "android.widget.ImageButton",
    "android.widget.ImageView",
    "androidx.appcompat.widget.AppCompatImageButton",
]


def _get_image_widgets(
    ui_elements: list[representation_utils.UIElement],
    image_widget_classes: list[str] | None = None,
) -> list[tuple[int, representation_utils.UIElement]]:
    """Filter UI elements to find image widgets.

    Args:
        ui_elements: List of UI elements to search.
        image_widget_classes: List of class names to consider. If None, uses default set.

    Returns:
        List of (index, element) tuples for image widgets with valid bbox and clickable.
    """
    if image_widget_classes is None:
        image_widget_classes = _DEFAULT_IMAGE_WIDGET_CLASSES

    image_widgets = []
    for i, elem in enumerate(ui_elements):
        if (
            elem.class_name in image_widget_classes
            and elem.is_clickable
            and elem.bbox_pixels is not None
        ):
            image_widgets.append((i, elem))

    return image_widgets


def find_and_click_element_by_image_text(
    env: android_world_controller.AndroidWorldController,
    image_widget_classes: list[str] | None = None,
    timeout_sec: float = 10.0,
) -> None:
    """Find and click a clickable image widget (ImageButton, ImageView, etc.).

    This function identifies clickable image widgets and clicks the first one found.
    No OCR is used - it simply finds clickable image widgets of the specified class.

    Args:
        env: The Android environment controller (AndroidWorldController) or AsyncEnv.
        image_widget_classes: List of class names to consider (e.g.,
            ["android.widget.ImageButton"]). If None, uses default set.
        timeout_sec: Maximum time to wait for element to appear.

    Raises:
        ValueError: If no clickable image widget found within timeout.
    """
    # Determine if env is AsyncEnv or AndroidWorldController
    is_async_env = isinstance(env, interface.AsyncEnv)
    if is_async_env:
        controller = env.controller
        tap_env = env.controller.env  # Use underlying AndroidEnvInterface for tap_screen
    else:
        controller = env
        tap_env = controller.env  # Use underlying AndroidEnvInterface for tap_screen

    start_time = time.time()

    while time.time() - start_time < timeout_sec:
        # Get UI elements (always works correctly via direct ADB query)
        ui_elements = controller.get_ui_elements()

        # Find image widgets (clickable ImageButton, ImageView, etc.)
        image_widgets = _get_image_widgets(ui_elements, image_widget_classes)

        if not image_widgets:
            time.sleep(0.5)
            continue

        # Click the first clickable image widget found
        idx, element = image_widgets[0]
        x, y = element.bbox_pixels.center
        adb_utils.tap_screen(int(x), int(y), tap_env)
        logging.info(
            f"Clicked image widget (class: {element.class_name}, index: {idx})"
        )
        return

    # Timeout
    raise ValueError(
        f"Clickable image widget not found within {timeout_sec}s"
    )

