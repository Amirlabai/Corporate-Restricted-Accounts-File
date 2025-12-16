"""
Script to download zip files from Bank of Israel restricted accounts page,
extract Excel files, parse them, and combine results.
Automatically import the combined data to IDEA with date-stamped naming.
"""

__author__ = "Amir Labai"
__copyright__ = "Copyright 2025, Amir Labai"
__credits__ = ["Amir Labai"]
__license__ = "MIT"
__maintainer__ = "Amir Labai"
__email__ = "amirlabay@gmail.com"
__status__ = "Production"

import os
import re
import zipfile
import tempfile
import shutil
import time
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from urllib.parse import urlparse

import requests
import pandas as pd
import IDEALib as idea

# --- Configuration ---
REQUIRED_COLUMNS = [
    'תאריך_סיום_הגבלה',      # col 0
    'מספר_סניף',              # col 1
    'שם_סניף',                # col 2
    'מספר_חשבון_מוגבל',      # col 3
    'מספר_בנק'                # col 4 - calculated
]

def download_zip(url: str, output_path: Optional[Path] = None) -> Path:
    """Download a zip file from a URL with a progress spinner."""
    print(f"Downloading zip file from: {url}\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()
    
    if output_path is None:
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"\'')
        else:
            parsed_url = urlparse(url)
            filename = Path(parsed_url.path).name or "downloaded_file.zip"
        output_path = Path(tempfile.gettempdir()) / filename
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    sys.stdout.write('\rDownload Complete!   \n')
    sys.stdout.flush()
    
    print(f"Downloaded to: {output_path}")
    return output_path


def extract_zip(zip_path: Path, extract_to: Optional[Path] = None) -> Path:
    """Extract a zip file to a directory."""
    print(f"Extracting zip file: {zip_path}")
    
    if extract_to is None:
        extract_to = Path(tempfile.gettempdir()) / f"extracted_{zip_path.stem}"
    
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    
    print(f"Extracted to: {extract_to}")
    return extract_to


def find_excel_files(directory: Path) -> List[Path]:
    """Find all Excel files in a directory (recursively)."""
    excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    excel_files = [
        p for p in Path(directory).rglob("*") 
        if p.suffix.lower() in excel_extensions and not p.name.startswith('~$')
    ]
    
    print(f"Found {len(excel_files)} Excel file(s)")
    return excel_files


def parse_excel_file(excel_path: Path) -> Dict[str, Any]:
    """Parse an Excel file."""
    print(f"Parsing Excel file: {excel_path}")
    
    try:     
        # Using openpyxl
        df = pd.read_excel(excel_path, engine='openpyxl', skiprows=4)
        
        df.reset_index(drop=True, inplace=True)
        
        # Extract Bank Number from digits in filename
        digits = ''.join(re.findall(r'\d+', excel_path.name))
        df['מספר_בנק'] = digits if digits else excel_path.stem
        
        df = rename_columns_by_content(df)
        
        return {
            'file_path': str(excel_path),
            'file_name': excel_path.name,
            'parsed_data': df,
            'row_count': len(df),
            'column_count': len(df.columns)
        }
    except Exception as e:
        print(f"Error parsing {excel_path}: {e}")
        return {
            'file_path': str(excel_path),
            'file_name': excel_path.name,
            'parsed_data': None,
            'error': str(e)
        }


def rename_columns_by_content(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns based on their position to match required Hebrew column names."""
    current_columns = df.columns.tolist()
    column_mapping = {}
    
    for i, required_name in enumerate(REQUIRED_COLUMNS):
        if i < len(current_columns):
            current_name = current_columns[i]
            if current_name != required_name:
                column_mapping[current_name] = required_name
    
    if column_mapping:
        df_renamed = df.rename(columns=column_mapping)
        return df_renamed
    
    return df


def save_parsed_result(parsed_data: Dict, original_filename: str, temp_dir: Path) -> Path:
    """Save parsed result to a temporary CSV file."""
    temp_dir = Path(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = Path(original_filename).stem
    output_path = temp_dir / f"{base_name}_parsed.csv"
    
    try:        
        if parsed_data.get('parsed_data') is not None:
            df = parsed_data['parsed_data']
            if isinstance(df, pd.DataFrame):
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print(f"Saved parsed result to: {output_path} ({len(df)} rows)")
            else:
                raise ValueError("Parsed data is not a DataFrame")
        else:
            # Save error info
            error_info = {
                'source_file': original_filename,
                'error': parsed_data.get('error', 'Unknown error')
            }
            pd.DataFrame([error_info]).to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"Saved error info to: {output_path}")
            
    except Exception as e:
        print(f"Error saving parsed result: {e}")
        # Fallback to text file
        output_path = temp_dir / f"{base_name}_parsed.txt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Error: {str(e)}")
            
    return output_path


def combine_results(parsed_files: List[Path], output_path: Path):
    """Combine all parsed files into a single final result file."""
    print(f"Combining {len(parsed_files)} parsed files...")
    
    try:        
        dfs = []
        for file_path in parsed_files:
            try:
                if str(file_path).endswith('.csv'):
                    df = pd.read_csv(file_path, encoding='utf-8-sig')
                    dfs.append(df)
            except Exception as e:
                print(f"  Error reading {file_path}: {e}")
                continue
        
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True, sort=False)
            
            # Reorder columns
            existing_cols = combined_df.columns.tolist()
            final_columns = [col for col in REQUIRED_COLUMNS if col in existing_cols]
            final_columns.extend([col for col in existing_cols if col not in final_columns])
            
            combined_df = combined_df[final_columns]
            
            # Save final
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
            
            print(f"Combined results saved to: {output_path} ({len(combined_df)} total rows)")
        else:
            print("No valid data files to combine!")
            
    except Exception as e:
        print(f"Error combining files: {e}")


def process_zip_file(zip_url: str, output_dir: Optional[Path] = None, final_output_path: Optional[Path] = None) -> Optional[Path]:
    """Orchestrate download, extraction, parsing, and combination."""
    
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="restricted_accounts_"))
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
    zip_path = output_dir / "downloaded.zip"
    extract_dir = output_dir / "extracted"
    
    try:
        download_zip(zip_url, zip_path)
        extract_zip(zip_path, extract_dir)
        
        excel_files = find_excel_files(extract_dir)
        
        if not excel_files:
            print("No Excel files found in the zip archive!")
            return None
        
        temp_parse_dir = output_dir / "parsed"
        parsed_file_paths = []
        
        for excel_file in excel_files:
            parsed_data = parse_excel_file(excel_file)
            result_path = save_parsed_result(parsed_data, excel_file.name, temp_parse_dir)
            parsed_file_paths.append(result_path)
        
        if parsed_file_paths:
            if final_output_path is None:
                final_output_path = output_dir / "final_combined_result.csv"
            
            combine_results(parsed_file_paths, final_output_path)
            return final_output_path
            
    except Exception as e:
        print(f"Error during processing: {e}")
        return None
    finally:
        # Cleanup
        if zip_path.exists():
            try:
                os.remove(zip_path)
            except: pass
        if extract_dir.exists():
            try:
                shutil.rmtree(extract_dir)
            except: pass


def get_download_url(file_code: str) -> str:
    """Get the download URL for a file from Bank of Israel API."""
    base_url = "https://mugbalim.boi.gov.il/api/umbraco/api/DownloadFiles"
    return f"{base_url}/{file_code}"


def save_to_idea(final_output_path: Path, today_date: str, ask_user_callback: Optional[Callable[[str], bool]] = None):
    """Save the final output path to IDEA.
    
    Args:
        final_output_path: Path to the CSV file to import
        today_date: Date string for naming
        ask_user_callback: Optional callback function that returns True/False for yes/no question.
                          If None, uses console input().
    """
    project_name = "חשבונות_מוגבלים"
    
    try:
        # Initialize client once
        client = idea.idea_client()
        
        # Robust path finding using pathlib
        working_dir = Path(client.WorkingDirectory)
        projects_dir = working_dir.parent 
        project_path = projects_dir / project_name

        # Create project folder if it doesn't exist
        if not project_path.exists():
            try:
                project_path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                print(f"Error creating projects path: {e}")
                # We do not return here; we might still be able to import to current project
        
        # Ask user for preference
        if ask_user_callback:
            # Use callback (e.g., from GUI)
            switch_project = ask_user_callback(project_name)
        else:
            # Use console input (original behavior)
            print(f"Dedicated Project: {project_name[::-1]}")
            user_input = input("Switch to this project? (y/n): ")
            switch_project = user_input.lower() == "y"
        
        if switch_project:
            print(f"Switching context to {project_name[::-1]}...")
            client.ManagedProject = project_name
        else:
            print("Importing into CURRENT active project...")

        # Perform the import
        print("Importing data...")
        df = pd.read_csv(final_output_path, encoding='utf-8-sig')
        idea.py2idea(df, f"חשבונות_מוגבלים_{today_date}")
        print("Import successful.")
    
    except Exception as e:
        print(f"Error saving to IDEA: {e}")
        print("CSV file is saved to:", final_output_path)


if __name__ == "__main__":
    start_time = time.time()
    
    # Configuration
    FILE_CODE = "WXPRSM02"
    ZIP_URL = get_download_url(FILE_CODE)
    TODAY_DATE = datetime.now().strftime("%Y_%m_%d")
    
    BASE_OUTPUT = Path("./output")
    FINAL_CSV = BASE_OUTPUT / "appended" / f"חשבונות_מוגבלים_{TODAY_DATE}.csv"
    
    print("--- Starting Process ---")
    
    result_path = process_zip_file(
        zip_url=ZIP_URL,
        output_dir=BASE_OUTPUT,
        final_output_path=FINAL_CSV
    )

    proc_time = time.time()
    print(f"Processing time: {proc_time - start_time:.2f} seconds")

    if result_path is not None:
        save_to_idea(result_path, TODAY_DATE)

    end_time = time.time()
    print(f"Total time: {end_time - start_time:.2f} seconds")

    try:
        idea.refresh_file_explorer()
    except Exception:
        pass