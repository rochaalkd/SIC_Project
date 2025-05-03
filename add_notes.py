
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Toplevel, filedialog, X, BOTH, Menu
from tkinter.messagebox import showinfo
from tkinter.scrolledtext import ScrolledText
import markdown
from fpdf import FPDF
from bs4 import BeautifulSoup
import os
import shutil

class AddNoteWindow:
    def __init__(self, parent):
        self.editor = Toplevel(parent)
        self.editor.title("New Note")
        self.editor.geometry("1200x700")
        try:
            self.editor.state('zoomed')
        except:
            self.editor.attributes('-zoomed', True)
        self.build_layout()

    def build_layout(self):
        ribbon = ttk.Frame(self.editor, bootstyle="secondary")
        ribbon.pack(side="top", fill=X)

        # Insert button now triggers a dropdown menu
        ttk.Button(ribbon, text="Insert", command=self.show_insert_menu, bootstyle="primary").pack(side="left", padx=10, pady=5)
        ttk.Button(ribbon, text="Edit", command=self.edit_content, bootstyle="warning").pack(side="left", padx=10)
        ttk.Button(ribbon, text="Save", command=self.save_note, bootstyle="success").pack(side="left", padx=10)

        self.heading = ttk.Entry(self.editor, font=("Helvetica", 16, "bold"))
        self.heading.pack(fill=X, padx=10, pady=(10, 0))

        self.text_area = ScrolledText(self.editor, font=("Consolas", 12), wrap="word")
        self.text_area.pack(fill=BOTH, expand=True, padx=10, pady=10)

        export_btn = ttk.Button(self.editor, text="Export to PDF", command=self.export_to_pdf, bootstyle="danger")
        export_btn.place(relx=0.95, rely=0.9, anchor="center")

    def show_insert_menu(self):
        """Show a dropdown menu with Template, Picture, and Equation options"""
        menu = Menu(self.editor, tearoff=0)
        menu.add_command(label="Template", command=self.insert_template)
        menu.add_command(label="Picture", command=self.insert_picture)
        menu.add_command(label="Equation", command=self.insert_equation)
        # Get button position to display menu below it
        button = self.editor.winfo_children()[0].winfo_children()[0]  # First button in ribbon
        x = button.winfo_rootx()
        y = button.winfo_rooty() + button.winfo_height()
        menu.post(x, y)

    def insert_template(self):
        """Insert the original markdown template"""
        self.text_area.insert("insert", "# Heading\n\n## Subheading\n\n- Bullet 1\n- Bullet 2\n\n| Column 1 | Column 2 |\n|----------|----------|\n| Data A   | Data B   |\n")

    def insert_picture(self):
        """Insert an image from the gallery with markdown syntax"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if file_path:
            # Create images folder if it doesn't exist
            images_dir = os.path.join(os.getcwd(), "images")
            os.makedirs(images_dir, exist_ok=True)
            # Copy image to images folder
            image_name = os.path.basename(file_path)
            dest_path = os.path.join(images_dir, image_name)
            try:
                shutil.copy(file_path, dest_path)
                # Insert markdown image syntax at cursor
                markdown_image = f"![Image](images/{image_name})\n"
                self.text_area.insert("insert", markdown_image)
            except Exception as e:
                showinfo("Error", f"Failed to insert image: {str(e)}")

    def insert_equation(self):
        """Insert a placeholder LaTeX equation code block"""
        self.text_area.insert("insert", "```latex\n\\equation\n```\n")

    def edit_content(self):
        self.text_area.config(state="normal")

    def save_note(self):
        title = self.heading.get().strip().replace(" ", "_") or "untitled"
        file_path = f"{title}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {self.heading.get()}\n\n")
            f.write(self.text_area.get("1.0", "end"))
        showinfo("Saved", f"Note saved as {file_path}")

    def export_to_pdf(self):
        content = f"# {self.heading.get()}\n\n" + self.text_area.get("1.0", "end")
        html = markdown.markdown(content)
        text = BeautifulSoup(html, "html.parser").get_text()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in text.split("\n"):
            pdf.multi_cell(0, 10, line)
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf.output(file_path)
            showinfo("Export", "Note exported as PDF!")
