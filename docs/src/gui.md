# Module `src/gui.py`

Simple GUI application for downloading and parsing Bank of Israel restricted accounts data.

## Functions

### `resource_path(relative_path)`

Get absolute path to resource, works for dev and for Nuitka/PyInstaller

**Arguments:**
- `relative_path`

### `main()`

Main entry point for GUI application.

## Classes

### `RestrictedAccountsGUI`

Main GUI application class.

#### Methods

- `__init__(self, root)`
  - No description provided.
  - Arguments:
    - `self`
    - `root`

- `setup_ui(self)`
  - Create and arrange UI components.
  - Arguments:
    - `self`

- `show_help(self)`
  - Show help dialog.
  - Arguments:
    - `self`

- `exit_program(self)`
  - Exit the program.
  - Arguments:
    - `self`

- `load_config(self)`
  - Load configuration from file.
  - Arguments:
    - `self`

- `save_config(self, config: dict)`
  - Save configuration to file.
  - Arguments:
    - `self`
    - `config` : `dict`

- `_auto_save_folder(self)`
  - Automatically save folder setting when changed.
  - Arguments:
    - `self`

- `browse_folder(self)`
  - Open folder browser dialog.
  - Arguments:
    - `self`

- `save_folder_setting(self)`
  - Save the current folder setting.
  - Arguments:
    - `self`

- `log(self, message: str)`
  - Add message to log area.
  - Arguments:
    - `self`
    - `message` : `str`

- `update_status(self, status: str)`
  - Update status bar.
  - Arguments:
    - `self`
    - `status` : `str`

- `ask_switch_project(self, project_name: str)`
  - Show messagebox to ask user if they want to switch project.

Args:
    project_name: Name of the project
    
Returns:
    True if user clicked Yes, False otherwise
  - Arguments:
    - `self`
    - `project_name` : `str`

- `open_output_folder(self)`
  - Open the output folder in file explorer.
  - Arguments:
    - `self`

- `_move_downloaded_file(self, old_folder: Path, new_folder: Path)`
  - Move downloaded file when folder path changes.
  - Arguments:
    - `self`
    - `old_folder` : `Path`
    - `new_folder` : `Path`

- `_check_url_accessible(self, url: str, timeout: int=10)`
  - Check if a URL is accessible.

Args:
    url: The URL to check
    timeout: Request timeout in seconds (default: 10)
    
Returns:
    True if URL is accessible, False otherwise
  - Arguments:
    - `self`
    - `url` : `str`
    - `timeout` : `int` (default: `10`)

- `download_from_github(self)`
  - Download the latest CSV file from GitHub repository.
  - Arguments:
    - `self`

- `_download_from_github_thread(self)`
  - Internal method to download from GitHub.
  - Arguments:
    - `self`

- `import_to_idea(self)`
  - Import the downloaded file to IDEA.
  - Arguments:
    - `self`

- `on_search_change(self, event=None)`
  - Handle search input changes.
  - Arguments:
    - `self`
    - `event` (default: `None`)

- `_validate_digit_only(self, event)`
  - Validate that only digits are entered in date fields.
  - Arguments:
    - `self`
    - `event`

- `_handle_day_input(self, event=None)`
  - Handle day input with validation and auto-advance.
  - Arguments:
    - `self`
    - `event` (default: `None`)

- `_handle_month_input(self, event=None)`
  - Handle month input with validation and auto-advance.
  - Arguments:
    - `self`
    - `event` (default: `None`)

- `_handle_year_input(self, event=None)`
  - Handle year input with validation.
  - Arguments:
    - `self`
    - `event` (default: `None`)

- `_trigger_date_search(self)`
  - Trigger search when date fields change.
  - Arguments:
    - `self`

- `_update_date_range_from_file(self, df)`
  - Update min/max year range from the loaded file.
  - Arguments:
    - `self`
    - `df`

- `perform_search(self)`
  - Search for account number and/or date in the downloaded file.
  - Arguments:
    - `self`
