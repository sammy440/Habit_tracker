"""
Habit model and business logic.
Handles habit creation, tracking, and statistics calculation.
"""

from datetime import datetime, date
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import uuid


@dataclass
class Habit:
    """Represents a single habit with tracking data."""
    
    name: str
    description: str = ""
    created_date: str = field(default_factory=lambda: date.today().isoformat())
    completion_dates: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def mark_completed(self, completion_date: Optional[date] = None):
        """
        Mark habit as completed for a specific date.
        
        Args:
            completion_date: Date to mark as completed (defaults to today)
        """
        if completion_date is None:
            completion_date = date.today()
        
        date_str = completion_date.isoformat()
        if date_str not in self.completion_dates:
            self.completion_dates.append(date_str)
            self.completion_dates.sort()
    
    def unmark_completed(self, completion_date: Optional[date] = None):
        """
        Remove completion mark for a specific date.
        
        Args:
            completion_date: Date to unmark (defaults to today)
        """
        if completion_date is None:
            completion_date = date.today()
        
        date_str = completion_date.isoformat()
        if date_str in self.completion_dates:
            self.completion_dates.remove(date_str)
    
    def is_completed_today(self) -> bool:
        """Check if habit is completed for today."""
        return date.today().isoformat() in self.completion_dates
    
    def is_completed_on_date(self, check_date: date) -> bool:
        """
        Check if habit was completed on a specific date.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if completed on that date
        """
        return check_date.isoformat() in self.completion_dates
    
    def get_current_streak(self) -> int:
        """
        Calculate current streak of consecutive completions.
        
        Returns:
            Number of consecutive days (including today if completed)
        """
        if not self.completion_dates:
            return 0
        
        streak = 0
        current_date = date.today()
        
        # Check if today is completed or if yesterday was (to allow for current streak)
        if not self.is_completed_on_date(current_date):
            # If not completed today, check yesterday
            from datetime import timedelta
            yesterday = current_date - timedelta(days=1)
            if not self.is_completed_on_date(yesterday):
                return 0
            streak = 1
            current_date = yesterday
        else:
            streak = 1
        
        # Count backwards from current date
        from datetime import timedelta
        while True:
            current_date = current_date - timedelta(days=1)
            if self.is_completed_on_date(current_date):
                streak += 1
            else:
                break
        
        return streak
    
    def get_longest_streak(self) -> int:
        """
        Calculate the longest streak ever achieved.
        
        Returns:
            Maximum number of consecutive days
        """
        if not self.completion_dates:
            return 0
        
        max_streak = 1
        current_streak = 1
        
        sorted_dates = sorted([date.fromisoformat(d) for d in self.completion_dates])
        
        for i in range(1, len(sorted_dates)):
            from datetime import timedelta
            if sorted_dates[i] - sorted_dates[i-1] == timedelta(days=1):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        return max_streak
    
    def get_total_completions(self) -> int:
        """Get total number of completions."""
        return len(self.completion_dates)
    
    def get_completion_rate(self) -> float:
        """
        Calculate completion rate since habit creation.
        
        Returns:
            Percentage of days completed (0-100)
        """
        created = date.fromisoformat(self.created_date)
        days_since_creation = (date.today() - created).days + 1
        
        if days_since_creation == 0:
            return 0.0
        
        return (self.get_total_completions() / days_since_creation) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert habit to dictionary for JSON serialization."""
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Habit':
        """
        Create Habit instance from dictionary.
        
        Args:
            data: Dictionary with habit data
            
        Returns:
            Habit instance
        """
        return Habit(**data)


class HabitManager:
    """Manages collection of habits and provides operations."""
    
    def __init__(self):
        """Initialize habit manager."""
        self.habits: List[Habit] = []
    
    def add_habit(self, name: str, description: str = "") -> Habit:
        """
        Create and add a new habit.
        
        Args:
            name: Habit name
            description: Optional description
            
        Returns:
            Created Habit instance
        """
        habit = Habit(name=name, description=description)
        self.habits.append(habit)
        return habit
    
    def remove_habit(self, habit_id: str) -> bool:
        """
        Remove a habit by ID.
        
        Args:
            habit_id: ID of habit to remove
            
        Returns:
            True if removed successfully
        """
        for i, habit in enumerate(self.habits):
            if habit.id == habit_id:
                self.habits.pop(i)
                return True
        return False
    
    def get_habit(self, habit_id: str) -> Optional[Habit]:
        """
        Get habit by ID.
        
        Args:
            habit_id: ID of habit to find
            
        Returns:
            Habit instance or None
        """
        for habit in self.habits:
            if habit.id == habit_id:
                return habit
        return None
    
    def update_habit(self, habit_id: str, name: Optional[str] = None, 
                    description: Optional[str] = None) -> bool:
        """
        Update habit details.
        
        Args:
            habit_id: ID of habit to update
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            True if updated successfully
        """
        habit = self.get_habit(habit_id)
        if habit:
            if name is not None:
                habit.name = name
            if description is not None:
                habit.description = description
            return True
        return False
    
    def get_all_habits(self) -> List[Habit]:
        """Get all habits."""
        return self.habits
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all habits to dictionary for JSON serialization."""
        return {
            "habits": [habit.to_dict() for habit in self.habits],
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_habits": len(self.habits)
            }
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """
        Load habits from dictionary.
        
        Args:
            data: Dictionary with habits data
        """
        self.habits = []
        if "habits" in data:
            for habit_data in data["habits"]:
                self.habits.append(Habit.from_dict(habit_data))
