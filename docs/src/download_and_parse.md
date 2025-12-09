# Module `src/download_and_parse.py`

Script to download zip files from Bank of Israel restricted accounts page,
extract Excel files, parse them, and combine results.
Automatically import the combined data to IDEA with date-stamped naming.

## Functions

### `download_zip(url: str, output_path: Optional[Path]=None)`

Download a zip file from a URL with a progress spinner.

**Arguments:**
- `url` : `str`
- `output_path` : `Optional[Path]` (default: `None`)

### `extract_zip(zip_path: Path, extract_to: Optional[Path]=None)`

Extract a zip file to a directory.

**Arguments:**
- `zip_path` : `Path`
- `extract_to` : `Optional[Path]` (default: `None`)

### `find_excel_files(directory: Path)`

Find all Excel files in a directory (recursively).

**Arguments:**
- `directory` : `Path`

### `parse_excel_file(excel_path: Path)`

Parse an Excel file.

**Arguments:**
- `excel_path` : `Path`

### `rename_columns_by_content(df: pd.DataFrame)`

Rename columns based on their position to match required Hebrew column names.

**Arguments:**
- `df` : `pd.DataFrame`

### `save_parsed_result(parsed_data: Dict, original_filename: str, temp_dir: Path)`

Save parsed result to a temporary CSV file.

**Arguments:**
- `parsed_data` : `Dict`
- `original_filename` : `str`
- `temp_dir` : `Path`

### `combine_results(parsed_files: List[Path], output_path: Path)`

Combine all parsed files into a single final result file.

**Arguments:**
- `parsed_files` : `List[Path]`
- `output_path` : `Path`

### `process_zip_file(zip_url: str, output_dir: Optional[Path]=None, final_output_path: Optional[Path]=None)`

Orchestrate download, extraction, parsing, and combination.

**Arguments:**
- `zip_url` : `str`
- `output_dir` : `Optional[Path]` (default: `None`)
- `final_output_path` : `Optional[Path]` (default: `None`)

### `get_download_url(file_code: str)`

Get the download URL for a file from Bank of Israel API.

**Arguments:**
- `file_code` : `str`

### `save_to_idea(final_output_path: Path, today_date: str)`

Save the final output path to IDEA.

**Arguments:**
- `final_output_path` : `Path`
- `today_date` : `str`
