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

"""Utils for capturing screenshots from Android environment for debugging."""

import os
from datetime import datetime
import cv2
import numpy as np
from absl import logging
from android_world.env import interface


def capture_screenshot(
    env: interface.AsyncEnv,
    save_dir: str = "screenshots",
    wait_to_stabilize: bool = False,
) -> str:
  """Captures a screenshot from the Android environment and saves it with timestamp.
  
  This function is primarily designed for debugging interactions with the emulator.
  It automatically generates a filename based on the current timestamp.
  
  Args:
    env: The Android environment interface (AsyncEnv).
    save_dir: Directory to save the screenshot. Default is "screenshots".
      The directory will be created if it doesn't exist.
    wait_to_stabilize: Whether to wait for the screen to stabilize before
      capturing. This is useful when the screen might be transitioning.
      
  Returns:
    The file path where the screenshot was saved.
    
  Example:
    ```python
    from android_world.utils import screenshot_utils
    
    # Capture screenshot (saved with timestamp)
    path = screenshot_utils.capture_screenshot(env)
    print(f"Screenshot saved to: {path}")
    
    # Capture with custom directory
    path = screenshot_utils.capture_screenshot(env, save_dir="debug_screenshots")
    
    # Capture with stabilization wait
    path = screenshot_utils.capture_screenshot(env, wait_to_stabilize=True)
    ```
  """
  # Get current timestamp for filename
  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
  filename = f"screenshot_{timestamp}.png"
  
  # Ensure directory exists
  os.makedirs(save_dir, exist_ok=True)
  
  # Full path
  save_path = os.path.join(save_dir, filename)
  
  # Capture screenshot
  state = env.get_state(wait_to_stabilize=wait_to_stabilize)
  screenshot = state.pixels
  
  # Convert RGB to BGR for OpenCV and save
  screenshot_bgr = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
  cv2.imwrite(save_path, screenshot_bgr)
  
  logging.info(f"Screenshot saved to {save_path}")
  
  return save_path
