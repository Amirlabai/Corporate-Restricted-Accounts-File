# Module `src/idea_controller.py`

## Functions

### `search_disk_for_idea()`

No description provided.

### `is_idea_running()`

Checks if IntelliJ IDEA is currently running.
Returns True if IDEA is running, False otherwise.

### `start_idea(executable_path)`

Starts the IntelliJ IDEA application using its full path.
Checks if IDEA is already running before starting it.
The process is detached so it continues running after the parent script exits.

Note: In debug mode, the debugger may still terminate child processes when stopped.
This is a limitation of how debuggers handle process trees.

**Arguments:**
- `executable_path`

### `stop_idea()`

Stops all running IntelliJ IDEA processes.
