"""
Storage module for handling JSON file operations.
Manages reading from and writing to habits.json.
"""

import json
import os
import shutil
import sys
from typing import Dict, Any
from datetime import datetime


def _resource_path(relative_path: str) -> str:
    """Return absolute path to resource, works for dev and for PyInstaller.

    When bundled by PyInstaller with --onefile the data files are extracted
    to a temporary folder pointed to by sys._MEIPASS. Otherwise return the
    path relative to this source file.
    """
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


class HabitStorage:
    """Handles persistent storage of habit data in JSON format."""
    
    def __init__(self, filename: str = None):
        """
        Initialize storage handler.

        Args:
            filename: Optional path to JSON file. If None, a writable file is
                created under the user's app data folder (e.g. ~/.habit_tracker/habits.json).
        """
        # Determine a safe, writable path for persistent data
        if filename:
            self.filename = os.path.abspath(filename)
        else:
            # Default location in the user's home directory
            home = os.path.expanduser('~')
            app_dir = os.path.join(home, '.habit_tracker')
            os.makedirs(app_dir, exist_ok=True)
            self.filename = os.path.join(app_dir, 'habits.json')
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file if it doesn't exist.

        If a bundled default `habits.json` is available (for example added with
        PyInstaller's --add-data), it will be copied to the user's app data
        location on first run so the user can modify it.
        """
        if not os.path.exists(self.filename):
            # Try to copy the bundled default JSON if present
            try:
                bundled_path = _resource_path('habits.json')
                if os.path.exists(bundled_path):
                    shutil.copy(bundled_path, self.filename)
                    return
            except Exception:
                pass

            # Fall back to creating an empty file
            self.save_data({"habits": [], "metadata": {"created": datetime.now().isoformat()}})
    
    def load_data(self) -> Dict[str, Any]:
        """
        Load habit data from JSON file.
        
        Returns:
            Dictionary containing habit data
        """
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading data: {e}")
            # Return default structure if file is corrupted
            return {"habits": [], "metadata": {"created": datetime.now().isoformat()}}
    
    def save_data(self, data: Dict[str, Any]):
        """
        Save habit data to JSON file.
        
        Args:
            data: Dictionary containing habit data to save
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving data: {e}")
            raise
    
    def backup_data(self):
        """Create a backup of the current data file."""
        if os.path.exists(self.filename):
            backup_filename = f"{self.filename}.backup"
            try:
                data = self.load_data()
                with open(backup_filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"Backup created: {backup_filename}")
            except Exception as e:
                print(f"Error creating backup: {e}")
