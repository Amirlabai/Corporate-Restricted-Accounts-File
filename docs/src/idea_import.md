# Module `src/idea_import.py`

Module for importing data to IDEA (Windows-only).

## Functions

### `save_to_idea(final_output_path: Path, today_date: str)`

Save the final output path to IDEA.

Args:
    final_output_path: Path to the CSV file to import
    today_date: Date string for naming
    ask_user_callback: Optional callback function that returns True/False for yes/no question.
                      If None, uses console input().

**Arguments:**
- `final_output_path` : `Path`
- `today_date` : `str`

### `refresh_file_explorer()`

Refresh IDEA file explorer if available.
