"""
Test script to verify Habit Tracker logic.
"""
import os
import unittest
from datetime import date, timedelta
from habit_model import Habit, HabitManager
from storage import HabitStorage

class TestHabitTracker(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_habits.json"
        self.storage = HabitStorage(self.test_file)
        self.manager = HabitManager()

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(f"{self.test_file}.backup"):
            os.remove(f"{self.test_file}.backup")

    def test_streak_calculation(self):
        habit = Habit("Test Habit")
        
        # No completions
        self.assertEqual(habit.get_current_streak(), 0)
        
        # Completed today
        habit.mark_completed(date.today())
        self.assertEqual(habit.get_current_streak(), 1)
        
        # Completed yesterday and today
        yesterday = date.today() - timedelta(days=1)
        habit.mark_completed(yesterday)
        self.assertEqual(habit.get_current_streak(), 2)
        
        # Missed a day (gap)
        three_days_ago = date.today() - timedelta(days=3)
        habit.mark_completed(three_days_ago)
        self.assertEqual(habit.get_current_streak(), 2) # Streak is still 2 (today + yesterday)

    def test_persistence(self):
        # Add habit and save
        habit = self.manager.add_habit("Reading", "Read 10 pages")
        habit.mark_completed()
        
        data = self.manager.to_dict()
        self.storage.save_data(data)
        
        # Load into new manager
        new_manager = HabitManager()
        loaded_data = self.storage.load_data()
        new_manager.from_dict(loaded_data)
        
        loaded_habits = new_manager.get_all_habits()
        self.assertEqual(len(loaded_habits), 1)
        self.assertEqual(loaded_habits[0].name, "Reading")
        self.assertTrue(loaded_habits[0].is_completed_today())

if __name__ == '__main__':
    unittest.main()
