import subprocess
import time
import os
import sys
import logging

def search_disk_for_idea():
    search_paths = [os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")]
    for base in search_paths:
        if base:
            potential_path = os.path.join(base, "CaseWare IDEA", "IDEA", "idea.exe")
            if os.path.exists(potential_path):
                return potential_path
    return "Executable not found on disk."

def is_idea_running():
    """
    Checks if IntelliJ IDEA is currently running.
    Returns True if IDEA is running, False otherwise.
    """
    try:
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq idea.exe"], 
                              capture_output=True, 
                              text=True, 
                              check=False)
        return "idea.exe" in result.stdout
    except Exception:
        return False

def start_idea(executable_path):
    """
    Starts the IntelliJ IDEA application using its full path.
    Checks if IDEA is already running before starting it.
    The process is detached so it continues running after the parent script exits.
    
    Note: In debug mode, the debugger may still terminate child processes when stopped.
    This is a limitation of how debuggers handle process trees.
    """
    try:
        # Check if IDEA is already running
        if is_idea_running():
            logging.debug("IDEA is already running, skipping start.")
            return  # IDEA is already running, no need to start it
        
        # Detect if running in debug mode (common debugger environment variables)
        is_debug_mode = any([
            os.environ.get('PYTHONBREAKPOINT'),
            os.environ.get('PYCHARM_HOSTED'),
            os.environ.get('VSCODE_PID'),
            'pydevd' in sys.modules if hasattr(sys, 'modules') else False
        ])
        
        if is_debug_mode:
            logging.debug("Running in debug mode - using Windows 'start' command for maximum independence")
        
        # Method 1: Use Windows 'start' command (most reliable, works in debug and normal mode)
        # The 'start' command creates a process that's independent of the parent
        # /B = Start application without creating a new console window
        try:
            subprocess.Popen(
                f'start "" /B "{executable_path}"',
                shell=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logging.debug(f"Started IDEA using 'start' command: {executable_path}")
            return
        except Exception as e:
            logging.debug(f"Failed to start IDEA with 'start' command: {e}")
            # Fall through to alternative method
        
        # Method 2: Fallback - Use CREATE_NEW_PROCESS_GROUP (less reliable in debug mode)
        try:
            subprocess.Popen(
                [executable_path],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            logging.debug(f"Started IDEA using CREATE_NEW_PROCESS_GROUP: {executable_path}")
        except Exception as e:
            logging.debug(f"Failed to start IDEA with CREATE_NEW_PROCESS_GROUP: {e}")
            raise Exception(f"Failed to start IDEA using all available methods: {e}")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"The file was not found at the specified path: '{executable_path}'")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

def stop_idea():
    """
    Stops all running IntelliJ IDEA processes.
    """
    try:
        import win32com.client as win32com
        client = win32com.Dispatch("Idea.IdeaClient")
        client.Quit()
    except:
        try:
            # Use taskkill to terminate all idea.exe processes
            subprocess.run(["taskkill", "/F", "/IM", "idea.exe"], 
                        capture_output=True, 
                        check=False)
        except Exception as e:
            raise Exception(f"An unexpected error occurred while stopping IDEA: {e}")
    finally:
        client = None