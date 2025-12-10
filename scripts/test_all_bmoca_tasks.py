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

"""Test BMOCA app tasks (Calculator, Snapseed, Wikipedia) with M3A or T3A agent.

This script can test individual tasks or all tasks from Calculator, Snapseed,
or Wikipedia apps using M3A (multimodal) or T3A (text-only) agents with GPT-4o.
Useful for testing and debugging BMOCA tasks.

Usage:
    # List available tasks for an app
    python scripts/test_all_bmoca_tasks.py --app calculator
    
    # Run a specific task with M3A (default)
    python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorInput1Plus1
    
    # Run a specific task with T3A (text-only, cheaper)
    python scripts/test_all_bmoca_tasks.py --app calculator --task CalculatorInput1Plus1 --agent t3a
    
    # Run ALL tasks for an app
    python scripts/test_all_bmoca_tasks.py --app calculator --run_all
    
    # Run ALL tasks with T3A agent
    python scripts/test_all_bmoca_tasks.py --app calculator --run_all --agent t3a
    
    # Run ALL tasks and save report to JSON file
    python scripts/test_all_bmoca_tasks.py --app calculator --run_all --report results/calculator_m3a.json
"""

from collections.abc import Sequence
from datetime import datetime
import json
import os
import sys
from typing import Type

# Add project root to Python path so we can import android_world
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SCRIPT_DIR)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# Set environment variables before any imports
os.environ['GRPC_VERBOSITY'] = 'ERROR'  # Only show errors
os.environ['GRPC_TRACE'] = 'none'  # Disable tracing

# Check for required dependencies before importing
def _check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import android_env
    except ImportError:
        missing.append('android_env')
    
    try:
        import absl
    except ImportError:
        missing.append('absl-py')
    
    if missing:
        print('=' * 80)
        print('ERROR: Missing required dependencies')
        print('=' * 80)
        print(f'Missing packages: {", ".join(missing)}')
        print()
        print('Please install dependencies using one of the following:')
        print('  1. Install from requirements.txt:')
        print('     pip install -r requirements.txt')
        print()
        print('  2. Install in development mode:')
        print('     pip install -e .')
        print()
        print('  3. Or ensure you are in the correct conda/virtual environment')
        print('     that has android_world dependencies installed.')
        print()
        print('Current Python environment:')
        print(f'  Python: {sys.executable}')
        print(f'  Python path: {sys.path[:3]}...')
        print()
        # Check if we're in base conda environment and suggest activating aw_plus
        if 'base' in sys.executable or 'anaconda3' in sys.executable:
            print('⚠️  You appear to be in the base conda environment.')
            print('   Try activating the correct environment first:')
            print('     conda activate aw_plus  # or your android_world environment')
            print()
        print('=' * 80)
        sys.exit(1)

# Check dependencies before proceeding
_check_dependencies()

from absl import app
from absl import flags
from absl import logging
from android_world import constants
from android_world import episode_runner
from android_world import registry
from android_world.agents import infer
from android_world.agents import m3a
from android_world.agents import t3a
from android_world.env import env_launcher
from android_world.task_evals import task_eval

logging.set_verbosity(logging.WARNING)

# All available BMOCA tasks by app
_CALCULATOR_TASKS = [
    'CalculatorOpen',
    'CalculatorInput1',
    'CalculatorInput1Plus1',
    'CalculatorInput3Times5',
    'CalculatorInput2Plus24Div3',
    'CalculatorInput17Times23',
    'CalculatorInputCos60',
    'CalculatorInputCos180',
    'CalculatorInputFactorial6',
    'CalculatorInputSqrt25',
    'CalculatorInputLn1234',
    'CalculatorInput5Choose2',
    'CalculatorInput10Choose2',
    'CalculatorInputPercent50Of28',
    'CalculatorGeometricMean',
    'CalculatorHarmonicMean',
    'CalculatorConvert45DegreesToRadians',
    'CalculatorSumFirst5Fibonacci',
    'CalculatorSumFirst5Primes',
]

_SNAPSEED_TASKS = [
    'SnapseedTask1',
    'SnapseedTask2',
    'SnapseedTask3',
    'SnapseedTask4',
    'SnapseedTask5',
    'SnapseedTask6',
    'SnapseedTask7',
    'SnapseedTask8',
    'SnapseedTask9',
    'SnapseedTask10',
    'SnapseedTask11',
]

_WIKIPEDIA_TASKS = [
    'WikipediaOpen',
    'WikipediaGoToSearchTab',
    'WikipediaGoToSavedTab',
    'WikipediaIncreaseTextSize180',
    'WikipediaDisablePreviewAndFeed',
]

# Combined list of all BMOCA tasks
_ALL_BMOCA_TASKS = _CALCULATOR_TASKS + _SNAPSEED_TASKS + _WIKIPEDIA_TASKS

# App name to task list mapping
_APP_TASKS = {
    'calculator': _CALCULATOR_TASKS,
    'snapseed': _SNAPSEED_TASKS,
    'wikipedia': _WIKIPEDIA_TASKS,
    'all': _ALL_BMOCA_TASKS,
}


def _find_adb_directory() -> str:
  """Returns the directory where adb is located."""
  potential_paths = [
      os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
      os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
      '/shared/ken/.android/platform-tools/adb',  # Cluster-specific path
  ]
  for path in potential_paths:
    if os.path.isfile(path):
      return path
  raise EnvironmentError(
      'adb not found in the common Android SDK paths. Please install Android'
      " SDK and ensure adb is in one of the expected directories. If it's"
      ' already installed, point to the installed location.'
  )


_ADB_PATH = flags.DEFINE_string(
    'adb_path',
    _find_adb_directory(),
    'Path to adb. Set if not installed through SDK.',
)
_DEVICE_CONSOLE_PORT = flags.DEFINE_integer(
    'console_port',
    5554,
    'The console port of the running Android device.',
)
_APP = flags.DEFINE_enum(
    'app',
    'all',
    ['calculator', 'snapseed', 'wikipedia', 'all'],
    'The app to test tasks from (or "all" for all apps).',
)
_TASK = flags.DEFINE_string(
    'task',
    None,
    'The specific task to test. If not provided, will list available tasks for the selected app.',
)

_RUN_ALL = flags.DEFINE_boolean(
    'run_all',
    False,
    'Run all tasks for the specified app sequentially.',
)

_MAX_STEPS = flags.DEFINE_integer(
    'max_steps',
    None,
    'Maximum number of steps for the agent (overrides complexity-based calculation).',
)

_GRPC_PORT = flags.DEFINE_integer(
    'grpc_port',
    8554,
    'The gRPC port for communication with the emulator.',
)

_AGENT = flags.DEFINE_enum(
    'agent',
    'm3a',
    ['m3a', 't3a'],
    'The agent to use: m3a (multimodal with screenshots) or t3a (text-only).',
)

_REPORT = flags.DEFINE_string(
    'report',
    None,
    'Path to save JSON report of results. If not specified, no report is saved.',
)


def _save_report(results: list[dict], app_name: str, agent_type: str, report_path: str) -> None:
  """Save results to a JSON report file."""
  report = {
      'timestamp': datetime.now().isoformat(),
      'app': app_name,
      'agent': agent_type,
      'total_tasks': len(results),
      'successful': sum(1 for r in results if r['success']),
      'failed': sum(1 for r in results if not r['success']),
      'success_rate': sum(1 for r in results if r['success']) / len(results) * 100 if results else 0,
      'results': results,
  }
  
  # Ensure directory exists
  report_dir = os.path.dirname(report_path)
  if report_dir:
    os.makedirs(report_dir, exist_ok=True)
  
  with open(report_path, 'w') as f:
    json.dump(report, f, indent=2)
  
  print(f'\n📄 Report saved to: {report_path}')


def _get_available_tasks(app_name: str) -> list[str]:
  """Get available tasks for the specified app."""
  if app_name == 'all':
    return _ALL_BMOCA_TASKS
  return _APP_TASKS.get(app_name, [])


def _get_app_display_name(app_name: str) -> str:
  """Get display name for the app."""
  display_names = {
      'calculator': 'Calculator',
      'snapseed': 'Snapseed (Photo Editor)',
      'wikipedia': 'Wikipedia',
      'all': 'All BMOCA Apps',
  }
  return display_names.get(app_name, app_name)


def _run_single_task(task_name: str, app_name: str, env, aw_registry) -> dict:
  """Run a single task and return results.
  
  Returns:
      dict with keys: task_name, goal, score, completed, steps, max_steps, success
  """
  available_tasks = _get_available_tasks(app_name)
  
  if task_name not in aw_registry:
    raise ValueError(
        f'Task {task_name} not found in registry.'
        f' Available tasks: {", ".join(available_tasks)}'
    )
  
  # Get the task from registry
  print(f'Loading task: {task_name}...')
  task_type: Type[task_eval.TaskEval] = aw_registry[task_name]
  params = task_type.generate_random_params()
  task = task_type(params)
  task.initialize_task(env)
  print('✓ Task loaded\n')
  
  # Initialize agent with GPT-4o
  agent_type = _AGENT.value.upper()
  print(f'Initializing {agent_type} agent with GPT-4o...')
  if _AGENT.value == 'm3a':
    agent = m3a.M3A(env, infer.Gpt4Wrapper('gpt-4o'))
    agent.name = 'm3a_gpt4o'
  else:
    agent = t3a.T3A(env, infer.Gpt4Wrapper('gpt-4o'))
    agent.name = 't3a_gpt4o'
  agent.reset(go_home_on_reset=task.start_on_home_screen)
  print('✓ Agent initialized\n')
  
  # Run the task
  print('=' * 80)
  print(f'Goal: {task.goal}')
  print('=' * 80)
  print()
  
  # Calculate step budget based on complexity or use override
  if _MAX_STEPS.value is not None:
    max_steps = _MAX_STEPS.value
  else:
    max_steps = int(10 * task.complexity)
  
  print(f'Running task with max {max_steps} steps...')
  print(f'Complexity: {task.complexity}')
  print(f'Start on home screen: {task.start_on_home_screen}')
  print()
  
  episode_result = episode_runner.run_episode(
      goal=task.goal,
      agent=agent,
      max_n_steps=max_steps,
      start_on_home_screen=task.start_on_home_screen,
      termination_fn=None,
  )
  
  # Check if task was successful
  task_score = task.is_successful(env)
  task_successful = task_score >= 1.0
  agent_completed = episode_result.done
  
  # Calculate steps taken from step_data
  steps_taken = len(episode_result.step_data.get(constants.STEP_NUMBER, []))
  
  print()
  print('=' * 80)
  if task_successful and agent_completed:
    print('✅ Task Successful!')
    success = True
  elif task_score > 0.5 and agent_completed:
    print(f'⚠️  Task Partially Successful (score: {task_score:.2f})')
    success = False
  elif task_successful:
    print('⚠️  Task conditions met, but agent did not indicate completion')
    success = True
  elif agent_completed:
    print('❌ Agent completed, but task conditions not met')
    success = False
  else:
    print('❌ Task Failed')
    success = False
  
  print('=' * 80)
  print(f'Task: {task_name}')
  print(f'App: {_get_app_display_name(app_name)}')
  print(f'Goal: {task.goal}')
  print(f'Complexity: {task.complexity}')
  print(f'Steps taken: {steps_taken}/{max_steps}')
  print(f'Agent completed: {agent_completed}')
  print(f'Task score: {task_score:.2f}')
  print('=' * 80)
  
  return {
      'task_name': task_name,
      'goal': task.goal,
      'score': task_score,
      'completed': agent_completed,
      'steps': steps_taken,
      'max_steps': max_steps,
      'success': success,
  }


def _main() -> None:
  """Runs BMOCA tasks with M3A agent."""
  app_name = _APP.value
  task_name = _TASK.value
  run_all = _RUN_ALL.value
  
  # Get available tasks for the app
  available_tasks = _get_available_tasks(app_name)
  
  # If no task specified and not run_all, list available tasks
  if task_name is None and not run_all:
    print('=' * 80)
    print(f'Available tasks for: {_get_app_display_name(app_name)}')
    print('=' * 80)
    print(f'\nTotal tasks: {len(available_tasks)}\n')
    
    # Group tasks by app for better readability
    if app_name == 'all':
      print('CALCULATOR TASKS:')
      for i, task in enumerate(_CALCULATOR_TASKS, 1):
        print(f'  {i:2d}. {task}')
      print(f'\nSNAPSEED TASKS:')
      for i, task in enumerate(_SNAPSEED_TASKS, 1):
        print(f'  {i:2d}. {task}')
      print(f'\nWIKIPEDIA TASKS:')
      for i, task in enumerate(_WIKIPEDIA_TASKS, 1):
        print(f'  {i:2d}. {task}')
    else:
      for i, task in enumerate(available_tasks, 1):
        print(f'  {i:2d}. {task}')
    
    print(f'\nTo test a specific task, use: --task <task_name>')
    print(f'To run all tasks, use: --run_all')
    print(f'Example: python {sys.argv[0]} --app {app_name} --task {available_tasks[0]}')
    print(f'Example: python {sys.argv[0]} --app {app_name} --run_all')
    print('=' * 80)
    return
  
  # Determine which tasks to run
  if run_all:
    tasks_to_run = available_tasks
  else:
    # Validate task name
    if task_name not in available_tasks:
      print('=' * 80)
      print(f'ERROR: Task "{task_name}" not found for app "{app_name}"')
      print('=' * 80)
      print(f'\nAvailable tasks for {_get_app_display_name(app_name)}:')
      for task in available_tasks:
        print(f'  - {task}')
      print('=' * 80)
      sys.exit(1)
    tasks_to_run = [task_name]
  
  print('=' * 80)
  if run_all:
    print(f'Running ALL {len(tasks_to_run)} tasks for: {_get_app_display_name(app_name)}')
  else:
    print(f'Testing BMOCA Task: {task_name}')
  print(f'App: {_get_app_display_name(app_name)}')
  print(f'Agent: {_AGENT.value.upper()} ({"multimodal" if _AGENT.value == "m3a" else "text-only"})')
  print(f'Console Port: {_DEVICE_CONSOLE_PORT.value}')
  print(f'gRPC Port: {_GRPC_PORT.value}')
  print('=' * 80)

  # Check for OpenAI API key
  if 'OPENAI_API_KEY' not in os.environ:
    raise RuntimeError(
        'OPENAI_API_KEY environment variable is not set. Please set it before'
        ' running the evaluation.'
    )

  # Load environment (no setup needed - apps already installed)
  print('Connecting to emulator...')
  env = env_launcher.load_and_setup_env(
      console_port=_DEVICE_CONSOLE_PORT.value,
      emulator_setup=False,  # No setup needed
      adb_path=_ADB_PATH.value,
      grpc_port=_GRPC_PORT.value,
  )
  print('✓ Connected to emulator\n')

  # Get task registry
  task_registry = registry.TaskRegistry()
  aw_registry = task_registry.get_registry(
      registry.TaskRegistry.ANDROID_WORLD_FAMILY
  )

  # Run tasks
  results = []
  for i, current_task in enumerate(tasks_to_run, 1):
    if run_all:
      print()
      print('#' * 80)
      print(f'# Task {i}/{len(tasks_to_run)}: {current_task}')
      print('#' * 80)
      print()
    
    try:
      result = _run_single_task(current_task, app_name, env, aw_registry)
      results.append(result)
    except Exception as e:
      print(f'❌ Error running task {current_task}: {e}')
      results.append({
          'task_name': current_task,
          'goal': 'N/A',
          'score': 0.0,
          'completed': False,
          'steps': 0,
          'max_steps': 0,
          'success': False,
          'error': str(e),
      })

  # Print summary if running all tasks
  if run_all and len(results) > 1:
    print()
    print('#' * 80)
    print('# SUMMARY')
    print('#' * 80)
    print()
    
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f'App: {_get_app_display_name(app_name)}')
    print(f'Total tasks: {total}')
    print(f'Successful: {successful}')
    print(f'Failed: {total - successful}')
    print(f'Success rate: {successful/total*100:.1f}%')
    print()
    
    print('Results by task:')
    print('-' * 80)
    for r in results:
      status = '✅' if r['success'] else '❌'
      error_msg = f" (Error: {r.get('error', '')})" if 'error' in r else ''
      print(f"  {status} {r['task_name']}: score={r['score']:.2f}, steps={r['steps']}/{r['max_steps']}{error_msg}")
    print('-' * 80)

  # Save report if requested
  if _REPORT.value and results:
    _save_report(results, app_name, _AGENT.value, _REPORT.value)

  env.close()


def main(argv: Sequence[str]) -> None:
  del argv
  _main()


if __name__ == '__main__':
  app.run(main)

