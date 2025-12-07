"""
Script to download zip files from Bank of Israel restricted accounts page,
extract Excel files, parse them, and combine results.
"""

import os
import re
import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
import requests
from urllib.parse import urlparse


def download_zip(url: str, output_path: Optional[str] = None, filename: Optional[str] = None) -> str:
    """
    Download a zip file from a URL.
    
    Args:
        url: URL of the zip file to download (can be direct URL or API endpoint)
        output_path: Optional path to save the zip file. If None, saves to temp directory.
        filename: Optional filename for the downloaded file. If None, extracts from URL or uses default.
    
    Returns:
        Path to the downloaded zip file
    """
    print(f"Downloading zip file from: {url}")
    
    # Set headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()
    
    if output_path is None:
        if filename:
            output_path = os.path.join(tempfile.gettempdir(), filename)
        else:
            # Try to get filename from Content-Disposition header
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"\'')
                output_path = os.path.join(tempfile.gettempdir(), filename)
            else:
                # Extract filename from URL or use default
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path) or "downloaded_file.zip"
                output_path = os.path.join(tempfile.gettempdir(), filename)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Download file
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Downloaded to: {output_path}")
    return output_path


def extract_zip(zip_path: str, extract_to: Optional[str] = None) -> str:
    """
    Extract a zip file to a directory.
    
    Args:
        zip_path: Path to the zip file
        extract_to: Directory to extract to. If None, extracts to temp directory.
    
    Returns:
        Path to the extraction directory
    """
    print(f"Extracting zip file: {zip_path}")
    
    if extract_to is None:
        extract_to = os.path.join(tempfile.gettempdir(), f"extracted_{os.path.basename(zip_path)}")
    
    os.makedirs(extract_to, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f"Extracted to: {extract_to}")
    return extract_to


def find_excel_files(directory: str) -> List[str]:
    """
    Find all Excel files in a directory (recursively).
    
    Args:
        directory: Directory to search in
    
    Returns:
        List of paths to Excel files
    """
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    excel_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in excel_extensions):
                excel_files.append(os.path.join(root, file))
    
    print(f"Found {len(excel_files)} Excel file(s)")
    return excel_files


def parse_excel_file(excel_path: str) -> dict:
    """
    Parse an Excel file. This is a placeholder function - implement the actual parsing logic here.
    
    Args:
        excel_path: Path to the Excel file
    
    Returns:
        Parsed data (as dictionary containing file info and parsed DataFrame)
    """
    print(f"Parsing Excel file: {excel_path}")
    
    try:
        import pandas as pd
        
        # Read Excel file - adjust parameters as needed for your specific file format
        # You may need to specify sheet_name, header row, etc.
        df = pd.read_excel(excel_path, engine='openpyxl')
        # TODO: Implement actual parsing logic here
        # For example, you might need to:
        # - Skip certain rows: pd.read_excel(excel_path, skiprows=2)
        # - Specify header row: pd.read_excel(excel_path, header=3)
        # - Read specific sheet: pd.read_excel(excel_path, sheet_name='Sheet1')
        # - Clean/transform data
        
        return {
            'file_path': excel_path,
            'file_name': os.path.basename(excel_path),
            'parsed_data': df,  # DataFrame with parsed data
            'row_count': len(df),
            'column_count': len(df.columns)
        }
    except Exception as e:
        print(f"Error parsing {excel_path}: {e}")
        return {
            'file_path': excel_path,
            'file_name': os.path.basename(excel_path),
            'parsed_data': None,
            'error': str(e)
        }


def rename_columns_by_content(df):
    """
    Rename columns based on their position/content to match required Hebrew column names.
    
    Args:
        df: DataFrame with columns to rename
    
    Returns:
        DataFrame with renamed columns
    """
    import pandas as pd
    
    # Define the required column names in order
    required_column_names = [
        'תאריך_סיום_הגבלה',      # col 0 - End date of restriction
        'מספר_סניף',              # col 1 - Branch number
        'שם_סניף',                # col 2 - Branch name
        'מספר_חשבון_מוגבל',      # col 3 - Restricted account number
        'מספר בנק'                 # col 4 - Bank number
    ]
    
    # Get current column names
    current_columns = df.columns.tolist()
    
    # Create a mapping dictionary
    column_mapping = {}
    
    # Map columns by position (assuming first 5 columns are the required ones)
    # Only rename if the column name doesn't already match the required name
    for i, required_name in enumerate(required_column_names):
        if i < len(current_columns):
            current_name = current_columns[i]
            # Only rename if it's different from the required name
            if current_name != required_name:
                column_mapping[current_name] = required_name
    
    # Rename columns if there are any mappings
    if column_mapping:
        df_renamed = df.rename(columns=column_mapping)
        print(f"  Renamed columns: {column_mapping}")
    else:
        df_renamed = df
    
    return df_renamed


def save_parsed_result(parsed_data: dict, original_filename: str, temp_dir: str) -> str:
    """
    Save parsed result to a temporary file with the original name.
    
    Args:
        parsed_data: Parsed data to save (should contain 'parsed_data' key with DataFrame)
        original_filename: Original filename (without extension)
        temp_dir: Temporary directory to save the file
    
    Returns:
        Path to the saved file
    """
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create output filename - save as CSV for easier combination later
    base_name = os.path.splitext(original_filename)[0]
    output_filename = f"{base_name}_parsed.csv"
    output_path = os.path.join(temp_dir, output_filename)
    
    try:
        import pandas as pd
        
        # Save as CSV if we have parsed data
        if parsed_data.get('parsed_data') is not None:
            df = parsed_data['parsed_data']
            if isinstance(df, pd.DataFrame):
                df = df.iloc[4:]
                # Reset index after slicing
                df = df.reset_index(drop=True)
                # Rename columns based on content/position
                df = rename_columns_by_content(df)
                # Add source file column for tracking - extract digits from filename
                digits = ''.join(re.findall(r'\d+', original_filename))
                df['מספר בנק'] = digits if digits else original_filename
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"Saved parsed result to: {output_path} ({len(df)} rows)")
            else:
                # Fallback if not a DataFrame
                raise ValueError("Parsed data is not a DataFrame")
        else:
            # If parsing failed, save error info
            digits = ''.join(re.findall(r'\d+', original_filename))
            error_info = {
                'source_file': digits if digits else original_filename,
                'error': parsed_data.get('error', 'Unknown error')
            }
            pd.DataFrame([error_info]).to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Saved error info to: {output_path}")
    
    except Exception as e:
        print(f"Error saving parsed result: {e}")
        # Fallback to text file
        output_path = os.path.join(temp_dir, f"{base_name}_parsed.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Parsed data from {original_filename}\n")
            f.write(f"Error: {str(e)}\n")
            f.write(str(parsed_data))
    
    return output_path


def combine_results(parsed_files: List[str], output_path: str):
    """
    Combine all parsed files into a single final result file.
    
    Args:
        parsed_files: List of paths to parsed files (CSV files)
        output_path: Path to save the final combined result
    """
    print(f"Combining {len(parsed_files)} parsed files...")
    
    try:
        import pandas as pd
        
        dfs = []
        for file_path in parsed_files:
            try:
                # Try to read as CSV first
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    dfs.append(df)
                    print(f"  Loaded {len(df)} rows from {os.path.basename(file_path)}")
                else:
                    # Fallback for other file types
                    print(f"  Skipping non-CSV file: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"  Error reading {os.path.basename(file_path)}: {e}")
                continue
        
        if dfs:
            # Combine all DataFrames
            combined_df = pd.concat(dfs, ignore_index=True, sort=False)
            
            # Define the required column order
            required_columns = [
                'תאריך_סיום_הגבלה',      # col 0
                'מספר_סניף',              # col 1
                'שם_סניף',                # col 2
                'מספר_חשבון_מוגבל',      # col 3
                'מספר בנק'                 # col 4
            ]
            
            # Get all existing columns
            existing_columns = combined_df.columns.tolist()
            
            # Build the final column order: required columns first, then others
            final_columns = []
            for col in required_columns:
                if col in existing_columns:
                    final_columns.append(col)
                else:
                    print(f"  Warning: Column '{col}' not found in data")
            
            # Add any remaining columns that aren't in the required list
            for col in existing_columns:
                if col not in final_columns:
                    final_columns.append(col)
            
            # Reorder columns
            combined_df = combined_df[final_columns]
            
            # Determine output format based on extension
            if output_path.endswith('.csv'):
                combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            elif output_path.endswith('.xlsx') or output_path.endswith('.xls'):
                combined_df.to_excel(output_path, index=False, engine='openpyxl')
            elif output_path.endswith('.json'):
                combined_df.to_json(output_path, orient='records', force_ascii=False, indent=2)
            else:
                # Default to CSV
                csv_path = os.path.splitext(output_path)[0] + '.csv'
                combined_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
                output_path = csv_path
            
            print(f"Combined results saved to: {output_path} ({len(combined_df)} total rows)")
            print(f"  Column order: {', '.join(final_columns[:5])}...")
        else:
            print("No valid data files to combine!")
    
    except Exception as e:
        print(f"Error combining files: {e}")
        # Fallback to text combination
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write("=== COMBINED RESULTS ===\n\n")
            for file_path in parsed_files:
                outfile.write(f"\n--- {os.path.basename(file_path)} ---\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}\n")
                outfile.write("\n")
        print(f"Combined results saved to: {output_path} (text format)")


def process_zip_file(zip_url: str, output_dir: Optional[str] = None, final_output_path: Optional[str] = None):
    """
    Main function to download zip, extract, parse Excel files, and combine results.
    
    Args:
        zip_url: URL of the zip file to download
        output_dir: Directory to save intermediate and final files. If None, uses temp directory.
        final_output_path: Path for the final combined result. If None, saves to output_dir.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="restricted_accounts_")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Step 1: Download zip file
        zip_path = download_zip(zip_url, os.path.join(output_dir, "downloaded.zip"))
        
        # Step 2: Extract zip file
        extract_dir = extract_zip(zip_path, os.path.join(output_dir, "extracted"))
        
        # Step 3: Find all Excel files
        excel_files = find_excel_files(extract_dir)
        
        if not excel_files:
            print("No Excel files found in the zip archive!")
            return
        
        # Step 4: Parse each Excel file and save to temp files
        temp_dir = os.path.join(output_dir, "parsed")
        os.makedirs(temp_dir, exist_ok=True)
        
        parsed_file_paths = []
        for excel_file in excel_files:
            try:
                # Parse the Excel file
                parsed_data = parse_excel_file(excel_file)
                
                # Save parsed result with original filename
                original_filename = os.path.basename(excel_file)
                parsed_file_path = save_parsed_result(parsed_data, original_filename, temp_dir)
                parsed_file_paths.append(parsed_file_path)
            except Exception as e:
                print(f"Error processing {excel_file}: {e}")
                continue
        
        # Step 5: Combine all parsed files
        if parsed_file_paths:
            if final_output_path is None:
                final_output_path = os.path.join(output_dir, "final_combined_result.csv")
            
            combine_results(parsed_file_paths, final_output_path)
            print(f"\nProcessing complete! Final result saved to: {final_output_path}")
        else:
            print("No files were successfully parsed!")
    
    except Exception as e:
        print(f"Error during processing: {e}")
        raise
    finally:
        # Optionally clean up temp files (uncomment if desired)
        # shutil.rmtree(output_dir, ignore_errors=True)
        pass


def get_download_url(file_code: str) -> str:
    """
    Get the download URL for a file from Bank of Israel API.
    
    Args:
        file_code: File code (e.g., 'WHPRSM02', 'WXPRSM02', 'WTHMUR02', 'WUHMUR02')
    
    Returns:
        API endpoint URL for downloading the file
    """
    base_url = "https://mugbalim.boi.gov.il/api/umbraco/api/DownloadFiles"
    return f"{base_url}/{file_code}"


def process_multiple_zip_files(file_codes: List[str], output_dir: Optional[str] = None, 
                                final_output_path: Optional[str] = None):
    """
    Process multiple zip files and combine all results into a single file.
    
    Args:
        file_codes: List of file codes to download and process
        output_dir: Directory to save intermediate and final files. If None, uses temp directory.
        final_output_path: Path for the final combined result. If None, saves to output_dir.
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="restricted_accounts_")
    
    os.makedirs(output_dir, exist_ok=True)
    
    all_parsed_files = []
    
    for file_code in file_codes:
        print(f"\n{'='*60}")
        print(f"Processing file: {file_code}")
        print(f"{'='*60}")
        
        try:
            zip_url = get_download_url(file_code)
            
            # Process each zip file
            file_output_dir = os.path.join(output_dir, file_code)
            process_zip_file(
                zip_url=zip_url,
                output_dir=file_output_dir,
                final_output_path=None  # We'll combine all at the end
            )
            
            # Collect all parsed files from this zip
            parsed_dir = os.path.join(file_output_dir, "parsed")
            if os.path.exists(parsed_dir):
                parsed_files = [os.path.join(parsed_dir, f) 
                              for f in os.listdir(parsed_dir) 
                              if f.endswith(('.csv', '.txt', '.json'))]
                all_parsed_files.extend(parsed_files)
        
        except Exception as e:
            print(f"Error processing {file_code}: {e}")
            continue
    
    # Combine all parsed files from all zip files
    if all_parsed_files:
        if final_output_path is None:
            final_output_path = os.path.join(output_dir, "final_combined_result.csv")
        
        combine_results(all_parsed_files, final_output_path)
        print(f"\n{'='*60}")
        print(f"All processing complete! Final result saved to: {final_output_path}")
        print(f"{'='*60}")
    else:
        print("No files were successfully parsed!")


if __name__ == "__main__":
    # Example usage
    # Available file codes from the website:
    # - WHPRSM02 (0.13 MB) - Corporate restricted accounts
    # - WXPRSM02 (1.29 MB) - Corporate restricted accounts
    # - WTHMUR02 (0.017 MB) - Individual restricted accounts
    # - WUHMUR02 (0.22 MB) - Individual restricted accounts
    
    # Option 1: Process a single zip file
    file_code = "WXPRSM02"  # Change this to the file you want to download
    zip_url = get_download_url(file_code)
    
    process_zip_file(
        zip_url=zip_url,
        output_dir="./output",  # Save to ./output directory
        final_output_path="./final_result.csv"  # Final combined result (CSV format)
    )
    
    # Option 2: Process multiple zip files and combine all results
    # Uncomment the following to process multiple files:
    # file_codes = ["WHPRSM02", "WXPRSM02"]  # Corporate restricted accounts
    # process_multiple_zip_files(
    #     file_codes=file_codes,
    #     output_dir="./output",
    #     final_output_path="./final_combined_result.csv"
    # )

