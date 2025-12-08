# Corporate Restricted Accounts File

Download and parse Excel files from Bank of Israel restricted accounts page and automatically import to IDEA.

## Features

- Downloads zip files from Bank of Israel API
- Extracts Excel files from zip archives
- Parses each Excel file with automatic column renaming
- Saves parsed results to temporary files
- Combines all parsed files into a single final result
- Automatically imports combined data to IDEA with date-stamped naming
- Performance timing for each processing stage

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the script to download and process a single zip file:

```bash
python src/download_and_parse.py
```

By default, it processes the `WXPRSM02` file (Corporate restricted accounts). The script will:
1. Download the zip file from Bank of Israel API
2. Extract and parse all Excel files
3. Combine all parsed data into a single CSV file
4. Automatically import the combined data to IDEA with a date-stamped name (e.g., `RestrictedAccounts_2025_12_08`)

### Customize File Selection

Edit the `__main__` section in `src/download_and_parse.py` to change the file code:

```python
file_code = "WXPRSM02"  # Change to desired file code
```

Available file codes:
- `WHPRSM02` (0.13 MB) - Corporate restricted accounts
- `WXPRSM02` (1.29 MB) - Corporate restricted accounts
- `WTHMUR02` (0.017 MB) - Individual restricted accounts
- `WUHMUR02` (0.22 MB) - Individual restricted accounts



## Data Structure

The parser automatically:
- Skips the first 4 rows of each Excel file (header rows)
- Renames columns to Hebrew names in the following order:
  - `תאריך_סיום_הגבלה` - End date of restriction
  - `מספר_סניף` - Branch number
  - `שם_סניף` - Branch name
  - `מספר_חשבון_מוגבל` - Restricted account number
  - `מספר_בנק` - Bank number (extracted from filename)

### Customizing the Parser

To customize the parsing logic, modify the `parse_excel_file()` function in `src/download_and_parse.py`:

```python
def parse_excel_file(excel_path: str) -> dict:
    # Current implementation skips 4 rows
    df = pd.read_excel(excel_path, engine='openpyxl', skiprows=4)
    
    # Modify skiprows, sheet_name, or other parameters as needed
    # df = pd.read_excel(excel_path, 
    #                    engine='openpyxl',
    #                    sheet_name='Sheet1',  # Specify sheet name
    #                    skiprows=4)           # Adjust skip rows
    
    # Column renaming is handled automatically by rename_columns_by_content()
    df = rename_columns_by_content(df)
    
    return {
        'file_path': excel_path,
        'file_name': os.path.basename(excel_path),
        'parsed_data': df,
        'row_count': len(df),
        'column_count': len(df.columns)
    }
```

## Output

The script creates the following structure:

```
output/
├── downloaded.zip          # Downloaded zip file
├── extracted/              # Extracted files
│   └── *.xlsx             # Excel files from zip
├── parsed/                 # Parsed results
│   └── *_parsed.csv       # Individual parsed files
└── appended/               # Final combined results
    └── RestrictedAccounts_YYYY_MM_DD.csv  # Date-stamped combined result
```

The final combined CSV file is automatically imported to IDEA with the same date-stamped name (e.g., `RestrictedAccounts_2025_12_08`).

## Performance

The script provides timing information for:
- Zip file processing (download, extraction, parsing, combination)
- IDEA import operation

Example output:
```
Time taken to process zip file: 45.23 seconds
Time taken to import to IDEA: 12.45 seconds
```

## Notes

- The script saves intermediate files for debugging. Uncomment the cleanup code in `process_zip_file()` if you want to remove them automatically.
- All CSV files use UTF-8 with BOM encoding (`utf-8-sig`) for proper Excel compatibility.
- The script requires IDEA to be installed and accessible via `IDEALib.py` in the `src/` directory.
- Output files are automatically named with today's date in `YYYY_MM_DD` format.
- The script automatically refreshes the IDEA file explorer after import.
