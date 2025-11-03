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

from unittest import mock
from absl.testing import absltest
from android_world.env import interface
from android_world.env import representation_utils
from android_world.task_evals.single import walmart
from android_world.utils import test_utils


class OpenWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_navigation_shop_exists(self):
    env = self.mock_env
    task = walmart.OpenWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_shop"
        ),
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/other_element"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_navigation_shop_missing(self):
    env = self.mock_env
    task = walmart.OpenWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_account"
        ),
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/other_element"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.OpenWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToAccountTabInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_tab_is_selected(self):
    env = self.mock_env
    task = walmart.GoToAccountTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_account",
            is_selected=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_tab_not_selected(self):
    env = self.mock_env
    task = walmart.GoToAccountTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_account",
            is_selected=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_is_successful_returns_zero_when_tab_missing(self):
    env = self.mock_env
    task = walmart.GoToAccountTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_shop"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToAccountTabInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToMyItemsTabInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_tab_is_selected(self):
    env = self.mock_env
    task = walmart.GoToMyItemsTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_my_items",
            is_selected=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_tab_not_selected(self):
    env = self.mock_env
    task = walmart.GoToMyItemsTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_my_items",
            is_selected=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToMyItemsTabInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToSearchTabInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_tab_is_selected(self):
    env = self.mock_env
    task = walmart.GoToSearchTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_search",
            is_selected=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_tab_not_selected(self):
    env = self.mock_env
    task = walmart.GoToSearchTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_search",
            is_selected=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToSearchTabInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToServicesTabInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_tab_is_selected(self):
    env = self.mock_env
    task = walmart.GoToServicesTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_services",
            is_selected=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_tab_not_selected(self):
    env = self.mock_env
    task = walmart.GoToServicesTabInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/navigation_services",
            is_selected=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToServicesTabInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToMyCartInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_cart_is_visible(self):
    env = self.mock_env
    task = walmart.GoToMyCartInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/cart_fragment_constraint_layout",
            is_visible=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_cart_not_visible(self):
    env = self.mock_env
    task = walmart.GoToMyCartInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/cart_fragment_constraint_layout",
            is_visible=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_is_successful_returns_zero_when_cart_missing(self):
    env = self.mock_env
    task = walmart.GoToMyCartInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/other_element"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToMyCartInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToStoreMapInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_store_map_is_visible(self):
    env = self.mock_env
    task = walmart.GoToStoreMapInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/instoremaps_webview_container",
            is_visible=True
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_store_map_not_visible(self):
    env = self.mock_env
    task = walmart.GoToStoreMapInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/instoremaps_webview_container",
            is_visible=False
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_is_successful_returns_zero_when_store_map_missing(self):
    env = self.mock_env
    task = walmart.GoToStoreMapInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/other_element"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = walmart.GoToStoreMapInWalmart.generate_random_params()
    self.assertEqual(params, {})


class GoToGroceryCategoryAndShowSubcategoriesInWalmartTest(test_utils.AdbEvalTestBase):

  def setUp(self):
    super().setUp()
    self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

  def test_is_successful_returns_one_when_grocery_category_visible(self):
    env = self.mock_env
    task = walmart.GoToGroceryCategoryAndShowSubcategoriesInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/category_container_title",
            text="Grocery"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 1.0)

  def test_is_successful_returns_zero_when_wrong_category_text(self):
    env = self.mock_env
    task = walmart.GoToGroceryCategoryAndShowSubcategoriesInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/category_container_title",
            text="Electronics"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_is_successful_returns_zero_when_category_missing(self):
    env = self.mock_env
    task = walmart.GoToGroceryCategoryAndShowSubcategoriesInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/other_element"
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_is_successful_returns_zero_when_text_is_none(self):
    env = self.mock_env
    task = walmart.GoToGroceryCategoryAndShowSubcategoriesInWalmart({})
    task.initialize_task(env)
    
    ui_elements = [
        representation_utils.UIElement(
            resource_id="com.walmart.android:id/category_container_title",
            text=None
        ),
    ]
    
    state = mock.MagicMock()
    state.ui_elements = ui_elements
    env.get_state.return_value = state
    
    self.assertEqual(task.is_successful(env), 0.0)

  def test_generate_random_params_returns_empty_dict(self):
    params = (
        walmart.GoToGroceryCategoryAndShowSubcategoriesInWalmart.generate_random_params()
    )
    self.assertEqual(params, {})


if __name__ == "__main__":
  absltest.main()

