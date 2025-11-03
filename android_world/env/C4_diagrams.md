# C4 Model Diagrams for Android World Environment

## Context Diagram (Level 1)
Shows the Android World Environment in the context of the broader system.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Android World Environment                         │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         env/ Module                                  │  │
│  │                                                                       │  │
│  │  Provides Android environment interface for:                         │  │
│  │  • Real-time device interaction                                      │  │
│  │  • UI observation and accessibility                                  │  │
│  │  • Action execution via ADB                                          │  │
│  │  • Environment setup and management                                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ uses
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         External Dependencies                               │
│                                                                              │
│  ┌──────────────────────┐    ┌──────────────────────┐                     │
│  │   Android Device/    │    │   android_env        │                     │
│  │   Emulator           │    │   Library            │                     │
│  │                      │    │                      │                     │
│  │  • ADB Interface     │    │  • Base environment  │                     │
│  │  • gRPC              │    │  • Wrappers          │                     │
│  │  • Accessibility     │    │  • Proto definitions │                     │
│  │    Service           │    │                      │                     │
│  └──────────────────────┘    └──────────────────────┘                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Container Diagram (Level 2)
Shows the major modules/containers within the env package and their relationships.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           env/ Package Structure                            │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    Core Environment Layer                          │    │
│  │                                                                    │    │
│  │  ┌──────────────────┐         ┌──────────────────────────────┐   │    │
│  │  │  interface.py    │◄────────│  env_launcher.py             │   │    │
│  │  │                  │         │                               │   │    │
│  │  │  • AsyncEnv      │         │  • load_and_setup_env()      │   │    │
│  │  │  • AsyncAndroidEnv│        │  • setup_env()               │   │    │
│  │  │  • State         │         │  • Environment factory       │   │    │
│  │  └──────────────────┘         └──────────────────────────────┘   │    │
│  │           │                              │                        │    │
│  │           │ uses                         │ uses                   │    │
│  │           ▼                              ▼                        │    │
│  │  ┌────────────────────────────────────────────────────────┐     │    │
│  │  │         android_world_controller.py                    │     │    │
│  │  │                                                         │     │    │
│  │  │  • AndroidWorldController                              │     │    │
│  │  │  • A11yMethod                                          │     │    │
│  │  │  • get_controller()                                    │     │    │
│  │  │  • Wraps AndroidEnv with A11y support                  │     │    │
│  │  └────────────────────────────────────────────────────────┘     │    │
│  └──────────────────────────────────────────────────────────────────┘    │
│                                                                            │
│  ┌────────────────────────────────────────────────────────────────────┐   │
│  │                    Device Interaction Layer                        │   │
│  │                                                                    │   │
│  │  ┌──────────────────┐         ┌──────────────────────────────┐   │   │
│  │  │  adb_utils.py    │◄────────│  actuation.py                │   │   │
│  │  │                  │         │                               │   │   │
│  │  │  • ADB commands  │         │  • execute_adb_action()      │   │   │
│  │  │  • Screen ops    │         │  • find_and_click_element()  │   │   │
│  │  │  • App mgmt      │         │  • Action execution logic    │   │   │
│  │  │  • Device info   │         │                               │   │   │
│  │  │  100+ functions  │         └──────────────────────────────┘   │   │
│  │  └──────────────────┘                 │                         │   │
│  │           │                            │ uses                   │   │
│  │           │                            ▼                         │   │
│  │           │                 ┌──────────────────────────────┐   │   │
│  │           │                 │  json_action.py              │   │   │
│  │           │                 │                              │   │   │
│  │           │                 │  • JSONAction                │   │   │
│  │           │                 │  • Action types              │   │   │
│  │           │                 │  • Serialization             │   │   │
│  │           │                 └──────────────────────────────┘   │   │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    UI Representation Layer                          │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────┐      │  │
│  │  │         representation_utils.py                        │      │  │
│  │  │                                                         │      │  │
│  │  │  • UIElement                                           │      │  │
│  │  │  • BoundingBox                                         │      │  │
│  │  │  • forest_to_ui_elements()                            │      │  │
│  │  │  • xml_dump_to_ui_elements()                          │      │  │
│  │  │  • A11y tree processing                                │      │  │
│  │  └────────────────────────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Setup and Tools Layer                           │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────┐      │  │
│  │  │  setup_device/                                         │      │  │
│  │  │  ┌──────────────────┐  ┌─────────────────────────┐   │      │  │
│  │  │  │   setup.py       │  │  apps.py                │   │      │  │
│  │  │  │                  │  │                         │   │      │  │
│  │  │  │  • setup_apps()  │  │  • AppSetup classes     │   │      │  │
│  │  │  │  • App install   │  │  • 25+ app setups       │   │      │  │
│  │  │  └──────────────────┘  └─────────────────────────┘   │      │  │
│  │  └────────────────────────────────────────────────────────┘      │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────┐      │  │
│  │  │  tools.py                                               │      │  │
│  │  │                                                         │      │  │
│  │  │  • AndroidToolController                               │      │  │
│  │  │  • High-level APIs                                     │      │  │
│  │  │  • open_web_page(), send_sms(), etc.                   │      │  │
│  │  └────────────────────────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    Constants                                       │  │
│  │                                                                    │  │
│  │  ┌────────────────────────────────────────────────────────┐      │  │
│  │  │  device_constants.py                                   │      │  │
│  │  │                                                         │      │  │
│  │  │  • Screen dimensions                                   │      │  │
│  │  │  • Data paths                                          │      │  │
│  │  │  • Timezone/DateTime                                   │      │  │
│  │  └────────────────────────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## Component Diagram (Level 3)
Detailed components within each container.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Component Relationships                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT LIFECYCLE                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

env_launcher.py
├── load_and_setup_env() ────────┐
│   • Creates AsyncAndroidEnv     │
│   • Calls setup_env()           │
│   • Returns ready environment   │
└─────────────────────────────────┤
                                  │
                                  ▼
setup_device/setup.py
├── setup_apps() ─────────────────┤
│   • maybe_install_app()         │
│   • setup_app()                 │
└─────────────────────────────────┘
                                  │
                                  ▼
setup_device/apps.py
├── AppSetup (abstract) ──────────┤
│   ├── CameraApp                 │
│   ├── ChromeApp                 │
│   ├── JoplinApp                 │
│   └── ... (25 total)            │
└─────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT INTERFACE                                                      │
└─────────────────────────────────────────────────────────────────────────────┘

interface.py
├── AsyncEnv (abstract base)
│   └── AsyncAndroidEnv (implementation)
│       ├── reset() → State
│       ├── get_state() → State
│       ├── execute_action()
│       ├── display_message()
│       └── ask_question()
│
└── State (dataclass)
    ├── pixels: np.ndarray
    ├── forest: AccessibilityForest
    ├── ui_elements: List[UIElement]
    └── auxiliaries: Dict

┌─────────────────────────────────────────────────────────────────────────────┐
│  CONTROLLER LAYER                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

android_world_controller.py
├── AndroidWorldController
│   ├── Wraps AndroidEnv
│   ├── Adds A11y tree support
│   ├── get_a11y_forest()
│   ├── get_ui_elements()
│   ├── _process_timestep()
│   └── device_screen_size, logical_screen_size
│
├── A11yMethod (enum)
│   ├── A11Y_FORWARDER_APP
│   ├── UIAUTOMATOR
│   └── NONE
│
└── get_controller() factory
    ├── Creates config
    ├── Loads AndroidEnv
    └── Wraps with AndroidWorldController

┌─────────────────────────────────────────────────────────────────────────────┐
│  ACTION EXECUTION                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

json_action.py
├── JSONAction (dataclass)
│   ├── action_type
│   ├── index, x, y
│   ├── text, direction
│   ├── app_name, keycode
│   └── Methods: as_dict(), json_str()
│
└── Action Types
    ├── CLICK, DOUBLE_TAP, LONG_PRESS
    ├── INPUT_TEXT, KEYBOARD_ENTER
    ├── NAVIGATE_HOME, NAVIGATE_BACK
    ├── OPEN_APP, SCROLL, SWIPE
    └── STATUS, ANSWER, WAIT

        │
        │ uses
        ▼

actuation.py
├── execute_adb_action()
│   ├── Click/Double-tap/Long-press
│   ├── Input text
│   ├── Navigate
│   ├── Scroll/Swipe
│   ├── Open app
│   └── Orientation change
│
├── find_and_click_element()
│   └── _wait_and_find_click_element()
│
└── _find_target_element()
    └── _levenshtein_distance()

        │
        │ uses
        ▼

adb_utils.py
├── Screen Operations
│   ├── tap_screen(x, y)
│   ├── double_tap(x, y)
│   ├── long_press(x, y)
│   ├── generate_swipe_command()
│   └── generate_drag_and_drop_command()
│
├── Navigation
│   ├── press_home_button()
│   ├── press_back_button()
│   ├── press_enter_button()
│   └── press_keyboard_generic()
│
├── Text Input
│   ├── type_text()
│   └── _adb_text_format()
│
├── App Management
│   ├── launch_app()
│   ├── close_app()
│   ├── get_all_apps()
│   └── get_adb_activity()
│
├── Device Info
│   ├── get_screen_size()
│   ├── get_logical_screen_size()
│   ├── get_orientation()
│   ├── get_physical_frame_boundary()
│   └── get_current_activity()
│
├── System Operations
│   ├── toggle_wifi(), toggle_bluetooth()
│   ├── set_brightness()
│   ├── change_orientation()
│   └── get_api_level()
│
├── Intent Broadcasting
│   ├── start_activity()
│   ├── send_android_intent()
│   └── issue_generic_request()
│
└── Utilities
    ├── retry() decorator
    ├── set_root_if_needed()
    └── uiautomator_dump()

┌─────────────────────────────────────────────────────────────────────────────┐
│  UI REPRESENTATION                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

representation_utils.py
├── UIElement (dataclass)
│   ├── text, content_description
│   ├── class_name, resource_id
│   ├── bbox, bbox_pixels
│   ├── is_clickable, is_editable, etc.
│   └── State flags (15+ properties)
│
├── BoundingBox (dataclass)
│   ├── x_min, x_max, y_min, y_max
│   └── Properties: center, width, height, area
│
├── forest_to_ui_elements()
│   └── accessibility_node_to_ui_element()
│       └── Converts A11y tree → UIElements
│
└── xml_dump_to_ui_elements()
    └── _parse_ui_hierarchy()
        └── Converts UI Automator dump → UIElements

┌─────────────────────────────────────────────────────────────────────────────┐
│  HIGH-LEVEL TOOLS                                                           │
└─────────────────────────────────────────────────────────────────────────────┘

tools.py
└── AndroidToolController
    ├── click_element()
    ├── open_web_page()
    ├── send_sms()
    ├── display_tool_usage()
    └── handle_json_request()
```

## Code Level (Level 4) - Key Files and Functions

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CODE IMPLEMENTATION DETAILS                            │
└─────────────────────────────────────────────────────────────────────────────┘

interface.py (362 lines)
├── class AsyncEnv (ABC)
│   ├── controller (property)
│   ├── reset(go_home: bool) → State
│   ├── get_state(wait_to_stabilize: bool) → State
│   ├── execute_action(action: JSONAction)
│   ├── display_message(message, header)
│   ├── ask_question(question, timeout)
│   ├── foreground_activity_name (property)
│   ├── device_screen_size (property)
│   └── close()
│
└── class AsyncAndroidEnv (AsyncEnv)
    ├── __init__(controller)
    ├── _get_state() → State
    ├── _get_stable_state() → State
    │   └── UI stability checking logic
    └── Uses adb_utils and actuation for implementation

android_world_controller.py (330 lines)
├── class AndroidWorldController (BaseWrapper)
│   ├── __init__(env, a11y_method, install_a11y_forwarding_app)
│   ├── Wraps AndroidEnv with A11yGrpcWrapper
│   ├── get_a11y_forest() → AccessibilityForest
│   ├── get_ui_elements() → List[UIElement]
│   ├── _process_timestep() → TimeStep (adds UI info)
│   ├── pull_file(), push_file()
│   └── refresh_env()
│
└── def get_controller(console_port, adb_path, grpc_port) → Controller
    └── Factory function creating controller

actuation.py (315 lines)
├── def execute_adb_action(action, screen_elements, screen_size, env)
│   ├── Handles 15+ action types
│   ├── Maps JSONAction → ADB commands
│   └── Calls adb_utils functions
│
├── def find_and_click_element(element_text, env, case_sensitive)
│   └── Waits for element and clicks
│
└── def _find_target_element(ui_elements, target_text, case_sensitive)
    └── Uses Levenshtein distance for matching

adb_utils.py (1781 lines) - Largest file
├── 80+ ADB command functions
├── Organized by category:
│   ├── Screen ops: tap_screen, double_tap, long_press, swipe
│   ├── Navigation: press_home, press_back, press_enter
│   ├── Text: type_text, press_keyboard_generic
│   ├── Apps: launch_app, close_app, get_all_apps
│   ├── Device: get_screen_size, get_orientation
│   ├── System: toggle_wifi, set_brightness, change_orientation
│   ├── Intents: start_activity, send_android_intent
│   ├── Utils: retry, issue_generic_request
│   └── Specialized: clipboard, contacts, SMS, calls

json_action.py (201 lines)
├── class JSONAction (dataclass)
│   ├── Field definitions
│   ├── __post_init__() - validation
│   ├── as_dict() - serialization
│   ├── json_str() - JSON output
│   └── __eq__() - comparison
│
└── Action type constants
    └── _PATTERN_TO_ACTIVITY mapping (170 lines)

representation_utils.py (220 lines)
├── class UIElement (dataclass) - 20+ fields
├── class BoundingBox (dataclass)
│   └── Properties: center, width, height, area
│
├── def accessibility_node_to_ui_element(node, screen_size) → UIElement
│   └── Converts protobuf node → UIElement
│
├── def forest_to_ui_elements(forest, exclude_invisible, screen_size)
│   └── Extracts all UI elements from accessibility tree
│
└── def xml_dump_to_ui_elements(xml_string) → List[UIElement]
    └── Converts UI Automator XML → UIElements

tools.py (191 lines)
└── class AndroidToolController
    ├── __init__(env)
    ├── click_element(element_text)
    ├── open_web_page(url)
    ├── send_sms(phone_number, message)
    ├── _gather_tool_details() → Dict
    ├── display_tool_usage() → str
    └── handle_json_request(json_request)

env_launcher.py (128 lines)
├── def _get_env(console_port, adb_path, grpc_port) → AsyncEnv
│   └── Creates AsyncAndroidEnv with controller
│
├── def setup_env(env, emulator_setup, freeze_datetime)
│   └── Calls setup.setup_apps() and datetime_utils.setup_datetime()
│
└── def load_and_setup_env(...) → AsyncEnv
    └── Main entry point

setup_device/setup.py (189 lines)
├── def setup_apps(env, app_list) → None
│   ├── maybe_install_app() for each app
│   └── setup_app() for each app
│
├── def maybe_install_app(app, env) → None
│   └── Downloads and installs APK
│
└── def setup_app(app, env) → None
    ├── Calls app.setup(env)
    └── Saves snapshot

setup_device/apps.py (769 lines)
├── class AppSetup (ABC)
│   ├── app_name (class var)
│   ├── apk_names (class var)
│   ├── package_name() → str
│   └── setup(env) → None
│
└── 25+ AppSetup subclasses
    ├── CameraApp
    ├── ChromeApp
    ├── JoplinApp
    ├── MarkorApp
    └── ... (each implements setup())

device_constants.py (45 lines)
├── Screen dimensions
├── Data paths for various apps
└── Timezone/DateTime defaults
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW                                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Agent/User]
    │
    │ Action Request
    ▼
┌──────────────────────┐
│  JSONAction          │
│  (json_action.py)    │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ execute_action()     │─────► [AsyncAndroidEnv]
│ (actuation.py)       │              │
└──────────────────────┘              │
    │                                  │
    ▼                                  ▼
┌──────────────────────┐      ┌─────────────────────┐
│ ADB Commands         │      │ get_state()         │
│ (adb_utils.py)       │      │                     │
└──────────────────────┘      └─────────────────────┘
    │                                  │
    ▼                                  ▼
[Android Device]              ┌─────────────────────┐
    │                         │ Controller          │
    │ State change            │ (android_world_     │
    ▼                         │  _controller.py)    │
[State Response]              └─────────────────────┘
    │                                  │
    ▼                                  ▼
┌──────────────────────┐      ┌─────────────────────┐
│ A11y Forest          │◄─────│ get_a11y_forest()   │
│ (protobuf)           │      └─────────────────────┘
└──────────────────────┘              │
    │                                  ▼
    ▼                         ┌─────────────────────┐
┌──────────────────────┐      │ forest_to_ui_       │
│ forest_to_ui_elements│◄─────│ elements()          │
│ (representation_     │      │ (representation_    │
│  utils.py)           │      │  utils.py)          │
└──────────────────────┘      └─────────────────────┘
    │
    ▼
┌──────────────────────┐
│ List[UIElement]      │
│ + screenshot pixels  │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ State                │─────► [Agent/User]
│ (interface.py)       │
└──────────────────────┘
```

## Summary Statistics

- **Total Files**: 16 Python modules
- **Total Lines**: ~6,500 lines of code
- **Largest File**: adb_utils.py (1,781 lines)
- **Core Components**: 7 main modules
- **Design Patterns**:
  - Wrapper Pattern (AndroidWorldController wrapping AndroidEnv)
  - Factory Pattern (get_controller, load_and_setup_env)
  - Abstract Base Classes (AsyncEnv, AppSetup)
  - Strategy Pattern (A11yMethod enum)

