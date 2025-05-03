
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel, PhotoImage, Label, filedialog
import os
from add_notes import AddNoteWindow
from read_notes import ReadSavedNotesWindow
from enhanced_data_plotting_1 import DataVisualizationApp
from canva_creation import DrawingApp

class NotexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notex - Your Engineering Notes")
        self.root.geometry("1200x700")
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)
        
        self.current_theme = "dark"
        self.style = ttk.Style(theme="superhero")
        self.open_windows = []
        self.root.app = self  # Allow access to NotexApp instance

        self.build_interface()

    def build_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=BOTH, expand=True)

        sidebar = ttk.Frame(main_frame, width=250, padding=20, bootstyle="primary")
        sidebar.pack(side=LEFT, fill=Y)

        app_label = ttk.Label(sidebar, text="Notex", font=("Helvetica", 28, "bold"), bootstyle="inverse-primary")
        app_label.pack(pady=(10, 40))

        btn_style = {"bootstyle": "light", "width": 20, "padding": 10}

        add_note_btn = ttk.Button(sidebar, text="📝 Add Note", command=self.open_add_note_window, **btn_style)
        add_note_btn.pack(pady=10)
        self.add_hover_colors(add_note_btn)

        read_notes_btn = ttk.Button(sidebar, text="📂 Read Notes", command=self.open_read_saved_notes_window, **btn_style)
        read_notes_btn.pack(pady=10)
        self.add_hover_colors(read_notes_btn)

        canva_btn = ttk.Button(sidebar, text="🎨 Canvas", command=self.open_canva, **btn_style)
        canva_btn.pack(pady=10)
        self.add_hover_colors(canva_btn)

        graphing_btn = ttk.Button(sidebar, text="📈 Graphing Unit", command=self.open_graphing_unit, **btn_style)
        graphing_btn.pack(pady=10)
        self.add_hover_colors(graphing_btn)

        theme_frame = ttk.Frame(sidebar)
        theme_frame.pack(pady=(20, 10))
        theme_label = ttk.Label(theme_frame, text="Select Theme:", font=("Helvetica", 10))
        theme_label.pack(side="left", padx=(0, 5))
        theme_options = ["Dark Theme", "White Theme"]
        self.theme_var = ttk.StringVar(value="Dark Theme")
        theme_dropdown = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=theme_options, state="readonly", width=15)
        theme_dropdown.pack(side="left")
        theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(side=LEFT, fill=BOTH, expand=True)

        try:
            self.bg_image = PhotoImage(file="notex_home_boy_board.png")
            bg_label = Label(content_frame, image=self.bg_image)
            bg_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
        except:
            fallback = ttk.Label(content_frame, text="Welcome to Notex", font=("Helvetica", 22), bootstyle="info")
            fallback.pack(expand=True)

    def add_hover_colors(self, button):
        def on_enter(e): button.config(bootstyle="primary")
        def on_leave(e): button.config(bootstyle="light")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def close_all_windows(self):
        for window_type, window, text_widget in self.open_windows[:]:
            try:
                if window_type == "read_notes":
                    for note_window, note_text_widget in window.note_windows[:]:
                        if note_window.winfo_exists():
                            note_window.destroy()
                    window.note_windows.clear()
                    if window.winfo_exists():
                        window.window.destroy()
                elif window_type == "add_note" and window.winfo_exists():
                    window.editor.destroy()
                elif window_type == "graphing" and window.master.winfo_exists():
                    window.master.destroy()
            except:
                pass
        self.open_windows.clear()

    def change_theme(self, event=None):
        selected_theme = self.theme_var.get()
        if selected_theme == "Dark Theme":
            self.current_theme = "dark"
            self.style.theme_use("superhero")
        else:
            self.current_theme = "white"
            self.style.theme_use("flatly")

        for window_type, window, text_widget in self.open_windows:
            if window.winfo_exists():
                if window_type == "read_notes":
                    window.current_theme = self.current_theme
                    window.style = self.style
                    for note_window, note_text_widget in window.note_windows:
                        if note_window.winfo_exists():
                            bg_color = "#2a2a2a" if self.current_theme == "dark" else "#ffffff"
                            fg_color = "#d4d4d4" if self.current_theme == "dark" else "#000000"
                            note_text_widget.config(background=bg_color, foreground=fg_color)
                elif window_type in ["add_note", "graphing"]:
                    window.style = self.style

    def open_add_note_window(self):
        self.close_all_windows()
        add_note_window = AddNoteWindow(self.root)
        self.open_windows.append(("add_note", add_note_window, None))

    def open_add_note_with_content(self, heading, content):
        self.close_all_windows()
        add_note_window = AddNoteWindow(self.root, heading=heading, content=content)
        self.open_windows.append(("add_note", add_note_window, None))

    def open_read_saved_notes_window(self):
        self.close_all_windows()
        read_notes_window = ReadSavedNotesWindow(self.root, self.current_theme, self.style)
        self.open_windows.append(("read_notes", read_notes_window, None))

    def open_canva(self):
        self.close_all_windows()
        plot_window = ttk.Toplevel(self.root)
        plot_window.title("Canva App")
        plot_window.geometry("1100x750")
        plot_window.transient(self.root)
        plot_window.grab_set()
        graphing_app = DrawingApp(plot_window)
        self.open_windows.append(("graphing", graphing_app, None))
        plot_window.focus_force()

    def open_graphing_unit(self):
        self.close_all_windows()
        plot_window = ttk.Toplevel(self.root)
        plot_window.title("Data Visualization")
        plot_window.geometry("1100x750")
        plot_window.transient(self.root)
        plot_window.grab_set()
        graphing_app = DataVisualizationApp(plot_window)
        self.open_windows.append(("graphing", graphing_app, None))
        plot_window.focus_force()

if __name__ == '__main__':
    root = ttk.Window(themename="superhero")
    app = NotexApp(root)
    root.mainloop()