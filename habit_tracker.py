"""
Habit Tracker - Modern GUI Application (CustomTkinter)
Clean, consistent UI using `customtkinter`.

This file provides a single, stable implementation that imports `habit_model` and `storage`,
and provides a `ModernHabitTrackerApp` class with a `main()` entrypoint.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta
from typing import Optional

from habit_model import HabitManager
from storage import HabitStorage


# Appearance Configuration
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
        """Create the main application layout."""
        # Header
        header = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header.pack(side='top', fill='x')
        header.grid_propagate(False)

        title = ctk.CTkLabel(header, text='🎯 Habit Tracker',
                             font=('Segoe UI', 20, 'bold'))
        title.pack(side='left', padx=20)

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

        edit_btn = ctk.CTkButton(action_frame, text='Edit', fg_color='#6B7280',
                                 hover_color='#4B5563', command=self._edit_habit_dialog)
        edit_btn.pack(side='right', padx=6)

        delete_btn = ctk.CTkButton(action_frame, text='Delete', fg_color='#EF4444',
                                   hover_color='#DC2626', command=self._delete_habit)
        delete_btn.pack(side='right', padx=6)

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
        """Create a styled statistic card."""
        card = ctk.CTkFrame(parent, corner_radius=8, fg_color='transparent')
        card.grid(row=0, column=col, padx=6, sticky='nwe')
        ctk.CTkLabel(card, text=title, font=('Segoe UI', 10), text_color='#98A1B3').pack(
            anchor='w', padx=12, pady=(10, 0))
        lbl = ctk.CTkLabel(card, text=value, font=('Segoe UI', 18, 'bold'))
        lbl.pack(anchor='w', padx=12, pady=(6, 12))
        return lbl

    def _refresh_habit_list(self):
        """Refresh the sidebar habit list."""
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
        """Select a habit and update the details panel."""
        self.selected_habit_id = habit_id
        self._refresh_habit_list()
        self._update_details()

    def _update_details(self):
        """Update the details panel with selected habit information."""
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

    def _add_habit_dialog(self):
        """Show dialog to add a new habit."""
        self._show_input_dialog('Add Habit', self._save_new_habit)

    def _edit_habit_dialog(self):
        """Show dialog to edit the selected habit."""
        if not self.selected_habit_id:
            return
        h = self.habit_manager.get_habit(self.selected_habit_id)
        if not h:
            return
        self._show_input_dialog('Edit Habit', self._save_edit_habit,
                                default_name=h.name, default_desc=h.description)

    def _show_input_dialog(self, title, callback, default_name='', default_desc=''):
        """Show a custom input dialog for habit creation/editing."""
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
        """Save a new habit."""
        self.habit_manager.add_habit(name, desc)
        self._save_and_refresh()

    def _save_edit_habit(self, name, desc):
        """Save edits to an existing habit."""
        if not self.selected_habit_id:
            return
        self.habit_manager.update_habit(self.selected_habit_id, name, desc)
        self._save_and_refresh()

    def _delete_habit(self):
        """Delete the selected habit."""
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
        """Toggle completion status for today."""
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
        """Save data and refresh the UI."""
        self.storage.save_data(self.habit_manager.to_dict())
        self._refresh_habit_list()
        self._update_details()

    def _load_data(self):
        """Load habit data from storage."""
        data = self.storage.load_data()
        self.habit_manager.from_dict(data)

    def _on_closing(self):
        """Handle window close event."""
        self.storage.save_data(self.habit_manager.to_dict())
        self.root.destroy()


def main():
    """Main entry point for the application."""
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
