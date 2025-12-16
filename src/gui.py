"""
Simple GUI application for downloading and parsing Bank of Israel restricted accounts data.
"""

__author__ = "Amir Labai"
__copyright__ = "Copyright 2025, Amir Labai"
__license__ = "MIT"

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os
import json

# Import the main script functions
from download_and_parse import (
    get_download_url,
    process_zip_file,
    save_to_idea
)

# Import version information
from version import __version__, __release_date__


class RestrictedAccountsGUI:
    """Main GUI application class."""
    
    CONFIG_FILE = Path("gui_config.json")
    
    def __init__(self, root):
        self.root = root
        self.root.title("חשבונות מוגבלים - Corporate Restricted Accounts")
        self.root.geometry("650x600")
        self.root.resizable(True, True)
        
        # Configure RTL support
        self.root.option_add('*Font', 'Arial 10')
        
        # Load saved configuration
        self.config = self.load_config()
        
        # Output directory - use saved config or default
        saved_folder = self.config.get('output_folder', None)
        if saved_folder:
            self.output_folder = Path(saved_folder)
            # Set base_output based on saved folder
            if self.output_folder.name == "appended":
                self.base_output = self.output_folder.parent
            else:
                self.base_output = self.output_folder.parent
        else:
            self.base_output = Path("./output")
            self.output_folder = self.base_output / "appended"
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Create and arrange UI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="מערכת הורדה ועיבוד חשבונות מוגבלים",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Folder selection section
        folder_frame = ttk.LabelFrame(main_frame, padding="10")
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Folder path entry
        folder_label = ttk.Label(folder_frame, text=":תיקיית שמירה", font=('Arial', 10, 'bold'))
        folder_label.pack(pady=(0, 5), anchor='e')

        path_frame = ttk.Frame(folder_frame)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text=":נתיב", width=8).pack(side=tk.RIGHT, padx=5)
        
        self.folder_path_var = tk.StringVar(value=str(self.output_folder))
        self.folder_entry = ttk.Entry(
            path_frame,
            textvariable=self.folder_path_var,
            width=50
        )
        self.folder_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        
        # Browse and Save buttons frame
        buttons_frame = ttk.Frame(folder_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        self.browse_button = ttk.Button(
            buttons_frame,
            text="...עיין",
            command=self.browse_folder,
            width=15
        )
        self.browse_button.pack(side=tk.RIGHT, padx=5)
        
        self.save_folder_button = ttk.Button(
            buttons_frame,
            text="שמור הגדרה",
            command=self.save_folder_setting,
            width=15
        )
        self.save_folder_button.pack(side=tk.RIGHT, padx=5)
        
        # Run button
        self.run_button = ttk.Button(
            main_frame,
            text="הפעל תהליך הורדה ועיבוד",
            command=self.run_process,
            width=30
        )
        self.run_button.pack(pady=5)
        
        # Open folder button
        self.open_folder_button = ttk.Button(
            main_frame,
            text="פתח תיקיית קבצים",
            command=self.open_output_folder,
            width=30
        )
        self.open_folder_button.pack(pady=5)
        
        # Status/Log area
        log_label = ttk.Label(main_frame, text=":יומן פעילות", font=('Arial', 10, 'bold'))
        log_label.pack(pady=(20, 5), anchor='e')
        
        self.log_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            width=70,
            wrap=tk.WORD,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="מוכן לפעולה")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor='w'
        )
        status_bar.pack(fill=tk.X, pady=(10, 0))

        self.exit_button = ttk.Button(
            main_frame,
            text="יציאה",
            command=self.exit_program,
            width=15
        )
        self.exit_button.pack(pady=10)
        
        # Version banner at the bottom
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        version_label = ttk.Label(
            version_frame,
            text=f"{__version__} גרסה",
            font=('Arial', 8),
            foreground='gray'
        )
        version_label.pack(anchor='center')
        
    def exit_program(self):
        """Exit the program."""
        self.root.quit()
        
    def load_config(self) -> dict:
        """Load configuration from file."""
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return {}
        return {}
    
    def save_config(self, config: dict):
        """Save configuration to file."""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לשמור הגדרות:\n{str(e)}")
    
    def browse_folder(self):
        """Open folder browser dialog."""
        initial_dir = self.folder_path_var.get()
        if not os.path.exists(initial_dir):
            initial_dir = os.getcwd()
        
        folder = filedialog.askdirectory(
            title="בחר תיקיית שמירה",
            initialdir=initial_dir
        )
        
        if folder:
            self.folder_path_var.set(folder)
            self.output_folder = Path(folder)
    
    def save_folder_setting(self):
        """Save the current folder setting."""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            messagebox.showwarning("אזהרה", "אנא בחר תיקייה")
            return
        
        # Validate path
        try:
            path_obj = Path(folder_path)
            # Create directory if it doesn't exist
            path_obj.mkdir(parents=True, exist_ok=True)
            
            # Update output folder
            self.output_folder = path_obj
            
            # Save to config
            self.config['output_folder'] = str(path_obj.absolute())
            self.save_config(self.config)
            
            messagebox.showinfo("הצלחה", f"התיקייה נשמרה:\n{path_obj.absolute()}")
            self.log(f"תיקיית שמירה עודכנה: {path_obj.absolute()}")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לשמור תיקייה:\n{str(e)}")
    
    def log(self, message: str):
        """Add message to log area."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status: str):
        """Update status bar."""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def ask_switch_project(self, project_name: str) -> bool:
        """Show messagebox to ask user if they want to switch project.
        
        Args:
            project_name: Name of the project
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        result = messagebox.askyesno(
            "החלפת פרויקט",
            f"האם לעבור לפרויקט: {project_name}?\n\n"
            f"כן - ייבא לפרויקט ייעודי\n"
            f"לא - ייבא לפרויקט הנוכחי הפעיל"
        )
        return result
        
    def run_process(self):
        """Run the download and parse process in a separate thread."""
        # Disable button during processing
        self.run_button.config(state='disabled')
        self.open_folder_button.config(state='disabled')
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Run in thread to prevent UI freezing
        thread = threading.Thread(target=self._run_process_thread)
        thread.daemon = True
        thread.start()
        
    def _run_process_thread(self):
        """Internal method to run the process."""
        # Create a custom stdout that redirects to log
        class LogRedirect:
            def __init__(self, log_func):
                self.log_func = log_func
                self.buffer = ""
                
            def write(self, text):
                if text.strip():
                    self.buffer += text
                    # Flush on newline
                    if '\n' in self.buffer:
                        lines = self.buffer.split('\n')
                        for line in lines[:-1]:
                            if line.strip():
                                self.log_func(line.strip())
                        self.buffer = lines[-1]
                        
            def flush(self):
                if self.buffer.strip():
                    self.log_func(self.buffer.strip())
                    self.buffer = ""
        
        log_redirect = LogRedirect(self.log)
        old_stdout = sys.stdout
        
        try:
            sys.stdout = log_redirect
            
            self.log("--- התחלת תהליך ---")
            self.update_status("מתחיל תהליך...")
            
            # Configuration
            FILE_CODE = "WXPRSM02"
            ZIP_URL = get_download_url(FILE_CODE)
            TODAY_DATE = datetime.now().strftime("%Y_%m_%d")
            
            # Get current output folder from entry (in case user changed it but didn't save)
            current_folder = Path(self.folder_path_var.get().strip())
            if current_folder:
                self.output_folder = current_folder
            
            FINAL_CSV = self.output_folder / f"חשבונות_מוגבלים_{TODAY_DATE}.csv"
            
            # Ensure output directory exists
            self.output_folder.mkdir(parents=True, exist_ok=True)
            
            # Use parent directory for base_output (for temporary files like downloaded.zip, extracted, parsed)
            # This keeps temp files separate from the final output
            if self.output_folder.name == "appended":
                self.base_output = self.output_folder.parent
            else:
                # For custom folders, use the parent directory for temp files
                self.base_output = self.output_folder.parent
            
            self.log(f"קוד קובץ: {FILE_CODE}")
            self.log(f"תאריך: {TODAY_DATE}")
            self.log(f"נתיב פלט: {FINAL_CSV}")
            self.log("")
            
            # Process zip file
            self.update_status("מוריד קובץ...")
            
            result_path = process_zip_file(
                zip_url=ZIP_URL,
                output_dir=self.base_output,
                final_output_path=FINAL_CSV
            )
            
            if result_path is None:
                self.log("שגיאה: לא ניתן לעבד את הקובץ")
                self.update_status("שגיאה בעיבוד")
                messagebox.showerror("שגיאה", "התהליך נכשל. בדוק את יומן הפעילות.")
                return
            
            self.log("")
            self.log(f"עיבוד הושלם בהצלחה!")
            self.log(f"קובץ נשמר ב: {result_path}")
            self.log("")
            
            # Save to IDEA
            self.update_status("מייבא ל-IDEA...")
            
            # Use callback for yes/no question
            save_to_idea(
                result_path,
                TODAY_DATE,
                ask_user_callback=self.ask_switch_project
            )
            
            self.log("ייבוא ל-IDEA הושלם בהצלחה!")
            self.update_status("התהליך הושלם בהצלחה")
            
            messagebox.showinfo(
                "הצלחה",
                f"התהליך הושלם בהצלחה!\n\nקובץ נשמר ב:\n{result_path}"
            )
            
        except Exception as e:
            error_msg = f"שגיאה: {str(e)}"
            self.log(error_msg)
            self.update_status("שגיאה")
            messagebox.showerror("שגיאה", f"אירעה שגיאה:\n{error_msg}")
            
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            # Re-enable buttons
            self.run_button.config(state='normal')
            self.open_folder_button.config(state='normal')
            
    def open_output_folder(self):
        """Open the output folder in file explorer."""
        try:
            # Ensure folder exists
            self.output_folder.mkdir(parents=True, exist_ok=True)
            
            # Open folder based on OS
            if sys.platform == "win32":
                os.startfile(self.output_folder)
            elif sys.platform == "darwin":
                subprocess.run(["open", str(self.output_folder)])
            else:
                subprocess.run(["xdg-open", str(self.output_folder)])
                
            self.log(f"נפתחה תיקייה: {self.output_folder}")
            
        except Exception as e:
            error_msg = f"לא ניתן לפתוח תיקייה: {str(e)}"
            self.log(error_msg)
            messagebox.showerror("שגיאה", error_msg)


def main():
    """Main entry point for GUI application."""
    root = tk.Tk()
    app = RestrictedAccountsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

