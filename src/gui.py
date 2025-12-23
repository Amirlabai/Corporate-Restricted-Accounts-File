"""
Simple GUI application for downloading and parsing Bank of Israel restricted accounts data.
"""

__author__ = "Amir Labai"
__copyright__ = "Copyright 2025, Amir Labai"
__license__ = "MIT"

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os
import json
import shutil
import requests
import pandas as pd
import re
from idea_import import save_to_idea, refresh_file_explorer

# Import version information
from version import __version__, __release_date__

def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for Nuitka/PyInstaller """
	try:
		# Nuitka/PyInstaller creates a temp folder and stores path in sys._MEIPASS
		# However, for data files meant to be alongside the exe, we use sys.executable
		if getattr(sys, 'frozen', False):
			# If the application is run as a bundle/frozen executable
			base_path = os.path.dirname(sys.executable)
			base_path = os.path.join(base_path,'_internal')
		else:
			# If running as a normal script
			base_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

		full_path = os.path.join(base_path, relative_path)
		return full_path
	except Exception as e:
		# Fallback or default path if needed
		return os.path.join(os.path.abspath("."), relative_path)


# Set appearance mode and color theme
ctk.set_appearance_mode("system")  # "system", "dark", or "light"
ctk.set_default_color_theme(resource_path("assets/custom-theme.json"))  # "blue", "green", or "dark-blue"


class RestrictedAccountsGUI:
    """Main GUI application class."""
    
    CONFIG_FILE = Path(resource_path("assets/gui_config.json"))
    
    def __init__(self, root):
        self.root = root
        self.root.title("ניתוח חשבונות מוגבלים")
        self.root.resizable(True, True)
        
        # Track downloaded file
        self.downloaded_file_path = None
        
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
        
        # Auto-download on startup
        self.root.after(100, self.download_from_github)
        
    def setup_ui(self):
        """Create and arrange UI components."""
        tab_banner_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        tab_banner_frame.pack(fill="x")

        help_button = ctk.CTkButton(
            tab_banner_frame,
            text="עזרה",
            command=self.show_help,
            corner_radius=0,
            fg_color="transparent"
        )
        help_button.pack(side="right")

        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True)

        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="ניתוח חשבונות מוגבלים",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack()
        
        # Folder selection section
        folder_frame = ctk.CTkFrame(main_frame)
        folder_frame.pack(fill="x", pady=(0, 5), padx=10)

        path_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        path_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(path_frame, text=":תיקיית שמירה", width=80).pack(side="right", padx=5)
        
        self.folder_path_var = tk.StringVar(value=str(self.output_folder))
        # Use a frame styled like an entry for read-only display
        self.folder_entry_frame = ctk.CTkFrame(path_frame, fg_color=("gray90", "gray13"), corner_radius=6)
        self.folder_entry_frame.pack(side="right", fill="x", expand=True, padx=5)
        
        self.folder_path_label = ctk.CTkLabel(
            self.folder_entry_frame,
            textvariable=self.folder_path_var,
            anchor='w',
            padx=10,
            pady=8
        )
        self.folder_path_label.pack(side="left", fill="x", expand=True)
        
        # Browse and Save buttons frame
        buttons_frame = ctk.CTkFrame(folder_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=5, padx=10)
        
        self.browse_button = ctk.CTkButton(
            buttons_frame,
            text="...עיין",
            command=self.browse_folder,
            width=120
        )
        self.browse_button.pack(side="right", padx=5)
        
        self.open_folder_button = ctk.CTkButton(
            buttons_frame,
            text="פתח תיקיית קבצים",
            command=self.open_output_folder,
            width=200
        )
        self.open_folder_button.pack(side="right", padx=5)

        import_idea_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        import_idea_frame.pack(fill="x", pady=5, padx=10)

        self.import_idea_button = ctk.CTkButton(
            import_idea_frame,
            text="IDEA - ייבא ל",
            command=self.import_to_idea,
            width=150,
            state='disabled'
        )
        self.import_idea_button.pack(padx=5)
        
        # Search section
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="both", expand=True, pady=(5, 5), padx=10)
        
        search_input_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_input_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(search_input_frame, text=":מספר חשבון מוגבל", width=120).pack(side="right", padx=5)
        
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_input_frame,
            textvariable=self.search_var,
            width=80
        )
        self.search_entry.pack(side="right", fill="x", expand=True, padx=5)
        self.search_entry.bind('<KeyPress>', self._validate_digit_only)
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        ctk.CTkLabel(search_input_frame, text=":תאריך צ'ק", width=120).pack(side="right", padx=5)
        
        # Date input fields container
        date_fields_frame = ctk.CTkFrame(search_input_frame, fg_color="transparent")
        date_fields_frame.pack(side="right", padx=5)
        
        # Year field
        self.year_var = tk.StringVar()
        self.year_entry = ctk.CTkEntry(
            date_fields_frame,
            textvariable=self.year_var,
            width=60,
            placeholder_text="yyyy"
        )
        self.year_entry.pack(side="right", padx=2)
        self.year_entry.bind('<KeyPress>', self._validate_digit_only)
        self.year_entry.bind('<KeyRelease>', lambda e: self._handle_year_input(e))
        
        # Separator label
        ctk.CTkLabel(date_fields_frame, text="/", width=10).pack(side="right", padx=1)
        
        # Month field
        self.month_var = tk.StringVar()
        self.month_entry = ctk.CTkEntry(
            date_fields_frame,
            textvariable=self.month_var,
            width=40,
            placeholder_text="mm"
        )
        self.month_entry.pack(side="right", padx=2)
        self.month_entry.bind('<KeyPress>', self._validate_digit_only)
        self.month_entry.bind('<KeyRelease>', lambda e: self._handle_month_input(e))
        
        # Separator label
        ctk.CTkLabel(date_fields_frame, text="/", width=10).pack(side="right", padx=1)
        
        # Day field
        self.day_var = tk.StringVar()
        self.day_entry = ctk.CTkEntry(
            date_fields_frame,
            textvariable=self.day_var,
            width=40,
            placeholder_text="dd"
        )
        self.day_entry.pack(side="right", padx=2)
        self.day_entry.bind('<KeyPress>', self._validate_digit_only)
        self.day_entry.bind('<KeyRelease>', lambda e: self._handle_day_input(e))
        
        # Initialize date range (will be updated when file is loaded)
        self.min_year = 1900
        self.max_year = 2100

        self.search_button = ctk.CTkButton(
            search_input_frame,
            text="חפש",
            command=self.perform_search,
            width=80
        )
        self.search_button.pack(side="right", padx=5)
        
        # Search results
        results_label = ctk.CTkLabel(search_frame, text=":תוצאות חיפוש", font=ctk.CTkFont(size=11, weight="bold"))
        results_label.pack(anchor='e', padx=10)
        
        # Create treeview for results (using ttk.Treeview wrapped in CTkFrame)
        results_frame = ctk.CTkFrame(search_frame)
        results_frame.pack(fill="both", expand=True, pady=5, padx=10)
        
        # Inner frame for treeview (needed for proper styling)
        tree_container = tk.Frame(results_frame)
        tree_container.pack(fill="both", expand=True)
        
        # Scrollbars for treeview
        scrollbar_y = ttk.Scrollbar(tree_container, orient=tk.VERTICAL)
        
        self.results_tree = ttk.Treeview(
            tree_container,
            columns=('מספר_בנק', 'מספר_סניף', 'מספר_חשבון_מוגבל', 'תאריך_סיום_הגבלה', 'שם_סניף'),
            show='headings',
            yscrollcommand=scrollbar_y.set,
        )

        # Style the treeview headers to be bold
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

        # Configure columns in the desired order with right alignment (RTL)
        self.results_tree.heading('מספר_בנק', text='מספר בנק', anchor='e')
        self.results_tree.heading('מספר_סניף', text='מספר סניף', anchor='e')
        self.results_tree.heading('מספר_חשבון_מוגבל', text='מספר חשבון מוגבל', anchor='e')
        self.results_tree.heading('תאריך_סיום_הגבלה', text='תאריך סיום הגבלה', anchor='e')
        self.results_tree.heading('שם_סניף', text='שם סניף', anchor='e')
        
        self.results_tree.column('מספר_בנק', width=100, anchor='e')
        self.results_tree.column('מספר_סניף', width=100, anchor='e')
        self.results_tree.column('מספר_חשבון_מוגבל', width=150, anchor='e')
        self.results_tree.column('תאריך_סיום_הגבלה', width=120, anchor='e')
        self.results_tree.column('שם_סניף', width=150, anchor='e')
        
        scrollbar_y.configure(command=self.results_tree.yview)
        
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status/Log area
        log_label = ctk.CTkLabel(main_frame, text=":יומן פעילות", font=ctk.CTkFont(weight="bold"))
        log_label.pack(anchor='e', padx=10)
        
        self.log_text = ctk.CTkTextbox(
            main_frame,
            height=100,
            wrap="word",
        )
        self.log_text.pack(fill="both", expand=False, padx=10)
        
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5, padx=10)
        # Status bar
        self.status_var = tk.StringVar(value="מוכן לפעולה")
        status_bar = ctk.CTkLabel(
            status_frame,
            textvariable=self.status_var,
            anchor='w',
        )
        status_bar.pack(side='right', padx=10)

        self.exit_button = ctk.CTkButton(
            main_frame,
            text="יציאה",
            command=self.exit_program,
            width=120
        )
        self.exit_button.pack()
        
        # Version banner at the bottom
        version_label = ctk.CTkLabel(
            main_frame,
            text=f"{__version__} גרסה",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        version_label.pack(side="bottom")

        self.root.geometry("900x750+50+50")
        
    def show_help(self):
        """Show help dialog."""
        help_file = resource_path("assets/manual.pdf")
        if os.path.exists(help_file):
            subprocess.Popen([help_file], shell=True)
        else:
            messagebox.showerror("שגיאה", "קובץ העזרה לא נמצא")

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
    
    def _auto_save_folder(self):
        """Automatically save folder setting when changed."""
        folder_path = self.folder_path_var.get().strip()
        
        if not folder_path:
            return
        
        # Validate path
        try:
            path_obj = Path(folder_path)
            # Create directory if it doesn't exist
            path_obj.mkdir(parents=True, exist_ok=True)
            
            old_folder = self.output_folder
            # Update output folder
            self.output_folder = path_obj
            
            # Save to config
            self.config['output_folder'] = str(path_obj.absolute())
            self.save_config(self.config)
            
            # Move downloaded file if it exists
            self._move_downloaded_file(old_folder, self.output_folder)
            
            self.log(f"תיקיית שמירה עודכנה אוטומטית: {path_obj.absolute()}")
            
        except Exception as e:
            # Silently fail for auto-save (don't show error popup)
            self.log(f"שגיאה בשמירה אוטומטית: {str(e)}")
    
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
            old_folder = self.output_folder
            self.folder_path_var.set(folder)
            self.output_folder = Path(folder)
            
            # Automatically save the setting
            self.config['output_folder'] = str(self.output_folder.absolute())
            self.save_config(self.config)
            
            # Move downloaded file if it exists
            self._move_downloaded_file(old_folder, self.output_folder)
            
            self.log(f"תיקיית שמירה עודכנה: {self.output_folder.absolute()}")
    
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
            
            old_folder = self.output_folder
            # Update output folder
            self.output_folder = path_obj
            
            # Save to config
            self.config['output_folder'] = str(path_obj.absolute())
            self.save_config(self.config)
            
            # Move downloaded file if it exists
            self._move_downloaded_file(old_folder, self.output_folder)
            
            messagebox.showinfo("הצלחה", f"התיקייה נשמרה:\n{path_obj.absolute()}")
            self.log(f"תיקיית שמירה עודכנה: {path_obj.absolute()}")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"לא ניתן לשמור תיקייה:\n{str(e)}")
    
    def log(self, message: str):
        """Add message to log area."""
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
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
    
    def _move_downloaded_file(self, old_folder: Path, new_folder: Path):
        """Move downloaded file when folder path changes."""
        if self.downloaded_file_path and self.downloaded_file_path.exists():
            try:
                new_folder.mkdir(parents=True, exist_ok=True)
                new_file_path = new_folder / self.downloaded_file_path.name
                
                # Move file
                shutil.move(str(self.downloaded_file_path), str(new_file_path))
                
                self.downloaded_file_path = new_file_path
                self.log(f"קובץ הועבר ל: {new_file_path}")
            except Exception as e:
                self.log(f"שגיאה בהעברת קובץ: {str(e)}")
    
    def _check_url_accessible(self, url: str, timeout: int = 10) -> bool:
        """Check if a URL is accessible.
        
        Args:
            url: The URL to check
            timeout: Request timeout in seconds (default: 10)
            
        Returns:
            True if URL is accessible, False otherwise
        """
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            # Accept both 2xx and 3xx status codes as accessible
            return response.status_code < 400
        except requests.exceptions.Timeout:
            self.log(f"Timeout: לא ניתן להגיע ל-{url}")
            return False
        except requests.exceptions.ConnectionError:
            self.log(f"Connection Error: לא ניתן להתחבר ל-{url}")
            return False
        except requests.exceptions.RequestException as e:
            self.log(f"Request Error: שגיאה בבדיקת {url}: {str(e)}")
            return False
        except Exception as e:
            self.log(f"Unexpected Error: שגיאה לא צפויה בבדיקת {url}: {str(e)}")
            return False
    
    def download_from_github(self):
        """Download the latest CSV file from GitHub repository."""
        self.update_status("...מוריד קובץ")
        
        thread = threading.Thread(target=self._download_from_github_thread)
        thread.daemon = True
        thread.start()
    
    def _download_from_github_thread(self):
        """Internal method to download from GitHub."""
        try:
            # Get current output folder
            current_folder = Path(self.folder_path_var.get().strip())
            if current_folder:
                self.output_folder = current_folder
            else:
                self.output_folder = self.base_output / "appended"
            
            self.output_folder.mkdir(parents=True, exist_ok=True)
            
            # Check if file for today already exists
            today_date = datetime.now().strftime("%Y_%m_%d")
            today_filename = f"חשבונות_מוגבלים_{today_date}.csv"
            today_file_path = self.output_folder / today_filename
            
            if today_file_path.exists():
                self.log(f"קובץ של היום כבר קיים: {today_file_path}")
                self.downloaded_file_path = today_file_path
                self.import_idea_button.configure(state='normal')
                self.update_status("קובץ של היום כבר קיים")
                return
            
            # GitHub API endpoint for repository contents
            repo_url = "https://api.github.com/repos/Amirlabai/Corporate-Restricted-Accounts-File/contents/output/appended"
            
            # Verify URL is accessible before attempting download
            self.log("בודק נגישות למאגר...")
            if not self._check_url_accessible(repo_url):
                error_msg = "לא ניתן להגיע למאגר. אנא בדוק את החיבור לאינטרנט."
                self.log(error_msg)
                self.update_status("שגיאה: לא ניתן להגיע למאגר")
                messagebox.showerror("שגיאה", error_msg)
                return
            
            self.log("...מתחבר")
            response = requests.get(repo_url, timeout=30)
            response.raise_for_status()
            
            files = response.json()
            
            # Filter CSV files and find the latest one
            csv_files = [f for f in files if f['name'].endswith('.csv') and 'חשבונות_מוגבלים' in f['name']]
            
            if not csv_files:
                messagebox.showerror("שגיאה", "לא נמצאו קבצים במאגר")
                self.update_status("שגיאה")
                return
            
            # Sort by name (which includes date) to get the latest
            latest_file = max(csv_files, key=lambda x: x['name'])
            
            self.log(f"מוצא קובץ: {latest_file['name']}")
            
            # Download the file
            download_url = latest_file['download_url']
            self.log(f"מוריד מ: {os.path.basename(download_url)}")
            
            # Verify download URL is accessible
            if not self._check_url_accessible(download_url):
                error_msg = "לא ניתן להגיע לקובץ להורדה. אנא נסה שוב מאוחר יותר."
                self.log(error_msg)
                self.update_status("שגיאה: לא ניתן להוריד קובץ")
                messagebox.showerror("שגיאה", error_msg)
                return
            
            file_response = requests.get(download_url, stream=True, timeout=60)
            file_response.raise_for_status()
            
            # Save file
            file_path = self.output_folder / latest_file['name']
            
            with open(file_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.downloaded_file_path = file_path
            self.import_idea_button.configure(state='normal')
            
            self.log(f"הורדה הושלמה: {file_path}")
            self.update_status("הורדה הושלמה בהצלחה")
            
            messagebox.showinfo(
                "הצלחה",
                f"הקובץ הורד בהצלחה!\n\n{file_path}"
            )
            
        except Exception as e:
            error_msg = f"שגיאה בהורדה: {str(e)}"
            self.log(error_msg)
            self.update_status("שגיאה")
            messagebox.showerror("שגיאה", error_msg)
    
    def import_to_idea(self):
        """Import the downloaded file to IDEA."""
        if not self.downloaded_file_path or not self.downloaded_file_path.exists():
            messagebox.showerror("שגיאה", "אין קובץ לייבוא. אנא הורד קובץ תחילה.")
            return
        
        self.import_idea_button.configure(state='disabled')
        self.update_status("...IDEA - מייבא ל")
        self.root.update()  # Update UI to show status change
        
        try:
            # Extract date from filename (format: חשבונות_מוגבלים_YYYY_MM_DD.csv)
            filename = self.downloaded_file_path.stem
            date_match = re.search(r'(\d{4}_\d{2}_\d{2})', filename)
            
            if date_match:
                today_date = date_match.group(1)
            else:
                today_date = datetime.now().strftime("%Y_%m_%d")
            
            self.log(f"מייבא ל-IDEA: {self.downloaded_file_path}")
            self.root.update()  # Update UI to show log message
            
            save_to_idea(self.downloaded_file_path, today_date)
            
            self.log("ייבוא ל-IDEA הושלם בהצלחה!")
            self.update_status("ייבוא הושלם בהצלחה")
            
            messagebox.showinfo(
                "הצלחה",
                f"הקובץ יובא ל-IDEA בהצלחה!\n\n{self.downloaded_file_path}"
            )
            
        except Exception as e:
            error_msg = f"שגיאה בייבוא: {str(e)}"
            self.log(error_msg)
            self.update_status("שגיאה")
            messagebox.showerror("שגיאה", error_msg)
        finally:
            refresh_file_explorer()
            self.import_idea_button.configure(state='normal')
    
    def on_search_change(self, event=None):
        """Handle search input changes."""
        # Auto-search as user types (debounced)
        if hasattr(self, '_search_timer'):
            self.root.after_cancel(self._search_timer)
        self._search_timer = self.root.after(500, self.perform_search)
    
    def _validate_digit_only(self, event):
        """Validate that only digits are entered in date fields."""
        # Allow backspace, delete, tab, and arrow keys
        if event.keysym in ('BackSpace', 'Delete', 'Tab', 'Left', 'Right', 'Home', 'End'):
            return
        
        # Allow Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        if event.state & 0x4 and event.keysym in ('a', 'c', 'v', 'x'):
            return
        
        # Only allow digits
        if not event.char.isdigit():
            return 'break'  # Block the character
    
    def _handle_day_input(self, event=None):
        """Handle day input with validation and auto-advance."""
        day_str = self.day_var.get().strip()
        
        # Only allow digits
        day_str = ''.join(filter(str.isdigit, day_str))
        
        if day_str:
            day_int = int(day_str)
            
            # Validate day <= 31
            if day_int > 31:
                day_str = '31'
                self.day_var.set('31')
                self.day_entry.icursor(tk.END)
            
            # Auto-advance to month if valid 2-digit day
            if len(day_str) == 2 and 1 <= day_int <= 31:
                self.month_entry.focus()
                self.month_entry.icursor(0)
        
        # Trigger search
        self._trigger_date_search()
    
    def _handle_month_input(self, event=None):
        """Handle month input with validation and auto-advance."""
        month_str = self.month_var.get().strip()
        
        # Only allow digits
        month_str = ''.join(filter(str.isdigit, month_str))
        
        if month_str:
            month_int = int(month_str)
            
            # Validate month <= 12
            if month_int > 12:
                month_str = '12'
                self.month_var.set('12')
                self.month_entry.icursor(tk.END)
            
            # Auto-advance to year if valid 2-digit month
            if len(month_str) == 2 and 1 <= month_int <= 12:
                self.year_entry.focus()
                self.year_entry.icursor(0)
        
        # Trigger search
        self._trigger_date_search()
    
    def _handle_year_input(self, event=None):
        """Handle year input with validation."""
        year_str = self.year_var.get().strip()
        
        # Only allow digits
        year_str = ''.join(filter(str.isdigit, year_str))
        
        if year_str:
            # Limit to 4 digits
            if len(year_str) > 4:
                year_str = year_str[:4]
                self.year_var.set(year_str)
            
            if len(year_str) == 4:
                year_int = int(year_str)
                
                # Validate year is within range
                if year_int < self.min_year:
                    year_str = str(self.min_year)
                    self.year_var.set(year_str)
                elif year_int > self.max_year:
                    year_str = str(self.max_year)
                    self.year_var.set(year_str)
        
        # Trigger search
        self._trigger_date_search()
    
    def _trigger_date_search(self):
        """Trigger search when date fields change."""
        # Auto-search as user types (debounced)
        if hasattr(self, '_date_timer'):
            self.root.after_cancel(self._date_timer)
        self._date_timer = self.root.after(500, self.perform_search)
    
    def _update_date_range_from_file(self, df):
        """Update min/max year range from the loaded file."""
        try:
            if 'תאריך_סיום_הגבלה' in df.columns:
                # Convert date column to datetime (format: yyyy-mm-dd)
                df['תאריך_סיום_הגבלה_parsed'] = pd.to_datetime(
                    df['תאריך_סיום_הגבלה'], 
                    format='%Y-%m-%d',
                    errors='coerce'
                )
                
                # Get min and max dates
                valid_dates = df['תאריך_סיום_הגבלה_parsed'].dropna()
                if len(valid_dates) > 0:
                    min_date = valid_dates.min()
                    max_date = valid_dates.max()
                    
                    self.min_year = min_date.year
                    self.max_year = max_date.year
                    
                    self.log(f"טווח תאריכים בקובץ: {self.min_year}-{self.max_year}")
        except Exception as e:
            # Keep default range if error
            self.log(f"שגיאה בעדכון טווח תאריכים: {str(e)}")
    
    def perform_search(self):
        """Search for account number and/or date in the downloaded file."""
        search_term = self.search_var.get().strip()
        
        # Get date from three separate fields
        day_str = self.day_var.get().strip()
        month_str = self.month_var.get().strip()
        year_str = self.year_var.get().strip()
        
        # Combine date fields if all are provided
        date_term = None
        if day_str and month_str and year_str:
            try:
                # Pad with zeros if needed
                day_str = day_str.zfill(2)
                month_str = month_str.zfill(2)
                year_str = year_str.zfill(4)
                date_term = f"{day_str}/{month_str}/{year_str}"
            except:
                pass
        
        # If both are empty, clear results
        if not search_term and not date_term:
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            return
        
        if not self.downloaded_file_path or not self.downloaded_file_path.exists():
            messagebox.showwarning("אזהרה", "אין קובץ לחיפוש. אנא הורד קובץ תחילה.")
            return
        
        try:
            self.update_status("...מחפש")
            
            # Read CSV file
            df = pd.read_csv(self.downloaded_file_path, encoding='utf-8-sig')
            
            # Update date range from file
            self._update_date_range_from_file(df)
            
            # Check required columns exist
            if 'מספר_חשבון_מוגבל' not in df.columns:
                messagebox.showerror("שגיאה", "עמודת מספר חשבון מוגבל לא נמצאה בקובץ")
                return
            
            # Start with all rows (True mask)
            mask = pd.Series([True] * len(df), index=df.index)
            
            # Filter by account number if provided
            if search_term:
                account_mask = df['מספר_חשבון_מוגבל'].astype(str).str.contains(search_term, na=False, case=False)
                mask = mask & account_mask
            
            # Filter by date if provided
            if date_term:
                # Parse date from dd/mm/yyyy format
                try:
                    search_date = datetime.strptime(date_term, '%d/%m/%Y').date()
                    
                    # Check if תאריך_סיום_הגבלה column exists
                    if 'תאריך_סיום_הגבלה' in df.columns:
                        # Convert date column to datetime (format: yyyy-mm-dd)
                        df['תאריך_סיום_הגבלה_parsed'] = pd.to_datetime(
                            df['תאריך_סיום_הגבלה'], 
                            format='%Y-%m-%d',
                            errors='coerce'
                        )
                        
                        # Filter rows where date is greater than or equal to search date
                        date_mask = df['תאריך_סיום_הגבלה_parsed'].dt.date >= search_date
                        mask = mask & date_mask.fillna(False)
                    else:
                        self.log("אזהרה: עמודת תאריך סיום הגבלה לא נמצאה - חיפוש לפי תאריך לא בוצע")
                except ValueError:
                    # Invalid date format, skip date filter
                    self.log(f"אזהרה: תאריך לא תקין '{date_term}' - חיפוש לפי תאריך לא בוצע")
            
            # Apply combined mask
            results_df = df[mask]
            
            # Clear previous results
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Add results to treeview
            for _, row in results_df.iterrows():
                values = (
                    str(row.get('מספר_בנק', '')),
                    str(row.get('מספר_סניף', '')),
                    str(row.get('מספר_חשבון_מוגבל', '')),
                    str(row.get('תאריך_סיום_הגבלה', '')),
                    str(row.get('שם_סניף', ''))
                )
                self.results_tree.insert('', tk.END, values=values)
            
            # Build search description
            search_desc = []
            if search_term:
                search_desc.append(f"חשבון: '{search_term}'")
            if date_term:
                search_desc.append(f"תאריך >= '{date_term}'")
            
            self.update_status(f"נמצאו {len(results_df)} תוצאות")
            self.log(f"חיפוש הושלם: נמצאו {len(results_df)} תוצאות עבור {', '.join(search_desc)}")
            
        except Exception as e:
            error_msg = f"שגיאה בחיפוש: {str(e)}"
            self.log(error_msg)
            self.update_status("שגיאה")
            messagebox.showerror("שגיאה", error_msg)


def main():
    """Main entry point for GUI application."""
    root = ctk.CTk()
    app = RestrictedAccountsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

