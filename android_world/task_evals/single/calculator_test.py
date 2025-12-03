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

"""Tests for Calculator task evaluations."""

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
from unittest import mock
from absl.testing import absltest
from android_world.env import interface
from android_world.env import representation_utils
from android_world.task_evals.single import calculator
from android_world.utils import test_utils


class CheckCalculatorOpenTest(absltest.TestCase):
    """Tests for _check_calculator_open function."""

    def test_calculator_open_by_package_name(self):
        """Test when Calculator is open (detected by package name)."""
        ui_elements = [
            representation_utils.UIElement(
                package_name="com.google.android.calculator"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._check_calculator_open(state)
        self.assertTrue(result)

    def test_calculator_open_by_clear_button_resource_id(self):
        """Test when Calculator is open (detected by clear button resource_id)."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/clr"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._check_calculator_open(state)
        self.assertTrue(result)

    def test_calculator_open_by_clear_button_resource_name(self):
        """Test when Calculator is open (detected by clear button resource_name)."""
        ui_elements = [
            representation_utils.UIElement(
                resource_name="com.google.android.calculator:id/clr"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._check_calculator_open(state)
        self.assertTrue(result)

    def test_calculator_not_open(self):
        """Test when Calculator is not open."""
        ui_elements = [
            representation_utils.UIElement(
                package_name="com.other.app"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._check_calculator_open(state)
        self.assertFalse(result)

    def test_calculator_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result = calculator._check_calculator_open(state)
        self.assertFalse(result)


class GetFormulaTextTest(absltest.TestCase):
    """Tests for _get_formula_text function."""

    def test_formula_text_found_by_resource_id(self):
        """Test when formula text is found by resource_id."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/formula",
                text="1+1"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._get_formula_text(state)
        self.assertEqual(result, "1+1")

    def test_formula_text_found_by_resource_name(self):
        """Test when formula text is found by resource_name."""
        ui_elements = [
            representation_utils.UIElement(
                resource_name="com.google.android.calculator:id/formula",
                text="3×5"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._get_formula_text(state)
        self.assertEqual(result, "3×5")

    def test_formula_text_not_found(self):
        """Test when formula element doesn't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/other"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result = calculator._get_formula_text(state)
        self.assertIsNone(result)

    def test_formula_text_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result = calculator._get_formula_text(state)
        self.assertIsNone(result)


class GetResultTextTest(absltest.TestCase):
    """Tests for _get_result_text function."""

    def test_result_text_preview_found(self):
        """Test when result preview is found."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/result_preview",
                text="2"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result_preview, result_final = calculator._get_result_text(state)
        self.assertEqual(result_preview, "2")
        self.assertIsNone(result_final)

    def test_result_text_final_found(self):
        """Test when result final is found."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/result_final",
                text="3.91"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result_preview, result_final = calculator._get_result_text(state)
        self.assertIsNone(result_preview)
        self.assertEqual(result_final, "3.91")

    def test_result_text_both_found(self):
        """Test when both preview and final are found."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/result_preview",
                text="2"
            ),
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/result_final",
                text="2"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result_preview, result_final = calculator._get_result_text(state)
        self.assertEqual(result_preview, "2")
        self.assertEqual(result_final, "2")

    def test_result_text_not_found(self):
        """Test when result elements don't exist."""
        ui_elements = [
            representation_utils.UIElement(
                resource_id="com.google.android.calculator:id/other"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        
        result_preview, result_final = calculator._get_result_text(state)
        self.assertIsNone(result_preview)
        self.assertIsNone(result_final)

    def test_result_text_empty_ui_elements(self):
        """Test with empty UI elements list."""
        state = mock.MagicMock()
        state.ui_elements = []
        
        result_preview, result_final = calculator._get_result_text(state)
        self.assertIsNone(result_preview)
        self.assertIsNone(result_final)


class CalculatorOpenTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorOpen task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    def test_is_successful_when_calculator_open(self):
        """Test task succeeds when Calculator is open."""
        task = calculator.CalculatorOpen({})
        task.initialize_task(self.mock_env)
        
        ui_elements = [
            representation_utils.UIElement(
                package_name="com.google.android.calculator"
            ),
        ]
        
        state = mock.MagicMock()
        state.ui_elements = ui_elements
        self.mock_env.get_state.return_value = state
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    def test_is_successful_when_calculator_not_open(self):
        """Test task fails when Calculator is not open."""
        task = calculator.CalculatorOpen({})
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


class CalculatorInput1Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInput1 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_1(self, mock_get_formula):
        """Test task succeeds when formula is '1'."""
        task = calculator.CalculatorInput1({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "1"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_1(self, mock_get_formula):
        """Test task fails when formula is not '1'."""
        task = calculator.CalculatorInput1({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "2"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorInput1Plus1Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInput1Plus1 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_1_plus_1(self, mock_get_formula):
        """Test task succeeds when formula is '1+1'."""
        task = calculator.CalculatorInput1Plus1({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "1+1"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_1_plus_1(self, mock_get_formula):
        """Test task fails when formula is not '1+1'."""
        task = calculator.CalculatorInput1Plus1({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "2+2"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorInput3Times5Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInput3Times5 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_3_times_5(self, mock_get_formula):
        """Test task succeeds when formula is '3×5'."""
        task = calculator.CalculatorInput3Times5({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "3×5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_3_times_5(self, mock_get_formula):
        """Test task fails when formula is not '3×5'."""
        task = calculator.CalculatorInput3Times5({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "3+5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorInputCos60Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInputCos60 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_c60(self, mock_get_formula):
        """Test task succeeds when formula is 'c60'."""
        task = calculator.CalculatorInputCos60({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "c60"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_c60(self, mock_get_formula):
        """Test task fails when formula is not 'c60'."""
        task = calculator.CalculatorInputCos60({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "cos(60)"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorInputFactorial6Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInputFactorial6 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_6_factorial(self, mock_get_formula):
        """Test task succeeds when formula is '6!'."""
        task = calculator.CalculatorInputFactorial6({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "6!"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_6_factorial(self, mock_get_formula):
        """Test task fails when formula is not '6!'."""
        task = calculator.CalculatorInputFactorial6({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "5!"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorInputSqrt25Test(test_utils.AdbEvalTestBase):
    """Tests for CalculatorInputSqrt25 task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_sqrt_25(self, mock_get_formula):
        """Test task succeeds when formula is '√25'."""
        task = calculator.CalculatorInputSqrt25({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "√25"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_not_sqrt_25(self, mock_get_formula):
        """Test task fails when formula is not '√25'."""
        task = calculator.CalculatorInputSqrt25({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "√16"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorGeometricMeanTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorGeometricMean task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_preview_starts_with_391(self, mock_get_result):
        """Test task succeeds when result preview starts with '3.91'."""
        task = calculator.CalculatorGeometricMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = ("3.91", None)
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_final_starts_with_391(self, mock_get_result):
        """Test task succeeds when result final starts with '3.91'."""
        task = calculator.CalculatorGeometricMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = (None, "3.91")
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_does_not_start_with_391(self, mock_get_result):
        """Test task fails when result doesn't start with '3.91'."""
        task = calculator.CalculatorGeometricMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = ("4.0", None)
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorHarmonicMeanTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorHarmonicMean task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_preview_starts_with_444(self, mock_get_result):
        """Test task succeeds when result preview starts with '4.44'."""
        task = calculator.CalculatorHarmonicMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = ("4.44", None)
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_final_starts_with_444(self, mock_get_result):
        """Test task succeeds when result final starts with '4.44'."""
        task = calculator.CalculatorHarmonicMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = (None, "4.44")
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_result_text')
    def test_is_successful_when_result_does_not_start_with_444(self, mock_get_result):
        """Test task fails when result doesn't start with '4.44'."""
        task = calculator.CalculatorHarmonicMean({})
        task.initialize_task(self.mock_env)
        
        mock_get_result.return_value = ("4.5", None)
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorConvert45DegreesToRadiansTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorConvert45DegreesToRadians task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_correct(self, mock_get_formula):
        """Test task succeeds when formula is '45×π÷180'."""
        task = calculator.CalculatorConvert45DegreesToRadians({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "45×π÷180"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_incorrect(self, mock_get_formula):
        """Test task fails when formula is incorrect."""
        task = calculator.CalculatorConvert45DegreesToRadians({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "45*pi/180"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorSumFirst5FibonacciTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorSumFirst5Fibonacci task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_0_1_1_2_3(self, mock_get_formula):
        """Test task succeeds when formula is '0+1+1+2+3'."""
        task = calculator.CalculatorSumFirst5Fibonacci({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "0+1+1+2+3"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_1_1_2_3_5(self, mock_get_formula):
        """Test task succeeds when formula is '1+1+2+3+5'."""
        task = calculator.CalculatorSumFirst5Fibonacci({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "1+1+2+3+5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_incorrect(self, mock_get_formula):
        """Test task fails when formula is incorrect."""
        task = calculator.CalculatorSumFirst5Fibonacci({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "1+2+3+4+5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorSumFirst5PrimesTest(test_utils.AdbEvalTestBase):
    """Tests for CalculatorSumFirst5Primes task."""

    def setUp(self):
        super().setUp()
        self.mock_env = mock.MagicMock(spec=interface.AsyncEnv)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_correct(self, mock_get_formula):
        """Test task succeeds when formula is '2+3+5+7+11'."""
        task = calculator.CalculatorSumFirst5Primes({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "2+3+5+7+11"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 1.0)

    @mock.patch('android_world.task_evals.single.calculator._get_formula_text')
    def test_is_successful_when_formula_is_incorrect(self, mock_get_formula):
        """Test task fails when formula is incorrect."""
        task = calculator.CalculatorSumFirst5Primes({})
        task.initialize_task(self.mock_env)
        
        mock_get_formula.return_value = "1+2+3+4+5"
        
        result = task.is_successful(self.mock_env)
        self.assertEqual(result, 0.0)


class CalculatorGenerateRandomParamsTest(absltest.TestCase):
    """Tests for generate_random_params methods."""

    def test_calculator_open_generate_random_params(self):
        """Test generate_random_params for CalculatorOpen."""
        params = calculator.CalculatorOpen.generate_random_params()
        self.assertEqual(params, {})

    def test_calculator_input_1_generate_random_params(self):
        """Test generate_random_params for CalculatorInput1."""
        params = calculator.CalculatorInput1.generate_random_params()
        self.assertEqual(params, {})

    def test_calculator_geometric_mean_generate_random_params(self):
        """Test generate_random_params for CalculatorGeometricMean."""
        params = calculator.CalculatorGeometricMean.generate_random_params()
        self.assertEqual(params, {})

    def test_calculator_convert_45_degrees_generate_random_params(self):
        """Test generate_random_params for CalculatorConvert45DegreesToRadians."""
        params = calculator.CalculatorConvert45DegreesToRadians.generate_random_params()
        self.assertEqual(params, {})


if __name__ == "__main__":
    absltest.main()

