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

"""Evaluators for Calculator app."""

from typing import Any, Optional

from android_world.env import interface
from android_world.task_evals import task_eval

PACKAGE_NAME = "com.google.android.calculator"
FORMULA_RESOURCE_ID = "com.google.android.calculator:id/formula"
RESULT_PREVIEW_RESOURCE_ID = "com.google.android.calculator:id/result_preview"
RESULT_FINAL_RESOURCE_ID = "com.google.android.calculator:id/result_final"
CLEAR_BUTTON_RESOURCE_ID = "com.google.android.calculator:id/clr"


def _check_calculator_open(state: interface.State) -> bool:
  """Check if Calculator app is open.

  Args:
    state: Current environment state.

  Returns:
    True if Calculator is open, False otherwise.
  """
  try:
    for element in state.ui_elements:
      # Check for package name or clear button resource ID
      if (element.package_name == PACKAGE_NAME or
          element.resource_id == CLEAR_BUTTON_RESOURCE_ID or
          element.resource_name == CLEAR_BUTTON_RESOURCE_ID):
        return True
    return False
  except Exception:
    return False


def _get_formula_text(state: interface.State) -> Optional[str]:
  """Get the formula text from the calculator display.

  Args:
    state: Current environment state.

  Returns:
    Formula text as string, or None if not found.
  """
  try:
    for element in state.ui_elements:
      if (element.resource_id == FORMULA_RESOURCE_ID or
          element.resource_name == FORMULA_RESOURCE_ID):
        return element.text
    return None
  except Exception:
    return None


def _get_result_text(state: interface.State) -> tuple[Optional[str], Optional[str]]:
  """Get the result text from calculator (both preview and final).

  Args:
    state: Current environment state.

  Returns:
    Tuple of (result_preview, result_final), either may be None.
  """
  result_preview = None
  result_final = None
  
  try:
    for element in state.ui_elements:
      if (element.resource_id == RESULT_PREVIEW_RESOURCE_ID or
          element.resource_name == RESULT_PREVIEW_RESOURCE_ID):
        result_preview = element.text
      elif (element.resource_id == RESULT_FINAL_RESOURCE_ID or
            element.resource_name == RESULT_FINAL_RESOURCE_ID):
        result_final = element.text
    return (result_preview, result_final)
  except Exception:
    return (None, None)


class _CalculatorTaskEval(task_eval.TaskEval):
  """Base class for Calculator-related TaskEvals."""

  app_names = ("calculator",)


class CalculatorOpen(_CalculatorTaskEval):
  """Task for opening the Calculator app."""

  complexity = 1.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "Open the Calculator app."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    if _check_calculator_open(state):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput1(_CalculatorTaskEval):
  """Task for inputting 1 in Calculator."""

  complexity = 1.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input 1."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "1":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput1Plus1(_CalculatorTaskEval):
  """Task for inputting '1+1' in Calculator."""

  complexity = 1.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '1+1'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "1+1":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput3Times5(_CalculatorTaskEval):
  """Task for inputting '3×5' in Calculator."""

  complexity = 1.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '3×5'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "3×5":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput2Plus24Div3(_CalculatorTaskEval):
  """Task for inputting '2+24÷3' in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '2+24÷3'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "2+24÷3":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput17Times23(_CalculatorTaskEval):
  """Task for inputting '17×23' in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '17×23'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "17×23":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputCos60(_CalculatorTaskEval):
  """Task for inputting 'cos(60)' in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input 'cos(60)'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "c60":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputCos180(_CalculatorTaskEval):
  """Task for inputting 'cos(180)' in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input 'cos(180)'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "c180":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputFactorial6(_CalculatorTaskEval):
  """Task for inputting factorial of 6 in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input factorial of 6."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "6!":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputSqrt25(_CalculatorTaskEval):
  """Task for inputting square root of 25 in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input square root of 25."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "√25":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputLn1234(_CalculatorTaskEval):
  """Task for inputting 'ln(1234)' in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input 'ln(1234)'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "l1234":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput5Choose2(_CalculatorTaskEval):
  """Task for inputting '5!÷(2!x3!)' in Calculator."""

  complexity = 2.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '5!÷(2!x3!)'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "5!÷(2!×3!)":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInput10Choose2(_CalculatorTaskEval):
  """Task for inputting '10!÷(2!x8!)' in Calculator."""

  complexity = 2.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, input '10!÷(2!x8!)'."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "10!÷(2!×8!)":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorInputPercent50Of28(_CalculatorTaskEval):
  """Task for computing 50% of 28 ('50%28') in Calculator."""

  complexity = 2.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, compute 50% of 28 ('50%28')."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "50%28":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorGeometricMean(_CalculatorTaskEval):
  """Task for computing the geometric mean of 3, 4, and 5 in Calculator."""

  complexity = 3.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, compute the geometric mean of 3, 4, and 5."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    result_preview, result_final = _get_result_text(state)
    # Geometric mean of 3, 4, 5 = (3*4*5)^(1/3) ≈ 3.91
    if ((result_preview is not None and result_preview.startswith("3.91")) or
        (result_final is not None and result_final.startswith("3.91"))):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorHarmonicMean(_CalculatorTaskEval):
  """Task for computing the harmonic mean of 4 and 5 in Calculator."""

  complexity = 3.0
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = "In the Calculator app, compute the harmonic mean of 4 and 5."

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    result_preview, result_final = _get_result_text(state)
    # Harmonic mean of 4 and 5 = 2/(1/4 + 1/5) = 2/(9/20) = 40/9 ≈ 4.44
    if ((result_preview is not None and result_preview.startswith("4.44")) or
        (result_final is not None and result_final.startswith("4.44"))):
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorConvert45DegreesToRadians(_CalculatorTaskEval):
  """Task for inputting the formula for converting 45 degrees to radians in Calculator."""

  complexity = 2.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = (
      "In the Calculator app, input the formula for converting 45 degrees to radians ('45xπ÷180')."
  )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "45×π÷180":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorSumFirst5Fibonacci(_CalculatorTaskEval):
  """Task for inputting the formula for computing sum of the first 5 Fibonacci numbers in Calculator."""

  complexity = 2.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = (
      "In the Calculator app, input the formula for computing sum of the first 5 Fibonacci numbers."
  )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    # Fibonacci can start with 0 or 1: 0+1+1+2+3 or 1+1+2+3+5
    if formula == "0+1+1+2+3" or formula == "1+1+2+3+5":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}


class CalculatorSumFirst5Primes(_CalculatorTaskEval):
  """Task for inputting the formula for computing sum of the first 5 prime numbers in Calculator."""

  complexity = 2.5
  schema = {
      "type": "object",
      "properties": {},
      "required": [],
  }
  template = (
      "In the Calculator app, input the formula for computing sum of the first 5 prime numbers."
  )

  def is_successful(self, env: interface.AsyncEnv) -> float:
    state = env.get_state()
    formula = _get_formula_text(state)
    if formula == "2+3+5+7+11":
      return super().is_successful(env)
    return 0.0

  @classmethod
  def generate_random_params(cls) -> dict[str, Any]:
    return {}

