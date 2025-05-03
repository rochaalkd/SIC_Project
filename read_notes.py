
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Toplevel, PhotoImage, messagebox, Frame, Canvas, Scrollbar
from tkinter import simpledialog, Menu
from tkinter.scrolledtext import ScrolledText
from tkinter import filedialog
import os
import json
from datetime import datetime
import re
import shutil
import markdown
from fpdf import FPDF
from bs4 import BeautifulSoup

class ReadSavedNotesWindow:
    def __init__(self, parent, theme, style):
        self.parent = parent
        self.current_theme = theme
        self.style = style
        self.window = Toplevel(parent)
        self.window.title("Read Saved Notes")
        self.window.geometry("800x600")
        
        self.icon = None
        self.note_windows = []
        self.history_file = "note_history.json"
        self.images = []
        self.image_sizes = {}

        if not os.path.exists(self.history_file):
            with open(self.history_file, "w") as f:
                json.dump({}, f)

        self.create_interface()

    def create_interface(self):
        frame = ttk.Frame(self.window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        label = ttk.Label(frame, text="Click on an icon to read or edit:", font=("Arial", 14, "bold"))
        label.pack(pady=(10, 20))

        try:
            self.icon = PhotoImage(file="your_icon.png")
            self.icon = self.icon.subsample(5, 5)
        except Exception:
            self.icon = self.create_default_icon()
        
        self.icon_frame = ttk.Frame(frame)
        self.icon_frame.pack(fill="both", expand=True)

        self.populate_saved_notes()

    def create_default_icon(self):
        canvas = ttk.Canvas(self.window, width=64, height=64)
        bg_color = "#2a2a2a" if self.current_theme == "dark" else "#f0f0f0"
        fg_color = "#ffffff" if self.current_theme == "dark" else "#000000"
        
        canvas.create_rectangle(10, 5, 54, 59, fill=bg_color, outline=fg_color, width=2)
        canvas.create_line(10, 15, 54, 15, fill=fg_color, width=1)
        canvas.create_line(10, 25, 54, 25, fill=fg_color, width=1)
        canvas.create_line(10, 35, 54, 35, fill=fg_color, width=1)
        canvas.create_line(10, 45, 54, 45, fill=fg_color, width=1)
        
        canvas.update()
        icon = PhotoImage(data=canvas.postscript(colormode='color'))
        return icon

    def populate_saved_notes(self):
        for widget in self.icon_frame.winfo_children():
            widget.destroy()
        
        current_directory = os.getcwd()
        saved_notes = [f for f in os.listdir(current_directory) if f.endswith('.md')]

        if not saved_notes:
            no_notes_label = ttk.Label(self.icon_frame, text="No saved notes found.", font=("Arial", 12))
            no_notes_label.pack(pady=30)
            return
            
        row, col = 0, 0
        for note in saved_notes:
            note_frame = ttk.Frame(self.icon_frame)
            note_frame.grid(row=row, column=col, padx=10, pady=10)

            note_button = ttk.Button(note_frame, image=self.icon, command=lambda note=note: self.open_note_in_view_mode(note))
            note_button.pack()

            display_name = note if len(note) <= 20 else note[:17] + "..."
            file_name_label = ttk.Label(note_frame, text=display_name, bootstyle="info")
            file_name_label.pack()

            col += 1
            if col == 5:
                col = 0
                row += 1

    def process_markdown_line(self, canvas, line, y_pos, fg_color, in_table, table_data):
        x_start = 10
        max_width = 600
        line_height = 20
        font_normal = ("TkDefaultFont", 10)
        font_bold = ("TkDefaultFont", 10, "bold")
        font_italic = ("TkDefaultFont", 10, "italic")
        font_h1 = ("TkDefaultFont", 14, "bold")
        font_h2 = ("TkDefaultFont", 12, "bold")
        font_h3 = ("TkDefaultFont", 11, "bold")
        char_width = 6

        print(f"Processing line: '{line[:50]}...' at y: {y_pos}")
        line = line.rstrip('\n')
        if not line.strip():
            print("Empty line, adding spacing")
            return y_pos + line_height, in_table, table_data

        # Image handling
        image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
        if image_match:
            alt_text, image_path = image_match.groups()
            try:
                image = PhotoImage(file=image_path)
                img_width, img_height = image.width(), image.height()
                target_width = self.image_sizes.get(image_path, max_width)
                if img_width > target_width:
                    scale = target_width / img_width
                    img_width = int(img_width * scale)
                    img_height = int(img_height * scale)
                    image = image.subsample(int(1/scale))
                self.images.append(image)
                canvas.create_image(x_start, y_pos, image=image, anchor="nw")
                y_pos += img_height + line_height
                print(f"Rendered image: {image_path}, size: {img_width}x{img_height}, y: {y_pos}")
            except Exception as e:
                print(f"Image error: {e}")
                canvas.create_text(x_start, y_pos, text=alt_text or "Image not found", font=font_normal, fill=fg_color, anchor="nw")
                print(f"Drawing alt text: '{alt_text[:30]}...', y: {y_pos}, items: {canvas.find_all()}")
                y_pos += line_height
            return y_pos, in_table, table_data

        # Table handling
        if line.strip().startswith("|") and line.strip().endswith("|"):
            if not in_table:
                in_table = True
                table_data = []
            row = [cell.strip() for cell in line.split("|")[1:-1]]
            if row:
                table_data.append(row)
                print(f"Collected table row: {row}")
            return y_pos, in_table, table_data
            
        elif in_table:
            in_table = False
            if table_data:
                num_cols = max(len(row) for row in table_data)
                if num_cols > 0:
                    table_data = [row + [''] * (num_cols - len(row)) for row in table_data]
                    col_widths = [min(max(len(cell) for row in table_data for cell in row[:num_cols]) * char_width, 200) for _ in range(num_cols)]
                    
                    x = x_start
                    for i, cell in enumerate(table_data[0]):
                        canvas.create_text(x + 5, y_pos, text=cell, font=font_bold, fill=fg_color, anchor="nw")
                        x += col_widths[i]
                    y_pos += line_height
                    
                    x = x_start
                    for width in col_widths:
                        canvas.create_line(x, y_pos, x + width, y_pos, fill=fg_color)
                        x += width
                    y_pos += 5
                    
                    for row in table_data[1:]:
                        x = x_start
                        for i, cell in enumerate(row):
                            canvas.create_text(x + 5, y_pos, text=cell, font=font_normal, fill=fg_color, anchor="nw")
                            x += col_widths[i]
                        y_pos += line_height
                    
                    y_pos += line_height
                    print(f"Rendered table: {num_cols} columns, y: {y_pos}")
            return y_pos, False, []

        # Header handling
        if line.startswith("### "):
            text = line[4:].strip()
            canvas.create_text(x_start, y_pos, text=text, font=font_h3, fill=fg_color, anchor="nw")
            print(f"Rendered ### header: '{text[:30]}...', y: {y_pos + 22}, items: {canvas.find_all()}")
            return y_pos + 22, in_table, table_data
        elif line.startswith("## "):
            text = line[3:].strip()
            canvas.create_text(x_start, y_pos, text=text, font=font_h2, fill=fg_color, anchor="nw")
            print(f"Rendered ## header: '{text[:30]}...', y: {y_pos + 24}, items: {canvas.find_all()}")
            return y_pos + 24, in_table, table_data
        elif line.startswith("# "):
            text = line[2:].strip()
            canvas.create_text(x_start, y_pos, text=text, font=font_h1, fill=fg_color, anchor="nw")
            print(f"Rendered # header: '{text[:30]}...', y: {y_pos + 26}, items: {canvas.find_all()}")
            return y_pos + 26, in_table, table_data

        # Sequential text parsing for normal, bold, italic
        segments = []
        i = 0
        curr_text = []
        while i < len(line):
            # Bold: **text** or __text__
            if i + 2 <= len(line) and line[i:i+2] in ("**", "__"):
                j = i + 2
                while j + 2 <= len(line) and line[j:j+2] != line[i:i+2]:
                    j += 1
                if j + 2 <= len(line):
                    if curr_text:
                        segments.append(("normal", "".join(curr_text)))
                        curr_text = []
                    text = line[i+2:j]
                    if text.strip():
                        segments.append(("bold", text))
                    i = j + 2
                    continue
            # Italic: *text* or _text_
            elif i + 1 < len(line) and line[i] in ("*", "_"):
                j = i + 1
                while j + 1 <= len(line) and line[j] != line[i]:
                    j += 1
                if j + 1 <= len(line):
                    if curr_text:
                        segments.append(("normal", "".join(curr_text)))
                        curr_text = []
                    text = line[i+1:j]
                    if text.strip():
                        segments.append(("italic", text))
                    i = j + 1
                    continue
            curr_text.append(line[i])
            i += 1
        if curr_text:
            segments.append(("normal", "".join(curr_text)))

        # Render segments
        for style, text in segments:
            text = text.strip()
            if not text:
                continue
            font = font_normal
            if style == "bold":
                font = font_bold
            elif style == "italic":
                font = font_italic
            print(f"Rendering segment: style={style}, text='{text[:30]}...', y={y_pos}")
            # Basic word wrapping
            words = text.split()
            x = x_start
            curr_line = []
            for word in words:
                word_width = len(word) * char_width
                if x + word_width > max_width:
                    if curr_line:
                        rendered_text = " ".join(curr_line)
                        canvas.create_text(x_start, y_pos, text=rendered_text, font=font, fill=fg_color, anchor="nw")
                        print(f"Drawing text: '{rendered_text[:30]}...', style={style}, font={font}, x={x_start}, y={y_pos}, items={canvas.find_all()}")
                        y_pos += line_height
                        x = x_start
                        curr_line = []
                    if word_width > max_width:
                        # Truncate long words
                        subword = word[:int(max_width / char_width)]
                        canvas.create_text(x_start, y_pos, text=subword, font=font, fill=fg_color, anchor="nw")
                        print(f"Drawing subword: '{subword[:30]}...', style={style}, font={font}, x={x_start}, y={y_pos}, items={canvas.find_all()}")
                        y_pos += line_height
                        continue
                curr_line.append(word)
                x += word_width + char_width
            if curr_line:
                rendered_text = " ".join(curr_line)
                canvas.create_text(x_start, y_pos, text=rendered_text, font=font, fill=fg_color, anchor="nw")
                print(f"Drawing final text: '{rendered_text[:30]}...', style={style}, font={font}, x={x_start}, y={y_pos}, items={canvas.find_all()}")
                y_pos += line_height

        print(f"Segments for line: {segments}, final y: {y_pos}")
        return y_pos, in_table, table_data

    def load_note_history(self, note_name):
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
            return history.get(note_name, [])
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def save_note_history(self, note_name, content):
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
        except:
            history = {}

        if note_name not in history:
            history[note_name] = []
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history[note_name].append({"timestamp": timestamp, "content": content})
        
        history[note_name] = history[note_name][-10:]
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)

    def open_note_in_view_mode(self, note_name):
        note_path = os.path.join(os.getcwd(), note_name)
        if not os.path.exists(note_path):
            messagebox.showerror("Error", "The selected note could not be found.")
            return
            
        view_window = Toplevel(self.window)
        view_window.title(f"Viewing: {note_name}")
        view_window.geometry("700x500")
        view_window.minsize(500, 400)

        if self.current_theme == "dark":
            self.style.theme_use("superhero")
        else:
            self.style.theme_use("flatly")

        history_frame = ttk.Frame(view_window)
        history_frame.pack(fill="x", padx=5, pady=5)
        history_label = ttk.Label(history_frame, text="Note History:")
        history_label.pack(side="left")
        history_combo = ttk.Combobox(history_frame, state="readonly")
        history_combo.pack(side="left", padx=5, fill="x", expand=True)

        text_frame = ttk.Frame(view_window)
        text_frame.pack(expand=True, fill="both", padx=5, pady=5)

        bg_color = "#2a2a2a" if self.current_theme == "dark" else "#ffffff"
        fg_color = "#d4d4d4" if self.current_theme == "dark" else "#000000"
        
        canvas = Canvas(
            text_frame,
            background=bg_color,
            highlightthickness=0
        )
        canvas.pack(side="left", expand=True, fill="both")
        
        scrollbar = Scrollbar(text_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.config(yscrollcommand=scrollbar.set)
        
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        self.note_windows.append((view_window, canvas))

        def render_content(content):
            canvas.delete("all")
            self.images = []
            lines = content.split('\n')
            y_pos = 10
            in_table = False
            table_data = []
            image_paths = []

            print("Starting render_content")
            for line in lines:
                image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
                if image_match:
                    _, image_path = image_match.groups()
                    image_paths.append(image_path)
                y_pos, in_table, table_data = self.process_markdown_line(canvas, line, y_pos, fg_color, in_table, table_data)
            
            canvas.configure(scrollregion=(0, 0, 680, y_pos + 20))
            canvas.update()
            print(f"Updated scrollregion: (0, 0, 680, {y_pos + 20}), bbox: {canvas.bbox('all')}, items: {canvas.find_all()}")
            return image_paths

        def resize_image():
            if not image_paths:
                messagebox.showinfo("No Images", "This note contains no images to resize.")
                return
            if len(image_paths) > 1:
                selected_path = simpledialog.askstring(
                    "Select Image",
                    "Enter image path to resize (e.g., images/test.jpg):\n" + "\n".join(image_paths),
                    parent=view_window
                )
                if not selected_path or selected_path not in image_paths:
                    messagebox.showerror("Error", "Invalid image path selected.")
                    return
            else:
                selected_path = image_paths[0]
            new_width = simpledialog.askinteger(
                "Resize Image",
                f"Enter new width for {selected_path} (50–650 pixels):",
                parent=view_window,
                minvalue=50,
                maxvalue=650
            )
            if new_width:
                self.image_sizes[selected_path] = new_width
                render_content(self.original_content)

        try:
            with open(note_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.original_content = content
                image_paths = render_content(content)

            history = self.load_note_history(note_name)
            history_combo["values"] = [f"Version {i+1}: {entry['timestamp']}" for i, entry in enumerate(history)]
            if history:
                history_combo.current(0)

            def on_history_select(event):
                selected_idx = history_combo.current()
                if selected_idx >= 0:
                    self.image_sizes.clear()
                    render_content(history[selected_idx]["content"])

            history_combo.bind("<<ComboboxSelected>>", on_history_select)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load note: {str(e)}")

        button_frame = ttk.Frame(view_window)
        button_frame.pack(fill="x", pady=5)
        
        edit_button = ttk.Button(
            button_frame, 
            text="Edit", 
            command=lambda: self.open_edit_window(note_name, content, view_window, canvas)
        )
        edit_button.pack(side="left", padx=10)
        
        resize_button = ttk.Button(
            button_frame,
            text="Resize Image",
            command=resize_image
        )
        resize_button.pack(side="left", padx=10)
        
        close_button = ttk.Button(
            button_frame,
            text="Close",
            command=lambda: [view_window.destroy(), self.note_windows.remove((view_window, canvas))]
        )
        close_button.pack(side="right", padx=10)

    def open_edit_window(self, note_name, content, view_window, canvas):
        edit_window = EditNoteWindow(self, note_name, content, self.current_theme, self.style)
        self.note_windows.append((edit_window.window, edit_window.ribbon))
        view_window.destroy()
        self.note_windows.remove((view_window, canvas))

class EditNoteWindow:
    def __init__(self, parent, note_name, content, theme, style):
        self.parent = parent
        self.note_name = note_name
        self.theme = theme
        self.style = style
        self.window = Toplevel(parent.window)
        self.window.title(f"Editing: {note_name}")
        self.window.geometry("1200x700")
        try:
            self.window.state('zoomed')
        except:
            self.window.attributes('-zoomed', True)
        
        lines = content.split('\n', 1)
        self.heading_text = note_name.replace(".md", "").replace("_", " ")
        self.body_text = content
        if lines and lines[0].startswith("# "):
            self.heading_text = lines[0][2:].strip()
            self.body_text = lines[1].strip() if len(lines) > 1 else ""
        
        self.build_layout()

    def build_layout(self):
        self.ribbon = ttk.Frame(self.window, bootstyle="secondary" if self.theme == "dark" else "light")
        self.ribbon.pack(side="top", fill=X)

        ttk.Button(self.ribbon, text="Insert", command=self.show_insert_menu, bootstyle="primary").pack(side="left", padx=10, pady=5)
        ttk.Button(self.ribbon, text="Save", command=self.save_note, bootstyle="success").pack(side="left", padx=10)
        ttk.Button(self.ribbon, text="Export to PDF", command=self.export_to_pdf, bootstyle="danger").pack(side="left", padx=10)

        self.heading = ttk.Entry(self.window, font=("Arial", 16, "bold"))
        self.heading.pack(fill=X, padx=10, pady=(10, 0))
        self.heading.insert(0, self.heading_text)

        self.text_area = ScrolledText(self.window, font=("Consolas", 12), wrap="word")
        self.text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.text_area.insert("1.0", self.body_text)

    def show_insert_menu(self):
        menu = Menu(self.window, tearoff=0)
        menu.add_command(label="Template", command=self.insert_template)
        menu.add_command(label="Picture", command=self.insert_picture)
        menu.add_command(label="Equation", command=self.insert_equation)
        button = self.ribbon.winfo_children()[0]
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        menu.post(x, y)

    def insert_template(self):
        self.text_area.insert("insert", "# Heading\n\n## Subheading\n\n- Bullet 1\n- Bullet 2\n\n| Column 1 | Column 2 |\n|----------|----------|\n| Data A   | Data B   |\n")

    def insert_picture(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if file_path:
            images_dir = os.path.join(os.getcwd(), "images")
            os.makedirs(images_dir, exist_ok=True)
            image_name = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, image_name)
            try:
                shutil.copy(file_path, dest_path)
                markdown_image = f"![Image](images/{image_name})\n"
                self.text_area.insert("insert", markdown_image)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to insert image: {str(e)}")

    def insert_equation(self):
        self.text_area.insert("insert", "```latex\n\\equation\n```\n")

    def save_note(self):
        file_path = os.path.join(os.getcwd(), self.note_name)
        content = f"# {self.heading.get()}\n\n" + self.text_area.get("1.0", "end").strip()
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.parent.save_note_history(self.note_name, content)
            messagebox.showinfo("Saved", f"Note saved as {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save note: {str(e)}")

    def export_to_pdf(self):
        content = f"# {self.heading.get()}\n\n" + self.text_area.get("1.0", "end").strip()
        lines = content.split('\n')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        x_start = 10
        y_pos = 10
        max_width = 190
        char_width = 0.6
        line_height = 6
        
        in_table = False
        table_data = []
        
        for line in lines:
            line = line.rstrip('\n')
            if not line.strip():
                y_pos += line_height
                continue
            
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line.strip())
            if image_match:
                alt_text, image_path = image_match.groups()
                try:
                    from PIL import Image
                    img = Image.open(image_path)
                    img_width, img_height = img.size
                    target_width = self.parent.image_sizes.get(image_path, max_width * 2)
                    if img_width > target_width:
                        scale = target_width / img_width
                        img_width = int(img_width * scale)
                        img_height = int(img_height * scale)
                    if y_pos + img_height / 3 > 270:
                        pdf.add_page()
                        y_pos = 10
                    pdf.image(image_path, x=x_start, y=y_pos, w=img_width / 3)
                    y_pos += img_height / 3 + line_height
                except Exception:
                    pdf.set_font("Arial", size=10)
                    words = (alt_text or "Image not found").split()
                    x = x_start
                    curr_line = []
                    for word in words:
                        word_width = len(word) * char_width
                        if x + word_width > max_width:
                            if curr_line:
                                pdf.text(x_start, y_pos, " ".join(curr_line))
                                y_pos += line_height
                                x = x_start
                                curr_line = []
                            if word_width > max_width:
                                while word:
                                    subword = word[:int(max_width / char_width)]
                                    pdf.text(x_start, y_pos, subword)
                                    y_pos += line_height
                                    word = word[len(subword):]
                                x = x_start
                                continue
                        curr_line.append(word)
                        x += word_width + char_width
                    if curr_line:
                        pdf.text(x_start, y_pos, " ".join(curr_line))
                        y_pos += line_height
                continue
            
            if line.strip().startswith("|") and line.strip().endswith("|"):
                if not in_table:
                    in_table = True
                    table_data = []
                row = [cell.strip() for cell in line.split("|")[1:-1]]
                if row:
                    table_data.append(row)
                continue
            
            elif in_table:
                in_table = False
                if table_data:
                    num_cols = max(len(row) for row in table_data)
                    if num_cols > 0:
                        table_data = [row + [''] * (num_cols - len(row)) for row in table_data]
                        col_widths = [min(max(len(cell) for row in table_data for cell in row[:num_cols]) * char_width, 50) for _ in range(num_cols)]
                        total_width = sum(col_widths)
                        if total_width > max_width:
                            scale = max_width / total_width
                            col_widths = [w * scale for w in col_widths]
                        
                        if y_pos + len(table_data) * line_height > 270:
                            pdf.add_page()
                            y_pos = 10
                        
                        x = x_start
                        pdf.set_font("Arial", "B", 10)
                        for i, cell in enumerate(table_data[0]):
                            pdf.text(x + 2, y_pos + 4, cell)
                            x += col_widths[i]
                        y_pos += line_height
                        
                        x = x_start
                        pdf.set_draw_color(0)
                        for width in col_widths:
                            pdf.line(x, y_pos, x + width, y_pos)
                            x += width
                        y_pos += 2
                        
                        pdf.set_font("Arial", size=10)
                        for row in table_data[1:]:
                            x = x_start
                            for i, cell in enumerate(row):
                                pdf.text(x + 2, y_pos + 4, cell)
                                x += col_widths[i]
                            y_pos += line_height
                        
                        y_pos += line_height
                        table_data = []
                continue
            
            if line.startswith("### "):
                pdf.set_font("Arial", "B", 12)
                pdf.text(x_start, y_pos + 4, line[4:].strip())
                y_pos += line_height + 2
                continue
            elif line.startswith("## "):
                pdf.set_font("Arial", "B", 14)
                pdf.text(x_start, y_pos + 4, line[3:].strip())
                y_pos += line_height + 3
                continue
            elif line.startswith("# "):
                pdf.set_font("Arial", "B", 16)
                pdf.text(x_start, y_pos + 4, line[2:].strip())
                y_pos += line_height + 4
                continue
            
            x = x_start
            i = 0
            curr_text = []
            curr_style = ""
            while i < len(line):
                if i + 4 <= len(line) and line[i:i+2] in ("**", "__") and line[i+2:].find(line[i:i+2]) != -1:
                    end = line[i+2:].find(line[i:i+2]) + i + 2
                    if end > i + 2 and curr_text:
                        pdf.set_font("Arial", curr_style, 10)
                        words = "".join(curr_text).split()
                        x = x_start
                        curr_line = []
                        for word in words:
                            word_width = len(word) * char_width
                            if x + word_width > max_width:
                                if curr_line:
                                    pdf.text(x_start, y_pos, " ".join(curr_line))
                                    y_pos += line_height
                                    x = x_start
                                    curr_line = []
                                if word_width > max_width:
                                    while word:
                                        subword = word[:int(max_width / char_width)]
                                        pdf.text(x_start, y_pos, subword)
                                        y_pos += line_height
                                        word = word[len(subword):]
                                    x = x_start
                                    continue
                            curr_line.append(word)
                            x += word_width + char_width
                        if curr_line:
                            pdf.text(x_start, y_pos, " ".join(curr_line))
                            y_pos += line_height
                        curr_text = []
                        curr_style = ""
                    if end > i + 2:
                        text = line[i+2:end]
                        pdf.set_font("Arial", "B", 10)
                        words = text.split()
                        x = x_start
                        curr_line = []
                        for word in words:
                            word_width = len(word) * char_width
                            if x + word_width > max_width:
                                if curr_line:
                                    pdf.text(x_start, y_pos, " ".join(curr_line))
                                    y_pos += line_height
                                    x = x_start
                                    curr_line = []
                                if word_width > max_width:
                                    while word:
                                        subword = word[:int(max_width / char_width)]
                                        pdf.text(x_start, y_pos, subword)
                                        y_pos += line_height
                                        word = word[len(subword):]
                                    x = x_start
                                    continue
                            curr_line.append(word)
                            x += word_width + char_width
                        if curr_line:
                            pdf.text(x_start, y_pos, " ".join(curr_line))
                            y_pos += line_height
                        i = end + 2
                        continue
                elif i + 2 <= len(line) and line[i] in ("*", "_") and line[i+1:].find(line[i]) != -1:
                    end = line[i+1:].find(line[i]) + i + 1
                    if end > i + 1 and curr_text:
                        pdf.set_font("Arial", curr_style, 10)
                        words = "".join(curr_text).split()
                        x = x_start
                        curr_line = []
                        for word in words:
                            word_width = len(word) * char_width
                            if x + word_width > max_width:
                                if curr_line:
                                    pdf.text(x_start, y_pos, " ".join(curr_line))
                                    y_pos += line_height
                                    x = x_start
                                    curr_line = []
                                if word_width > max_width:
                                    while word:
                                        subword = word[:int(max_width / char_width)]
                                        pdf.text(x_start, y_pos, subword)
                                        y_pos += line_height
                                        word = word[len(subword):]
                                    x = x_start
                                    continue
                            curr_line.append(word)
                            x += word_width + char_width
                        if curr_line:
                            pdf.text(x_start, y_pos, " ".join(curr_line))
                            y_pos += line_height
                        curr_text = []
                        curr_style = ""
                    if end > i + 1:
                        text = line[i+1:end]
                        pdf.set_font("Arial", "I", 10)
                        words = text.split()
                        x = x_start
                        curr_line = []
                        for word in words:
                            word_width = len(word) * char_width
                            if x + word_width > max_width:
                                if curr_line:
                                    pdf.text(x_start, y_pos, " ".join(curr_line))
                                    y_pos += line_height
                                    x = x_start
                                    curr_line = []
                                if word_width > max_width:
                                    while word:
                                        subword = word[:int(max_width / char_width)]
                                        pdf.text(x_start, y_pos, subword)
                                        y_pos += line_height
                                        word = word[len(subword):]
                                    x = x_start
                                    continue
                            curr_line.append(word)
                            x += word_width + char_width
                        if curr_line:
                            pdf.text(x_start, y_pos, " ".join(curr_line))
                            y_pos += line_height
                        i = end + 1
                        continue
                curr_text.append(line[i])
                i += 1
            if curr_text:
                pdf.set_font("Arial", curr_style, 10)
                words = "".join(curr_text).split()
                x = x_start
                curr_line = []
                for word in words:
                    word_width = len(word) * char_width
                    if x + word_width > max_width:
                        if curr_line:
                            pdf.text(x_start, y_pos, " ".join(curr_line))
                            y_pos += line_height
                            x = x_start
                            curr_line = []
                        if word_width > max_width:
                            while word:
                                subword = word[:int(max_width / char_width)]
                                pdf.text(x_start, y_pos, subword)
                                y_pos += line_height
                                word = word[len(subword):]
                            x = x_start
                            continue
                    curr_line.append(word)
                    x += word_width + char_width
                if curr_line:
                    pdf.text(x_start, y_pos, " ".join(curr_line))
                    y_pos += line_height
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                pdf.output(file_path)
                messagebox.showinfo("Export", "Note exported as PDF!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")