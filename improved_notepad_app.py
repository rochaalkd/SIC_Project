### main.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Toplevel, PhotoImage, Label, filedialog
import os
from add_notes import AddNoteWindow

class NotexApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notex - Your Notes, Reimagined")
        self.root.geometry("1200x700")
        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)

        self.style = ttk.Style(theme="flatly")
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

        read_notes_btn = ttk.Button(sidebar, text="📂 Read Notes", command=self.read_notes, **btn_style)
        read_notes_btn.pack(pady=10)
        self.add_hover_colors(read_notes_btn)

        canva_btn = ttk.Button(sidebar, text="🎨 Canva", command=self.open_canva, **btn_style)
        canva_btn.pack(pady=10)
        self.add_hover_colors(canva_btn)

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
        def on_enter(e):
            button.config(bootstyle="primary")
        def on_leave(e):
            button.config(bootstyle="light")
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    def open_add_note_window(self):
        AddNoteWindow(self.root)

    def read_notes(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path and os.path.exists(file_path):
            viewer = Toplevel(self.root)
            viewer.title("Read Note")
            viewer.geometry("700x500")
            text_area = ttk.Text(viewer, wrap="word", font=("Arial", 12))
            text_area.pack(expand=True, fill="both")
            with open(file_path, "r", encoding="utf-8") as file:
                text_area.insert("1.0", file.read())
            text_area.config(state="disabled")

    def open_canva(self):
        messagebox.showinfo("Canva", "Canvas tool coming soon!")

if __name__ == '__main__':
    root = ttk.Window(themename="flatly")
    app = NotexApp(root)
    root.mainloop()