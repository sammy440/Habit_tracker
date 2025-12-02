# 🎯 Habit Tracker - Desktop Application

A beautiful and functional desktop application for tracking your daily habits, built with Python and Tkinter.

![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- **📝 Habit Management**: Add, edit, and delete habits with names and descriptions
- **✅ Daily Tracking**: Mark habits as completed for each day with a single click
- **🔥 Streak Tracking**: Automatic calculation of current and longest streaks
- **📊 Statistics Dashboard**: View total completions, completion rates, and trends
- **📅 Recent Activity**: Visual 7-day activity overview for each habit
- **💾 Persistent Storage**: All data saved locally in JSON format
- **🎨 Clean Interface**: Intuitive, user-friendly GUI built with Tkinter

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- No additional dependencies required (uses Python standard library)

### Installation

1. **Clone or download** this repository to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd "c:\Users\USER\Desktop\Habit Tracker"
   ```

3. **Run the application**:
   ```bash
   python habit_tracker.py
   ```

That's it! The application will start and automatically create a `habits.json` file for data storage.

## 📖 Usage Guide

### Adding a New Habit

1. Click the **"+ Add Habit"** button in the top-left
2. Enter the habit name (required) and optional description
3. Click **"Add Habit"** to save

### Tracking Daily Progress

1. Select a habit from the list on the left
2. Click **"✓ Complete Today"** to mark it as done
3. The streak counter updates automatically!

### Viewing Statistics

When you select a habit, the right panel shows:
- 🔥 **Current Streak**: How many consecutive days you've maintained the habit
- 🏆 **Longest Streak**: Your best streak ever
- ✅ **Total Completions**: Total number of times you've completed this habit
- 📊 **Completion Rate**: Percentage of days completed since creation
- 📅 **Recent Activity**: Visual 7-day completion history

### Editing a Habit

1. Select the habit you want to edit
2. Click **"Edit"**
3. Modify the name or description
4. Click **"Save Changes"**

### Deleting a Habit

1. Select the habit you want to delete
2. Click **"Delete"**
3. Confirm the deletion (this cannot be undone!)

## 📁 Project Structure

```
Habit Tracker/
├── habit_tracker.py          # Main GUI application
├── habit_model.py            # Business logic and data models
├── storage.py                # JSON file handling
├── habits.json               # Data storage (auto-created)
├── habits.json.backup        # Backup file (auto-created)
└── README.md                 # This file
```

## 🔧 Technical Details

### Data Storage

All habit data is stored in `habits.json` with the following structure:

```json
{
  "habits": [
    {
      "name": "Exercise",
      "description": "30 minutes of exercise",
      "created_date": "2025-12-01",
      "completion_dates": ["2025-12-01", "2025-12-02"],
      "id": "unique-id-here"
    }
  ],
  "metadata": {
    "last_updated": "2025-12-01T19:00:00",
    "total_habits": 1
  }
}
```

### Architecture

The application follows a modular design pattern:

- **`habit_tracker.py`**: GUI layer using Tkinter
- **`habit_model.py`**: Business logic (Habit and HabitManager classes)
- **`storage.py`**: Data persistence layer

This separation makes the code maintainable and allows for future enhancements.

## 🎨 Customization

### Changing the Theme

Edit the `_setup_styles()` method in `habit_tracker.py` to customize colors and fonts:

```python
def _setup_styles(self):
    style = ttk.Style()
    style.theme_use('clam')  # Try 'default', 'alt', 'clam', 'classic'
    # Customize your styles here
```

### Adding New Statistics

To add new statistics:
1. Add calculation method to the `Habit` class in `habit_model.py`
2. Create a new stat card in `_create_details_panel()` in `habit_tracker.py`
3. Update the display in `_update_details_panel()`

## 🐛 Troubleshooting

### Application won't start
- Ensure Python 3.10+ is installed: `python --version`
- Check that all files are in the same directory

### Data not saving
- Check file permissions in the application directory
- Look for error messages in the console
- Restore from `habits.json.backup` if needed

### UI looks different
- The appearance depends on your operating system's theme
- Try changing the theme in `_setup_styles()` method

## 🔮 Future Enhancements

Potential features to add:
- 📈 Monthly/yearly statistics and charts
- 🎯 Goal setting with target streaks
- 📧 Email or desktop notifications
- 🌙 Dark mode support
- 📤 Export data to CSV
- ☁️ Cloud sync capabilities
- 📱 Mobile companion app

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 💡 Tips for Success

1. **Start Small**: Begin with 2-3 habits you really want to build
2. **Be Consistent**: Try to check the app every day, even if just for a minute
3. **Celebrate Streaks**: Reward yourself when you hit streak milestones!
4. **Don't Break the Chain**: Once you start a streak, keep it going!
5. **Review Weekly**: Check your statistics every week to stay motivated

---

**Happy Habit Building! 🚀**

*Built with ❤️ using Python and Tkinter*
