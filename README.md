# Corporate Restricted Accounts File

Download and parse Excel files from Bank of Israel restricted accounts page and import to IDEA.

## Features

- Downloads zip files from Bank of Israel API
- Extracts Excel files from zip archives
- Parses each Excel file (customizable parser function)
- Saves parsed results to temporary files
- Combines all parsed files into a single final result

## Installation

Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the script to download and process a single zip file:

```bash
python download_and_parse.py
```

By default, it processes the `WHPRSM02` file (Corporate restricted accounts).

### Customize File Selection

Edit the `__main__` section in `download_and_parse.py` to change the file code:

```python
file_code = "WXPRSM02"  # Change to desired file code
```

Available file codes:
- `WHPRSM02` (0.13 MB) - Corporate restricted accounts
- `WXPRSM02` (1.29 MB) - Corporate restricted accounts
- `WTHMUR02` (0.017 MB) - Individual restricted accounts
- `WUHMUR02` (0.22 MB) - Individual restricted accounts

### Process Multiple Files

Uncomment the code in `__main__` to process multiple files:

```python
file_codes = ["WHPRSM02", "WXPRSM02"]
process_multiple_zip_files(
    file_codes=file_codes,
    output_dir="./output",
    final_output_path="./final_combined_result.csv"
)
```

## Customizing the Parser

The `parse_excel_file()` function in `download_and_parse.py` is a placeholder. Implement your specific parsing logic:

```python
def parse_excel_file(excel_path: str) -> dict:
    import pandas as pd
    
    # Customize based on your Excel file structure
    df = pd.read_excel(excel_path, 
                       sheet_name='Sheet1',  # Specify sheet name
                       skiprows=2,            # Skip header rows if needed
                       header=3)              # Specify header row
    
    # Add your data transformation logic here
    # ...
    
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
└── final_combined_result.csv  # Final combined result
```

## Notes

- The script saves intermediate files for debugging. Uncomment the cleanup code in `process_zip_file()` if you want to remove them automatically.
- Adjust the `save_parsed_result()` and `combine_results()` functions to match your desired output format (CSV, Excel, JSON, etc.).
