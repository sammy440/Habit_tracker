"""
Storage module for handling JSON file operations.
Manages reading from and writing to habits.json.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime


class HabitStorage:
    """Handles persistent storage of habit data in JSON format."""
    
    def __init__(self, filename: str = "habits.json"):
        """
        Initialize storage handler.
        
        Args:
            filename: Name of the JSON file for storing habits
        """
        self.filename = filename
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self.filename):
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
