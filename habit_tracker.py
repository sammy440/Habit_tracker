"""
Habit Tracker - Main GUI Application
A desktop application for tracking daily habits with statistics and streak tracking.
Features a modern UI with Dark/Light mode support.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from typing import Optional, Dict

from habit_model import HabitManager, Habit
from storage import HabitStorage

# --- Theme Configuration ---
THEMES = {
    "light": {
        "bg": "#F3F4F6",           # Main window background
        "surface": "#FFFFFF",       # Card/Panel background
        "fg": "#1F2937",           # Main text
        "fg_secondary": "#6B7280", # Subtitle/Info text
        "primary": "#4F46E5",      # Primary button/accent
        "primary_fg": "#FFFFFF",
        "success": "#10B981",      # Success/Complete
        "danger": "#EF4444",       # Delete/Danger
        "select_bg": "#E0E7FF",    # Selection background
        "select_fg": "#1F2937",    # Selection text
        "border": "#E5E7EB",       # Borders
        "tree_bg": "#FFFFFF",
        "tree_fg": "#374151",
    },
    "dark": {
        "bg": "#111827",
        "surface": "#1F2937",
        "fg": "#F9FAFB",
        "fg_secondary": "#9CA3AF",
        "primary": "#6366F1",
        "primary_fg": "#FFFFFF",
        "success": "#34D399",
        "danger": "#F87171",
        "select_bg": "#374151",
        "select_fg": "#F9FAFB",
        "border": "#374151",
        "tree_bg": "#1F2937",
        "tree_fg": "#D1D5DB",
    }
}

class HabitTrackerApp:
    """Main application class for the Habit Tracker GUI."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Habit Tracker")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Initialize managers
        self.storage = HabitStorage()
        self.habit_manager = HabitManager()
        self._load_data()
        
        # State
        self.selected_habit: Optional[Habit] = None
        self.current_theme = "light"
        
        # Configure Grid Layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main Container
        self.main_container = ttk.Frame(self.root)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.columnconfigure(1, weight=1) # Right panel expands
        self.main_container.rowconfigure(1, weight=1)    # Content area expands
        
        # Setup UI
        self._setup_initial_styles()
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        
        # Apply initial theme
        self._apply_theme(self.current_theme)
        self._refresh_habit_list()
        
        # Save on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_initial_styles(self):
        """Configure base font styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Fonts
        self.fonts = {
            'h1': ('Segoe UI', 24, 'bold'),
            'h2': ('Segoe UI', 16, 'bold'),
            'h3': ('Segoe UI', 12, 'bold'),
            'body': ('Segoe UI', 10),
            'small': ('Segoe UI', 9),
            'stat_val': ('Segoe UI', 20, 'bold'),
        }

    def _apply_theme(self, theme_name: str):
        """Apply colors and styles based on the selected theme."""
        colors = THEMES[theme_name]
        style = ttk.Style()
        
        # Root background
        self.root.configure(bg=colors["bg"])
        self.main_container.configure(style='Main.TFrame')
        
        # Frame Styles
        style.configure('Main.TFrame', background=colors["bg"])
        style.configure('Surface.TFrame', background=colors["surface"], relief='flat')
        style.configure('Sidebar.TFrame', background=colors["surface"])
        style.configure('Card.TFrame', background=colors["surface"], relief='groove', borderwidth=1)
        
        # Label Styles
        style.configure('TLabel', background=colors["surface"], foreground=colors["fg"], font=self.fonts['body'])
        style.configure('Header.TLabel', background=colors["surface"], foreground=colors["fg"], font=self.fonts['h1'])
        style.configure('SubHeader.TLabel', background=colors["surface"], foreground=colors["fg"], font=self.fonts['h2'])
        style.configure('CardTitle.TLabel', background=colors["surface"], foreground=colors["fg_secondary"], font=self.fonts['small'])
        style.configure('CardValue.TLabel', background=colors["surface"], foreground=colors["primary"], font=self.fonts['stat_val'])
        style.configure('Info.TLabel', background=colors["surface"], foreground=colors["fg_secondary"], font=self.fonts['small'])
        
        # Button Styles
        style.configure('TButton', font=self.fonts['body'], padding=6, borderwidth=0)
        style.map('TButton',
            background=[('active', colors["select_bg"]), ('!active', colors["surface"])],
            foreground=[('active', colors["primary"]), ('!active', colors["fg"])]
        )
        
        # Primary Button (Add, Save)
        style.configure('Primary.TButton', background=colors["primary"], foreground=colors["primary_fg"])
        style.map('Primary.TButton',
            background=[('active', colors["primary"]), ('!active', colors["primary"])], # Keep consistent
            foreground=[('active', colors["primary_fg"]), ('!active', colors["primary_fg"])]
        )
        
        # Success Button (Complete)
        style.configure('Success.TButton', background=colors["success"], foreground="#FFFFFF")
        style.map('Success.TButton', background=[('active', colors["success"])])
        
        # Danger Button (Delete)
        style.configure('Danger.TButton', background=colors["danger"], foreground="#FFFFFF")
        style.map('Danger.TButton', background=[('active', colors["danger"])])

        # Treeview (List)
        style.configure('Treeview', 
            background=colors["tree_bg"],
            foreground=colors["tree_fg"],
            fieldbackground=colors["tree_bg"],
            font=self.fonts['body'],
            rowheight=35,
            borderwidth=0
        )
        style.configure('Treeview.Heading', 
            background=colors["bg"], 
            foreground=colors["fg"], 
            font=self.fonts['h3'],
            relief='flat'
        )
        style.map('Treeview', 
            background=[('selected', colors["select_bg"])], 
            foreground=[('selected', colors["select_fg"])]
        )
        
        # Update specific widget backgrounds that might not catch the style
        for widget in [self.header_frame, self.sidebar_frame, self.content_frame]:
            widget.configure(style='Surface.TFrame')
            
        # Force update of the root background
        self.root.configure(bg=colors["bg"])

    def _toggle_theme(self):
        """Switch between light and dark modes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme(self.current_theme)
        # Update button text/icon
        icon = "🌙" if self.current_theme == "light" else "☀️"
        self.theme_btn.configure(text=icon)

    def _create_header(self):
        """Create the top header bar."""
        self.header_frame = ttk.Frame(self.main_container, padding="20 10")
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.columnconfigure(1, weight=1)
        
        # Logo/Title
        title = ttk.Label(self.header_frame, text="🎯 Habit Tracker", style='Header.TLabel')
        title.grid(row=0, column=0, sticky="w")
        
        # Theme Toggle
        self.theme_btn = ttk.Button(self.header_frame, text="🌙", width=3, command=self._toggle_theme)
        self.theme_btn.grid(row=0, column=2, padx=10)

    def _create_sidebar(self):
        """Create the left sidebar for habit list."""
        self.sidebar_frame = ttk.Frame(self.main_container, padding="20", style='Sidebar.TFrame')
        self.sidebar_frame.grid(row=1, column=0, sticky="ns", padx=(0, 2))
        self.sidebar_frame.rowconfigure(2, weight=1)
        
        # Add Button
        add_btn = ttk.Button(self.sidebar_frame, text="+ New Habit", style='Primary.TButton', 
                            command=self._add_habit_dialog, width=20)
        add_btn.grid(row=0, column=0, pady=(0, 20), sticky="ew")
        
        # Label
        ttk.Label(self.sidebar_frame, text="YOUR HABITS", style='Info.TLabel').grid(row=1, column=0, sticky="w", pady=(0, 10))
        
        # Treeview
        self.habit_tree = ttk.Treeview(self.sidebar_frame, columns=('Streak'), show='tree', selectmode='browse')
        self.habit_tree.grid(row=2, column=0, sticky="nsew")
        
        # Customizing tree column
        self.habit_tree.column('#0', width=220)
        self.habit_tree.column('Streak', width=50, anchor="e")
        
        # Scrollbar
        sb = ttk.Scrollbar(self.sidebar_frame, orient="vertical", command=self.habit_tree.yview)
        sb.grid(row=2, column=1, sticky="ns")
        self.habit_tree.configure(yscrollcommand=sb.set)
        
        self.habit_tree.bind('<<TreeviewSelect>>', self._on_habit_select)

    def _create_main_content(self):
        """Create the right main content area."""
        self.content_frame = ttk.Frame(self.main_container, padding="30", style='Main.TFrame')
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        
        # Placeholder when no habit selected
        self.placeholder_label = ttk.Label(self.content_frame, text="Select a habit to view details", 
                                          font=self.fonts['h2'], foreground="#9CA3AF")
        self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Detail Container (Hidden initially)
        self.detail_container = ttk.Frame(self.content_frame, style='Main.TFrame')
        
        # Header Section
        self.detail_header = ttk.Frame(self.detail_container, style='Main.TFrame')
        self.detail_header.pack(fill="x", pady=(0, 30))
        
        self.habit_title = ttk.Label(self.detail_header, text="", style='SubHeader.TLabel')
        self.habit_title.pack(side="left")
        
        self.habit_desc = ttk.Label(self.detail_header, text="", style='Info.TLabel')
        self.habit_desc.pack(side="left", padx=15, pady=4)
        
        # Action Buttons
        btn_frame = ttk.Frame(self.detail_header, style='Main.TFrame')
        btn_frame.pack(side="right")
        
        self.complete_btn = ttk.Button(btn_frame, text="✓ Check In", style='Success.TButton', command=self._toggle_today_completion)
        self.complete_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Edit", command=self._edit_habit_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete", style='Danger.TButton', command=self._delete_habit).pack(side="left", padx=5)

        # Stats Grid
        self.stats_grid = ttk.Frame(self.detail_container, style='Main.TFrame')
        self.stats_grid.pack(fill="x", pady=(0, 30))
        self.stats_grid.columnconfigure((0,1,2,3), weight=1)
        
        # Stat Cards
        self.lbl_streak = self._create_stat_card(self.stats_grid, "🔥 Current Streak", 0, 0)
        self.lbl_best = self._create_stat_card(self.stats_grid, "🏆 Best Streak", 0, 1)
        self.lbl_total = self._create_stat_card(self.stats_grid, "✅ Total Check-ins", 0, 2)
        self.lbl_rate = self._create_stat_card(self.stats_grid, "📊 Consistency", 0, 3)
        
        # Activity History
        history_frame = ttk.LabelFrame(self.detail_container, text="  Recent History  ", padding="20", style='Card.TFrame')
        history_frame.pack(fill="x", expand=True)
        
        self.history_label = ttk.Label(history_frame, text="", font=('Consolas', 12)) # Monospace for alignment
        self.history_label.pack(anchor="center")

    def _create_stat_card(self, parent, title, row, col):
        """Create a styled statistic card."""
        card = ttk.Frame(parent, padding="15", style='Card.TFrame')
        card.grid(row=row, column=col, padx=10, sticky="ew")
        
        ttk.Label(card, text=title, style='CardTitle.TLabel').pack(anchor="w")
        value_lbl = ttk.Label(card, text="0", style='CardValue.TLabel')
        value_lbl.pack(anchor="w", pady=(5, 0))
        return value_lbl

    def _refresh_habit_list(self):
        """Refresh the sidebar list."""
        for item in self.habit_tree.get_children():
            self.habit_tree.delete(item)
            
        for habit in self.habit_manager.get_all_habits():
            # Add icon based on status
            status_icon = "✅" if habit.is_completed_today() else "⬜"
            display_text = f" {status_icon}  {habit.name}"
            streak_text = f"{habit.get_current_streak()} 🔥" if habit.get_current_streak() > 0 else ""
            
            self.habit_tree.insert('', 'end', iid=habit.id, text=display_text, values=(streak_text,))

    def _on_habit_select(self, event):
        """Handle selection."""
        selection = self.habit_tree.selection()
        if not selection:
            return
            
        habit_id = selection[0]
        self.selected_habit = self.habit_manager.get_habit(habit_id)
        
        # Show details, hide placeholder
        self.placeholder_label.place_forget()
        self.detail_container.pack(fill="both", expand=True)
        
        self._update_details()

    def _update_details(self):
        """Update the detail view with selected habit data."""
        if not self.selected_habit:
            return
            
        h = self.selected_habit
        
        # Header
        self.habit_title.configure(text=h.name)
        self.habit_desc.configure(text=h.description)
        
        # Button State
        if h.is_completed_today():
            self.complete_btn.configure(text="✕ Undo Check-in", style='Danger.TButton')
        else:
            self.complete_btn.configure(text="✓ Check In Today", style='Success.TButton')
            
        # Stats
        self.lbl_streak.configure(text=str(h.get_current_streak()))
        self.lbl_best.configure(text=str(h.get_longest_streak()))
        self.lbl_total.configure(text=str(h.get_total_completions()))
        self.lbl_rate.configure(text=f"{h.get_completion_rate():.0f}%")
        
        # History Visualization
        days = []
        today = date.today()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_name = d.strftime("%a")
            status = "🟩" if h.is_completed_on_date(d) else "⬜"
            days.append(f"{day_name}\n{status}")
            
        self.history_label.configure(text="   ".join(days))

    # --- Dialogs & Actions (Logic mostly same, just styling updates) ---
    
    def _add_habit_dialog(self):
        self._show_input_dialog("New Habit", self._save_new_habit)

    def _edit_habit_dialog(self):
        if self.selected_habit:
            self._show_input_dialog("Edit Habit", self._save_edit_habit, 
                                  self.selected_habit.name, self.selected_habit.description)

    def _show_input_dialog(self, title, callback, default_name="", default_desc=""):
        """Custom styled dialog."""
        d = tk.Toplevel(self.root)
        d.title(title)
        d.geometry("400x250")
        d.configure(bg=THEMES[self.current_theme]["bg"])
        
        # Center
        x = self.root.winfo_x() + (self.root.winfo_width()//2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height()//2) - 125
        d.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(d, padding=20, style='Main.TFrame')
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Name", style='TLabel').pack(anchor="w")
        name_var = tk.StringVar(value=default_name)
        ttk.Entry(frame, textvariable=name_var, width=40).pack(pady=(5, 15))
        
        ttk.Label(frame, text="Description", style='TLabel').pack(anchor="w")
        desc_var = tk.StringVar(value=default_desc)
        ttk.Entry(frame, textvariable=desc_var, width=40).pack(pady=(5, 20))
        
        def on_save():
            if name_var.get().strip():
                callback(name_var.get(), desc_var.get())
                d.destroy()
            else:
                messagebox.showwarning("Required", "Name cannot be empty")
                
        ttk.Button(frame, text="Save", style='Primary.TButton', command=on_save).pack(fill="x")

    def _save_new_habit(self, name, desc):
        self.habit_manager.add_habit(name, desc)
        self._save_and_refresh()

    def _save_edit_habit(self, name, desc):
        if self.selected_habit:
            self.habit_manager.update_habit(self.selected_habit.id, name, desc)
            self._save_and_refresh()
            self._update_details()

    def _delete_habit(self):
        if not self.selected_habit: return
        if messagebox.askyesno("Delete", f"Delete '{self.selected_habit.name}'?"):
            self.habit_manager.remove_habit(self.selected_habit.id)
            self.selected_habit = None
            self.detail_container.pack_forget()
            self.placeholder_label.place(relx=0.5, rely=0.5, anchor="center")
            self._save_and_refresh()

    def _toggle_today_completion(self):
        if not self.selected_habit: return
        
        if self.selected_habit.is_completed_today():
            self.selected_habit.unmark_completed()
        else:
            self.selected_habit.mark_completed()
            
        self._save_and_refresh()
        self._update_details()

    def _save_and_refresh(self):
        data = self.habit_manager.to_dict()
        self.storage.save_data(data)
        self._refresh_habit_list()
        # Reselect if exists
        if self.selected_habit:
            # Check if still exists (wasn't deleted)
            if self.habit_manager.get_habit(self.selected_habit.id):
                self.habit_tree.selection_set(self.selected_habit.id)

    def _load_data(self):
        data = self.storage.load_data()
        self.habit_manager.from_dict(data)

    def _on_closing(self):
        data = self.habit_manager.to_dict()
        self.storage.save_data(data)
        self.root.destroy()

def main():
    root = tk.Tk()
    # Attempt to improve DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass
        
    app = HabitTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
