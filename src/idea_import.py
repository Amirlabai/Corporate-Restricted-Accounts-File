"""
Module for importing data to IDEA (Windows-only).
"""

__author__ = "Amir Labai"
__copyright__ = "Copyright 2025, Amir Labai"
__license__ = "MIT"

from pathlib import Path
from tkinter import messagebox

import pandas as pd

# IDEALib is Windows-specific, import only if available
try:
    import IDEALib as idea
    IDEA_AVAILABLE = True
except ImportError:
    IDEA_AVAILABLE = False
    idea = None


def save_to_idea(final_output_path: Path, today_date: str):
    """Save the final output path to IDEA.
    
    Args:
        final_output_path: Path to the CSV file to import
        today_date: Date string for naming
        ask_user_callback: Optional callback function that returns True/False for yes/no question.
                          If None, uses console input().
    """
    if not IDEA_AVAILABLE:
        print("IDEALib not available (Windows-only). Skipping IDEA import.")
        print(f"CSV file saved to: {final_output_path}")
        return
    
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
        

        # Use callback (e.g., from GUI)
        switch_project = messagebox.askyesno(f"החלפת פרויקט", f"האם לעבור לפרויקט: {project_name}?\n\n"
            f"כן - ייבא לפרויקט ייעודי\n"
            f"לא - ייבא לפרויקט הנוכחי הפעיל")
        
        if switch_project == True:
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


def refresh_file_explorer():
    """Refresh IDEA file explorer if available."""
    if IDEA_AVAILABLE:
        try:
            idea.refresh_file_explorer()
        except Exception:
            pass

