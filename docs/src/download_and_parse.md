# Module `src/download_and_parse.py`

Script to download zip files from Bank of Israel restricted accounts page,
extract Excel files, parse them, and combine results.

## Functions

### `download_zip(url: str, output_path: Optional[str]=None, filename: Optional[str]=None)`

Download a zip file from a URL.

Args:
    url: URL of the zip file to download (can be direct URL or API endpoint)
    output_path: Optional path to save the zip file. If None, saves to temp directory.
    filename: Optional filename for the downloaded file. If None, extracts from URL or uses default.

Returns:
    Path to the downloaded zip file

**Arguments:**
- `url` : `str`
- `output_path` : `Optional[str]` (default: `None`)
- `filename` : `Optional[str]` (default: `None`)

### `extract_zip(zip_path: str, extract_to: Optional[str]=None)`

Extract a zip file to a directory.

Args:
    zip_path: Path to the zip file
    extract_to: Directory to extract to. If None, extracts to temp directory.

Returns:
    Path to the extraction directory

**Arguments:**
- `zip_path` : `str`
- `extract_to` : `Optional[str]` (default: `None`)

### `find_excel_files(directory: str)`

Find all Excel files in a directory (recursively).

Args:
    directory: Directory to search in

Returns:
    List of paths to Excel files

**Arguments:**
- `directory` : `str`

### `parse_excel_file(excel_path: str)`

Parse an Excel file. This is a placeholder function - implement the actual parsing logic here.

Args:
    excel_path: Path to the Excel file

Returns:
    Parsed data (as dictionary containing file info and parsed DataFrame)

**Arguments:**
- `excel_path` : `str`

### `rename_columns_by_content(df)`

Rename columns based on their position/content to match required Hebrew column names.

Args:
    df: DataFrame with columns to rename

Returns:
    DataFrame with renamed columns

**Arguments:**
- `df`

### `save_parsed_result(parsed_data: dict, original_filename: str, temp_dir: str)`

Save parsed result to a temporary file with the original name.

Args:
    parsed_data: Parsed data to save (should contain 'parsed_data' key with DataFrame)
    original_filename: Original filename (without extension)
    temp_dir: Temporary directory to save the file

Returns:
    Path to the saved file

**Arguments:**
- `parsed_data` : `dict`
- `original_filename` : `str`
- `temp_dir` : `str`

### `combine_results(parsed_files: List[str], output_path: str)`

Combine all parsed files into a single final result file.

Args:
    parsed_files: List of paths to parsed files (CSV files)
    output_path: Path to save the final combined result

**Arguments:**
- `parsed_files` : `List[str]`
- `output_path` : `str`

### `process_zip_file(zip_url: str, output_dir: Optional[str]=None, final_output_path: Optional[str]=None)`

Main function to download zip, extract, parse Excel files, and combine results.

Args:
    zip_url: URL of the zip file to download
    output_dir: Directory to save intermediate and final files. If None, uses temp directory.
    final_output_path: Path for the final combined result. If None, saves to output_dir.

**Arguments:**
- `zip_url` : `str`
- `output_dir` : `Optional[str]` (default: `None`)
- `final_output_path` : `Optional[str]` (default: `None`)

### `get_download_url(file_code: str)`

Get the download URL for a file from Bank of Israel API.

Args:
    file_code: File code (e.g., 'WHPRSM02', 'WXPRSM02', 'WTHMUR02', 'WUHMUR02')

Returns:
    API endpoint URL for downloading the file

**Arguments:**
- `file_code` : `str`
