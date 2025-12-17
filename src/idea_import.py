"""
Module for importing data to IDEA (Windows-only).
"""

__author__ = "Amir Labai"
__copyright__ = "Copyright 2025, Amir Labai"
__license__ = "MIT"

from pathlib import Path
from tkinter import messagebox

import pandas as pd

import IDEALib as idea



def save_to_idea(final_output_path: Path, today_date: str):
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
                pass
        
        switch_project = messagebox.askyesno(f"החלפת פרויקט", f"האם לעבור לפרויקט: {project_name}?\n\n"
            f"כן - ייבא לפרויקט ייעודי\n"
            f"לא - ייבא לפרויקט הנוכחי הפעיל")
        
        if switch_project == True:
            client.ManagedProject = project_name

        # Perform the impor
        df = pd.read_csv(final_output_path, encoding='utf-8-sig')
        idea.py2idea(df, f"חשבונות_מוגבלים_{today_date}")
        return("success: Import successful.")
    
    except Exception as e:
        return(f"error: Error saving to IDEA: {e}")



def refresh_file_explorer():
    """Refresh IDEA file explorer if available."""
    idea.refresh_file_explorer()

