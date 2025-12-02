@echo off
REM Build Windows single-file executable using PyInstaller
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller




pauseecho Build complete. The exe can be found in the dist\ folder.pyinstaller --onefile --noconsole --add-data "habits.json;." --name HabitTracker habit_tracker.pynREM Add habits.json to bundle; using windows `;` separator for add-data