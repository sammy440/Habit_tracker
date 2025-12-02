"""
Habit Tracker - Modern GUI Application (CustomTkinter)
Reimplements the GUI using customtkinter for a modern look.

Requirements: pip install -r requirements.txt
"""

import os
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta
from typing import Optional

from habit_model import HabitManager, Habit
from storage import HabitStorage


ctk.set_appearance_mode('System')  # 'System', 'Dark', 'Light'
ctk.set_default_color_theme('blue')  # 'blue', 'green', 'dark-blue'


class ModernHabitTrackerApp:
    """Modern habit tracker using customtkinter for a contemporary UI."""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title('Habit Tracker')
        self.root.geometry('1000x700')
        self.root.minsize(900, 600)

        # Data managers
        self.storage = HabitStorage()
        self.habit_manager = HabitManager()
        self._load_data()

        # State
        self.selected_habit_id: Optional[str] = None

        # Layout
        self._create_layout()
        self._refresh_habit_list()
        self._update_details()

        # Close handling
        self.root.protocol('WM_DELETE_WINDOW', self._on_closing)

    def _create_layout(self):
        # Header
        header = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header.pack(side='top', fill='x')
        header.grid_propagate(False)

        title = ctk.CTkLabel(header, text='🎯 Habit Tracker',
                             font=('Segoe UI', 20, 'bold'))
        title.pack(side='left', padx=20)

        self.theme_toggle = ctk.CTkSegmentedButton(
            header, values=['Light', 'Dark'], command=self._on_theme_changed)
        self.theme_toggle.set(
            'Light' if ctk.get_appearance_mode() == 'Light' else 'Dark')
        self.theme_toggle.pack(side='right', padx=20)

        # Main container
        main = ctk.CTkFrame(self.root, corner_radius=0)
        main.pack(side='top', fill='both', expand=True, padx=12, pady=12)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(1, weight=1)

        # Sidebar
        sidebar = ctk.CTkFrame(main, width=300)
        sidebar.grid(row=0, column=0, sticky='nswe', padx=(0, 12), pady=4)
        sidebar.grid_propagate(False)

        add_btn = ctk.CTkButton(sidebar, text='+ New Habit', fg_color='#1E90FF',
                                hover_color='#1565C0', corner_radius=8, command=self._add_habit_dialog)
        add_btn.pack(fill='x', padx=12, pady=(12, 8))

        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            sidebar, placeholder_text='Search habits...', textvariable=self.search_var, width=220)
        search_entry.pack(fill='x', padx=12, pady=(0, 12))
        search_entry.bind('<KeyRelease>', lambda e: self._refresh_habit_list())

        self.habit_scroll = ctk.CTkScrollableFrame(
            sidebar, width=260, height=520, corner_radius=6)
        self.habit_scroll.pack(fill='both', expand=True, padx=8)

        # Content
        content = ctk.CTkFrame(main, corner_radius=8)
        content.grid(row=0, column=1, sticky='nswe')
        content.grid_rowconfigure(2, weight=1)

        self.detail_title = ctk.CTkLabel(
            content, text='Select a habit to view details', font=('Segoe UI', 18, 'bold'))
        self.detail_title.grid(
            row=0, column=0, sticky='w', padx=20, pady=(20, 6))

        self.detail_desc = ctk.CTkLabel(content, text='', font=(
            'Segoe UI', 12), text_color='#7C8BA4', wraplength=520)
        self.detail_desc.grid(row=1, column=0, sticky='w', padx=20)

        action_frame = ctk.CTkFrame(content, fg_color='transparent')
        action_frame.grid(row=0, column=1, rowspan=2,
                          sticky='e', padx=20, pady=6)

        self.checkin_btn = ctk.CTkButton(action_frame, text='✓ Check In', fg_color='#10B981',
                                         hover_color='#0F9A60', command=self._toggle_today_completion)
        self.checkin_btn.pack(side='right', padx=6)
        ctk.CTkButton(action_frame, text='Edit', fg_color='transparent',
                      hover_color='#dddddd', command=self._edit_habit_dialog).pack(side='right', padx=6)
        ctk.CTkButton(action_frame, text='Delete', fg_color='#F87171',
                      hover_color='#ef6b6b', command=self._delete_habit).pack(side='right')

        # Stats
        stats_frame = ctk.CTkFrame(content, fg_color='transparent')
        stats_frame.grid(row=2, column=0, columnspan=2,
                         sticky='nwe', padx=20, pady=20)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_streak = self._create_stat_card(
            stats_frame, '🔥 Current Streak', '0', 0)
        self.card_best = self._create_stat_card(
            stats_frame, '🏆 Best Streak', '0', 1)
        self.card_total = self._create_stat_card(
            stats_frame, '✅ Total Check-ins', '0', 2)
        self.card_rate = self._create_stat_card(
            stats_frame, '📊 Consistency', '0%', 3)

        # Recent history
        self.history_frame = ctk.CTkFrame(content, fg_color='transparent')
        self.history_frame.grid(
            row=3, column=0, columnspan=2, sticky='nwe', padx=20, pady=(0, 20))
        self.history_label = ctk.CTkLabel(
            self.history_frame, text='', font=('Consolas', 12))
        self.history_label.pack(fill='x')

    def _create_stat_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color='transparent')
        card.grid(row=0, column=col, padx=6, sticky='nwe')
        ctk.CTkLabel(card, text=title, font=('Segoe UI', 10), text_color='#98A1B3').pack(
            anchor='w', padx=12, pady=(10, 0))
        lbl = ctk.CTkLabel(card, text=value, font=('Segoe UI', 18, 'bold'))
        lbl.pack(anchor='w', padx=12, pady=(6, 12))
        return lbl

    def _refresh_habit_list(self):
        for w in self.habit_scroll.winfo_children():
            w.destroy()

        query = self.search_var.get().strip().lower() if getattr(
            self, 'search_var', None) else ''
        for habit in self.habit_manager.get_all_habits():
            if query and query not in habit.name.lower():
                continue

            item_frame = ctk.CTkFrame(
                self.habit_scroll, corner_radius=8, fg_color='transparent')
            item_frame.pack(fill='x', pady=6, padx=6)

            b = ctk.CTkButton(item_frame, text=f"{habit.name}", anchor='w', fg_color='transparent',
                              hover_color='#2D2F31', command=lambda id=habit.id: self._select_habit(id))
            b.pack(side='left', fill='x', expand=True)

            status = '✅' if habit.is_completed_today() else '⬜'
            ctk.CTkLabel(item_frame, text=f"{status} {habit.get_current_streak()} 🔥", width=80, anchor='e').pack(
                side='right')

            if self.selected_habit_id == habit.id:
                b.configure(fg_color='#374151', hover_color='#2f3a44')

    def _select_habit(self, habit_id: str):
        self.selected_habit_id = habit_id
        self._refresh_habit_list()
        self._update_details()

    def _update_details(self):
        if not self.selected_habit_id:
            self.detail_title.configure(text='Select a habit to view details')
            self.detail_desc.configure(text='')
            self.card_streak.configure(text='0')
            self.card_best.configure(text='0')
            self.card_total.configure(text='0')
            self.card_rate.configure(text='0%')
            self.history_label.configure(text='')
            self.checkin_btn.configure(state='disabled')
            return

        h = self.habit_manager.get_habit(self.selected_habit_id)
        if not h:
            self.selected_habit_id = None
            return

        self.detail_title.configure(text=h.name)
        self.detail_desc.configure(
            text=h.description if h.description else '\u00A0')
        self.card_streak.configure(text=str(h.get_current_streak()))
        self.card_best.configure(text=str(h.get_longest_streak()))
        self.card_total.configure(text=str(h.get_total_completions()))
        self.card_rate.configure(text=f"{h.get_completion_rate():.0f}%")
        self.checkin_btn.configure(state='normal')
        if h.is_completed_today():
            self.checkin_btn.configure(
                text='✕ Undo Check-in', fg_color='#FF7B7B')
        else:
            self.checkin_btn.configure(text='✓ Check In', fg_color='#10B981')

        days = []
        today = date.today()
        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            day_name = d.strftime('%a')
            status = '🟩' if h.is_completed_on_date(d) else '⬜'
            days.append(f"{day_name}: {status}")

        self.history_label.configure(text='   '.join(days))

    # --- CRUD & Actions ---
    def _add_habit_dialog(self):
        self._show_input_dialog('Add Habit', self._save_new_habit)

    def _edit_habit_dialog(self):
        if not self.selected_habit_id:
            return
        h = self.habit_manager.get_habit(self.selected_habit_id)
        if not h:
            return
        self._show_input_dialog('Edit Habit', self._save_edit_habit,
                                default_name=h.name, default_desc=h.description)

    def _show_input_dialog(self, title, callback, default_name='', default_desc=''):
        d = ctk.CTkToplevel(self.root)
        d.geometry('420x260')
        d.title(title)
        d.transient(self.root)
        d.grab_set()

        frame = ctk.CTkFrame(d)
        frame.pack(fill='both', expand=True, padx=16, pady=16)

        ctk.CTkLabel(frame, text='Name').pack(anchor='w')
        name_var = ctk.StringVar(value=default_name)
        name_entry = ctk.CTkEntry(
            frame, textvariable=name_var, placeholder_text='e.g. Read 10 pages')
        name_entry.pack(fill='x', pady=(6, 12))

        ctk.CTkLabel(frame, text='Description').pack(anchor='w')
        desc_var = ctk.StringVar(value=default_desc)
        desc_entry = ctk.CTkEntry(
            frame, textvariable=desc_var, placeholder_text='Optional short description')
        desc_entry.pack(fill='x', pady=(6, 12))

        def on_save(event=None):
            if name_var.get().strip():
                callback(name_var.get(), desc_var.get())
                d.destroy()
                return
            messagebox.showwarning('Validation', 'Name cannot be empty')

        name_entry.focus()
        d.bind('<Return>', on_save)

        button_row = ctk.CTkFrame(frame, fg_color='transparent')
        button_row.pack(fill='x', pady=(6, 0))
        ctk.CTkButton(button_row, text='Cancel', command=d.destroy,
                      fg_color='transparent').pack(side='right', padx=6)
        ctk.CTkButton(button_row, text='Save', command=on_save,
                      fg_color='#1E90FF').pack(side='right')

    def _save_new_habit(self, name, desc):
        self.habit_manager.add_habit(name, desc)
        self._save_and_refresh()

    def _save_edit_habit(self, name, desc):
        if not self.selected_habit_id:
            return
        self.habit_manager.update_habit(self.selected_habit_id, name, desc)
        self._save_and_refresh()

    def _delete_habit(self):
        if not self.selected_habit_id:
            return
        h = self.habit_manager.get_habit(self.selected_habit_id)
        if not h:
            return
        if messagebox.askyesno('Delete', f"Delete '{h.name}'?"):
            self.habit_manager.remove_habit(h.id)
            self.selected_habit_id = None
            self._save_and_refresh()

    def _toggle_today_completion(self):
        if not self.selected_habit_id:
            return
        h = self.habit_manager.get_habit(self.selected_habit_id)
        if not h:
            return
        if h.is_completed_today():
            h.unmark_completed()
        else:
            h.mark_completed()
        self._save_and_refresh()

    def _save_and_refresh(self):
        self.storage.save_data(self.habit_manager.to_dict())
        self._refresh_habit_list()
        self._update_details()

    def _load_data(self):
        data = self.storage.load_data()
        self.habit_manager.from_dict(data)

    def _on_closing(self):
        self.storage.save_data(self.habit_manager.to_dict())
        self.root.destroy()

    def _on_theme_changed(self, choice):
        if choice.lower().startswith('dark'):
            ctk.set_appearance_mode('Dark')
        else:
            ctk.set_appearance_mode('Light')


def main():
    root = ctk.CTk()
    # Attempt to improve DPI awareness on Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = ModernHabitTrackerApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
"""
Habit Tracker - Modern GUI Application (CustomTkinter)
Reimplements the GUI using customtkinter for a modern look.

Requirements: pip install customtkinter
"""




# -- Appearance Configuration --
ctk.set_appearance_mode('System')  # 'System', 'Dark', 'Light'
ctk.set_default_color_theme('blue')  # 'blue', 'green', 'dark-blue'


class ModernHabitTrackerApp:
    """Modern habit tracker using customtkinter for a contemporary UI."""

    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title('Habit Tracker')
        self.root.geometry('1000x700')
        self.root.minsize(900, 600)

        # Data managers
        self.storage = HabitStorage()
        if __name__ == '__main__':
            main()
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
