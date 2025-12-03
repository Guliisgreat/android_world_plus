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

"""Test Android Lab apps (Bluecoins, Maps.me, Pi Music) with M3A agent.

This script can test individual tasks or all tasks from Bluecoins, Maps.me,
or Pi Music apps using the M3A GPT-4 agent. Useful for testing and debugging
Android Lab tasks.

Usage:
    # List available tasks for an app
    python scripts/test_androidlab_apps.py --app bluecoins
    
    # Run a specific task
    python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsAddExpense
    
    # Run with custom ports
    python scripts/test_androidlab_apps.py --app bluecoins --task BluecoinsAddExpense --console_port 5706 --grpc_port 8556
"""

from collections.abc import Sequence
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


def _check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import android_env  # type: ignore
    except ImportError:
        missing.append('android_env')
    
    try:
        import absl  # type: ignore
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
        print('=' * 80)
        sys.exit(1)


# Check dependencies before proceeding
_check_dependencies()

from absl import app  # type: ignore
from absl import flags  # type: ignore
from absl import logging  # type: ignore

from android_world import constants
from android_world import episode_runner
from android_world import registry
from android_world.agents import infer
from android_world.agents import m3a
from android_world.env import env_launcher
from android_world.task_evals import task_eval

logging.set_verbosity(logging.WARNING)


# ============================================================================
# Task definitions for Android Lab apps
# ============================================================================

_BLUECOINS_TASKS = [
    # Query tasks
    'BluecoinsQuerySpendingOnDate',
    'BluecoinsQuerySpendingReason',
    'BluecoinsQueryTotalSpendingOnDate',
    'BluecoinsQueryTransactionCount',
    'BluecoinsQueryCategorySpending',
    # Create tasks
    'BluecoinsAddExpense',
    'BluecoinsAddIncomeWithLabel',
    'BluecoinsAddExpenseOnDate',
    'BluecoinsAddIncomeOnDateWithNote',
    'BluecoinsAddExpenseOnDateWithLabel',
    # Edit tasks
    'BluecoinsEditExpenseAmount',
    'BluecoinsEditIncomeDateAndAmount',
    'BluecoinsEditTransactionType',
    'BluecoinsEditTransactionTypeAmountNote',
    'BluecoinsEditExpenseDateAmountNote',
]

_MAPS_ME_TASKS = [
    # Query tasks
    'MapsMeCheckWalkingDistanceTime',
    'MapsMeCheckDrivingDistanceTime',
    'MapsMeCheckRidingTime',
    'MapsMeCheckPublicTransportRoute',
    'MapsMeCompareRidingVsPublicTransport',
    'MapsMeCheckNearestPlace',
    'MapsMeCheckNearestPlaceWalkTime',
    'MapsMeCheckNearestHotel',
    'MapsMeCheckNearestPlaceDriveTime',
    # Operation tasks
    'MapsMeAddWorkPlace',
    'MapsMeNavigateToLocation',
    'MapsMeNavigateToStanford',
    'MapsMeNavigateToUniversitySouth',
    'MapsMeNavigateToOpenAI',
    'MapsMeNavigateToBerkeley',
]

_PIMUSIC_TASKS = [
    # Query tasks
    'PiMusicQueryTotalSongs',
    'PiMusicQueryArtistSongCount',
    'PiMusicQuerySongAlbum',
    'PiMusicQueryLongestSongDuration',
    'PiMusicQuerySortedSongsByTitle',
    'PiMusicQueryArtistTotalDuration',
    # Operation tasks
    'PiMusicPlayFromPlaylist',
    'PiMusicSortByDurationDescending',
    'PiMusicCreatePlaylist',
    'PiMusicPauseAndSeek',
    'PiMusicPlaySongByTitleArtist',
    'PiMusicSortByDurationAscending',
]

# Combined list of all Android Lab tasks
_ALL_ANDROIDLAB_TASKS = _BLUECOINS_TASKS + _MAPS_ME_TASKS + _PIMUSIC_TASKS

# App name to task list mapping
_APP_TASKS = {
    'bluecoins': _BLUECOINS_TASKS,
    'maps.me': _MAPS_ME_TASKS,
    'mapsme': _MAPS_ME_TASKS,
    'pimusic': _PIMUSIC_TASKS,
    'pi_music': _PIMUSIC_TASKS,
    'all': _ALL_ANDROIDLAB_TASKS,
}


# ============================================================================
# Command line flags
# ============================================================================

def _find_adb_directory() -> str:
    """Returns the directory where adb is located."""
    potential_paths = [
        os.path.expanduser('~/Library/Android/sdk/platform-tools/adb'),
        os.path.expanduser('~/Android/Sdk/platform-tools/adb'),
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
    5706,
    'The console port of the running Android device.',
)

_GRPC_PORT = flags.DEFINE_integer(
    'grpc_port',
    8556,
    'The gRPC port for communication with the emulator.',
)

_APP = flags.DEFINE_enum(
    'app',
    'all',
    ['bluecoins', 'maps.me', 'mapsme', 'pimusic', 'pi_music', 'all'],
    'The app to test tasks from (or "all" for all apps).',
)

_TASK = flags.DEFINE_string(
    'task',
    None,
    'The specific task to test. If not provided, will list available tasks.',
)

_MAX_STEPS = flags.DEFINE_integer(
    'max_steps',
    None,
    'Maximum number of steps for the agent (overrides complexity-based calculation).',
)


# ============================================================================
# Main functions
# ============================================================================

def _get_available_tasks(app_name: str) -> list[str]:
    """Get available tasks for the specified app."""
    return _APP_TASKS.get(app_name, [])


def _get_app_display_name(app_name: str) -> str:
    """Get display name for the app."""
    display_names = {
        'bluecoins': 'Bluecoins (Personal Finance)',
        'maps.me': 'Maps.me (Navigation)',
        'mapsme': 'Maps.me (Navigation)',
        'pimusic': 'Pi Music Player',
        'pi_music': 'Pi Music Player',
        'all': 'All Android Lab Apps',
    }
    return display_names.get(app_name, app_name)


def _main() -> None:
    """Runs Android Lab tasks with M3A agent."""
    app_name = _APP.value
    task_name = _TASK.value
    
    # Get available tasks for the app
    available_tasks = _get_available_tasks(app_name)
    
    # If no task specified, list available tasks
    if task_name is None:
        print('=' * 80)
        print(f'Available tasks for: {_get_app_display_name(app_name)}')
        print('=' * 80)
        print(f'\nTotal tasks: {len(available_tasks)}\n')
        
        # Group tasks by type for better readability
        if app_name == 'all':
            print('BLUECOINS TASKS:')
            for i, task in enumerate(_BLUECOINS_TASKS, 1):
                print(f'  {i:2d}. {task}')
            print(f'\nMAPS.ME TASKS:')
            for i, task in enumerate(_MAPS_ME_TASKS, 1):
                print(f'  {i:2d}. {task}')
            print(f'\nPI MUSIC TASKS:')
            for i, task in enumerate(_PIMUSIC_TASKS, 1):
                print(f'  {i:2d}. {task}')
        else:
            for i, task in enumerate(available_tasks, 1):
                print(f'  {i:2d}. {task}')
        
        print(f'\nTo test a specific task, use: --task <task_name>')
        print(f'Example: python {sys.argv[0]} --app {app_name} --task {available_tasks[0]}')
        print('=' * 80)
        return
    
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
    
    print('=' * 80)
    print(f'Testing Android Lab Task: {task_name}')
    print(f'App: {_get_app_display_name(app_name)}')
    print(f'Console Port: {_DEVICE_CONSOLE_PORT.value}')
    print(f'gRPC Port: {_GRPC_PORT.value}')
    print('=' * 80)
    
    # Check for OpenAI API key
    if 'OPENAI_API_KEY' not in os.environ:
        raise RuntimeError(
            'OPENAI_API_KEY environment variable is not set. Please set it before'
            ' running the evaluation.'
        )
    
    # Load environment
    print('Connecting to emulator...')
    env = env_launcher.load_and_setup_env(
        console_port=_DEVICE_CONSOLE_PORT.value,
        emulator_setup=False,
        adb_path=_ADB_PATH.value,
        grpc_port=_GRPC_PORT.value,
    )
    print('✓ Connected to emulator\n')
    
    # Get the task from registry
    print(f'Loading task: {task_name}...')
    task_registry = registry.TaskRegistry()
    aw_registry = task_registry.get_registry(
        registry.TaskRegistry.ANDROID_WORLD_FAMILY
    )
    
    if task_name not in aw_registry:
        raise ValueError(
            f'Task {task_name} not found in registry.'
            f' Available tasks: {", ".join(available_tasks)}'
        )
    
    task_type: Type[task_eval.TaskEval] = aw_registry[task_name]
    params = task_type.generate_random_params()
    task = task_type(params)
    task.initialize_task(env)
    print('✓ Task loaded\n')
    
    # Initialize M3A agent with GPT-4
    print('Initializing M3A agent with GPT-4...')
    agent = m3a.M3A(env, infer.Gpt4Wrapper('gpt-4-turbo-2024-04-09'))
    agent.name = 'm3a_gpt4v'
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
    task_successful = task.is_successful(env)
    agent_completed = episode_result.done
    
    # Calculate steps taken from step_data
    steps_taken = len(episode_result.step_data.get(constants.STEP_NUMBER, []))
    
    print()
    print('=' * 80)
    if task_successful >= 1.0 and agent_completed:
        print('✅ Task Successful!')
    elif task_successful > 0.5 and agent_completed:
        print(f'⚠️  Task Partially Successful (score: {task_successful:.2f})')
    elif task_successful >= 1.0:
        print('⚠️  Task conditions met, but agent did not indicate completion')
    elif agent_completed:
        print('❌ Agent completed, but task conditions not met')
    else:
        print('❌ Task Failed')
    
    print('=' * 80)
    print(f'Task: {task_name}')
    print(f'App: {_get_app_display_name(app_name)}')
    print(f'Goal: {task.goal}')
    print(f'Complexity: {task.complexity}')
    print(f'Steps taken: {steps_taken}/{max_steps}')
    print(f'Agent completed: {agent_completed}')
    print(f'Task score: {task_successful:.2f}')
    print('=' * 80)
    
    env.close()


def main(argv: Sequence[str]) -> None:
    del argv
    _main()


if __name__ == '__main__':
    app.run(main)

