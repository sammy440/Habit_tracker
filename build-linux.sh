#!/usr/bin/env bash
# Build Linux single-file executable using PyInstaller
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
pip3 install pyinstaller

# Add habits.json to bundle; use ':' separator for add-data on Linux/macOS
pyinstaller --onefile --noconsole --add-data "habits.json:./" --name HabitTracker habit_tracker.py

echo "Build complete. The executable can be found in the dist/ folder."