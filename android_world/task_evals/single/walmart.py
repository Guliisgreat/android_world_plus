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

"""Tasks for the Walmart app."""

from typing import Any
from android_world.env import interface
from android_world.task_evals import task_eval


class _WalmartEval(task_eval.TaskEval):
  """Base class for Walmart tasks."""

  app_names = ("walmart",)


class OpenWalmart(_WalmartEval):
  """Task for opening Walmart app and verifying home screen is visible."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Open Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if element.resource_id == "com.walmart.android:id/navigation_shop":
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToAccountTabInWalmart(_WalmartEval):
  """Task for navigating to the account tab in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to the account tab in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id == "com.walmart.android:id/navigation_account"
          and element.is_selected is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToMyItemsTabInWalmart(_WalmartEval):
  """Task for navigating to the my items tab in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to the my items tab in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id == "com.walmart.android:id/navigation_my_items"
          and element.is_selected is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToSearchTabInWalmart(_WalmartEval):
  """Task for navigating to the search tab in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to the search tab in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id == "com.walmart.android:id/navigation_search"
          and element.is_selected is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToServicesTabInWalmart(_WalmartEval):
  """Task for navigating to the services tab in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to the services tab in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id == "com.walmart.android:id/navigation_services"
          and element.is_selected is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToMyCartInWalmart(_WalmartEval):
  """Task for navigating to the cart page in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to my cart in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id
          == "com.walmart.android:id/cart_fragment_constraint_layout"
          and element.is_visible is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToStoreMapInWalmart(_WalmartEval):
  """Task for navigating to the store map in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = "Go to the store map in Walmart."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id
          == "com.walmart.android:id/instoremaps_webview_container"
          and element.is_visible is True
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class GoToGroceryCategoryAndShowSubcategoriesInWalmart(_WalmartEval):
  """Task for navigating to grocery category and showing subcategories in Walmart."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
  }
  template = (
      "Go to grocery category and show subcategories in Walmart."
  )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    super().is_successful(env)
    ui_elements = env.get_state().ui_elements

    for element in ui_elements:
      if (
          element.resource_id
          == "com.walmart.android:id/category_container_title"
          and element.text == "Grocery"
      ):
        return 1.0

    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}

