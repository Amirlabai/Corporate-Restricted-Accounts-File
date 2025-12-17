import subprocess
import os
import sys
import shutil

# Add parent directory to path to allow importing from src
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

import src.version as version

APP_VERSION = version.__version__
APP_NAME = f"Corp restricted accounts {APP_VERSION}"

def archive_old_installers():
    """ 
    Scans for 'installer_files_*' directories from previous versions and moves them
    into an 'old_installer_files' archive folder.
    """
    ARCHIVE_DIR = "old_installer_files"
    current_version_prefix = f"installer_files_{APP_VERSION}"
    print("--- Archiving old installers ---")

    # Ensure the archive directory exists, creating it if necessary
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        print(f"ℹ️  Created archive directory: {ARCHIVE_DIR}")

    found_old_files = False
    # Iterate over every item in the current directory
    for item in os.listdir("."):
        # Process only items that are directories and match the naming pattern
        if os.path.isdir(item) and item.startswith("installer_files_"):
            # If the directory doesn't match the current version, archive it
            if not item.startswith(current_version_prefix):
                source_path = item
                dest_path = os.path.join(ARCHIVE_DIR, item)
                print(f"🗂️  Archiving {source_path} -> {dest_path}")
                shutil.move(source_path, dest_path)
                found_old_files = True

    if not found_old_files:
        print("✅ No old installer directories found to archive.")
    print("--------------------------------\n")

def run_pyinstaller():
    """
    Runs the PyInstaller command with dynamically generated paths based on the current version.
    Deletes the old .spec file and handles existing directories by appending a counter.
    """
    # --- NEW: Archive old build directories before starting ---
    archive_old_installers()

    # --- 1. Clean up previous build files ---
    spec_file = APP_NAME +".spec"
    if os.path.exists(spec_file):
        try:
            os.remove(spec_file)
            print(f"✅ Deleted existing spec file: {spec_file}")
        except OSError as e:
            print(f"❌ ERROR: Could not delete spec file: {e}")

    # --- 2. Determine unique output directory ---
    base_folder_name = f"installer_files_{APP_VERSION}"
    installer_folder = base_folder_name
    
    counter = 1
    # Loop to find a unique directory name by appending a counter
    while os.path.exists(installer_folder):
        installer_folder = f"{base_folder_name}_{counter}"
        counter += 1

    # --- 3. Create the full paths for dist and work directories ---
    # os.path.join is used to create system-agnostic paths (works on Windows, Mac, Linux)
    dist_path = os.path.join(".", installer_folder, "dist")
    work_path = os.path.join(".", installer_folder, "build")
    
    # PyInstaller will create these, but we can print the chosen path
    print(f"ℹ️  Output will be in directory: {installer_folder}")

    # --- 4. Construct the command as a list of arguments ---
    # This is the recommended and safest way to run external commands in Python
    command = [
        'pyinstaller',
        '--noconsole',
        #'--icon=assets/icons/iacslogo.ico',
        F'--name={APP_NAME}',
        f'--distpath={dist_path}',
        f'--workpath={work_path}',
        #'--add-data=assets:assets',
        'src/gui.py'
    ]

    print("\n--- Running PyInstaller ---")
    print(f"Command: {' '.join(command)}") # Print the command for verification
    print("---------------------------\n")

    try:
        # --- 5. Execute the command ---
        # check=True will raise an exception if the command returns a non-zero exit code (i.e., fails)
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        
        print("✅ PyInstaller completed successfully!")
        print("\n--- PyInstaller Output ---")
        print(result.stdout)
        print("--------------------------")

    except FileNotFoundError:
        print("❌ ERROR: 'pyinstaller' command not found.")
        print("Please ensure PyInstaller is installed (`pip install pyinstaller`) and that it's in your system's PATH.")
    except subprocess.CalledProcessError as e:
        # This block runs if the command fails (returns a non-zero exit code)
        print("❌ ERROR: PyInstaller failed to execute.")
        print(f"Return Code: {e.returncode}")
        print("\n--- STDOUT ---")
        print(e.stdout)
        print("\n--- STDERR ---")
        print(e.stderr)
        print("--------------")
    finally:
        # After PyInstaller completes, zip the dist\Corp restricted accounts folder and save in project root
        dist_corp_dir = os.path.join(installer_folder, "dist", APP_NAME)
        zip_path = os.path.join(".", f"corp restricted accounts.zip")
        import zipfile

        if os.path.exists(dist_corp_dir):
            print(f"Zipping '{dist_corp_dir}' to '{zip_path}'...")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(dist_corp_dir):
                    for file in files:
                        abs_file = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_file, start=dist_corp_dir)
                        zipf.write(abs_file, arcname=rel_path)
            print(f"✅ Created zip archive at: {zip_path}")
        else:
            print(f"❌ ERROR: Directory not found for zipping: {dist_corp_dir}")

if __name__ == "__main__":
    run_pyinstaller()

