import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Drawing Canvas App")
        
        # Variables
        self.draw_color = "black"
        self.bg_color = "white"
        self.eraser_on = False
        self.current_tool = "pen"
        self.line_width = 2
        self.start_x, self.start_y = None, None
        self.shapes = ["line", "rectangle", "oval", "triangle"]
        
        # Create main frames
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create Canvas with scrollbars
        self.canvas_frame = ttk.Frame(self.main_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_color, bd=2, relief=tk.GROOVE,
                               scrollregion=(0, 0, 1200, 900))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbars
        v_scroll = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll = ttk.Scrollbar(self.main_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        h_scroll.pack(fill=tk.X)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        # Create Tool Frame
        self.tool_frame = ttk.Frame(root)
        self.tool_frame.pack(fill=tk.X)
        
        # Create buttons
        self.create_buttons()
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)
        
        # Initialize PIL image for drawing
        self.image = Image.new("RGB", (1200, 900), self.bg_color)
        self.draw = ImageDraw.Draw(self.image)
        
        # Store temporary canvas items
        self.temp_items = []
        
    def create_buttons(self):
        # Tool selection frame
        tool_selection_frame = ttk.LabelFrame(self.tool_frame, text="Tools")
        tool_selection_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Pen tool
        pen_btn = ttk.Button(tool_selection_frame, text="Pen", 
                            command=lambda: self.select_tool("pen"))
        pen_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Shape tools
        for shape in self.shapes:
            btn = ttk.Button(tool_selection_frame, text=shape.capitalize(), 
                            command=lambda s=shape: self.select_tool(s))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Color frame
        color_frame = ttk.LabelFrame(self.tool_frame, text="Colors")
        color_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        color_btn = ttk.Button(color_frame, text="Choose Color", command=self.choose_color)
        color_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        eraser_btn = ttk.Button(color_frame, text="Eraser", command=self.use_eraser)
        eraser_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.tool_frame, text="Options")
        options_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        clear_btn = ttk.Button(options_frame, text="Clear Canvas", command=self.clear_canvas)
        clear_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        save_btn = ttk.Button(options_frame, text="Save Drawing", command=self.save_drawing)
        save_btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Line width slider
        width_frame = ttk.LabelFrame(self.tool_frame, text="Line Width")
        width_frame.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.width_slider = ttk.Scale(width_frame, from_=1, to=20, 
                                    command=self.change_width)
        self.width_slider.set(self.line_width)
        self.width_slider.pack(padx=5)
        
    def select_tool(self, tool):
        self.current_tool = tool
        self.eraser_on = False
        
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.draw_color = color
            self.eraser_on = False
            
    def use_eraser(self):
        self.eraser_on = True
        self.draw_color = self.bg_color
        
    def change_width(self, width):
        self.line_width = int(float(width))
        
    def start_draw(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "pen" or self.eraser_on:
            self.draw.line([(self.start_x, self.start_y), (self.start_x+1, self.start_y+1)], 
                          fill=self.draw_color, width=self.line_width)
            self.update_canvas()
            
    def draw(self, event):
        if self.start_x is None or self.start_y is None:
            return
            
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        if self.current_tool == "pen" or self.eraser_on:
            self.draw.line([(self.start_x, self.start_y), (current_x, current_y)], 
                          fill=self.draw_color, width=self.line_width)
            self.start_x, self.start_y = current_x, current_y
            self.update_canvas()
        elif self.current_tool in self.shapes:
            # Clear temporary items
            for item in self.temp_items:
                self.canvas.delete(item)
            self.temp_items = []
            
            # Draw temporary shape
            if self.current_tool == "line":
                item = self.canvas.create_line(self.start_x, self.start_y, current_x, current_y, 
                                            fill=self.draw_color, width=self.line_width)
            elif self.current_tool == "rectangle":
                item = self.canvas.create_rectangle(self.start_x, self.start_y, current_x, current_y, 
                                                 outline=self.draw_color, width=self.line_width)
            elif self.current_tool == "oval":
                item = self.canvas.create_oval(self.start_x, self.start_y, current_x, current_y, 
                                            outline=self.draw_color, width=self.line_width)
            elif self.current_tool == "triangle":
                item = self.canvas.create_polygon(self.start_x, self.start_y, 
                                               current_x, current_y, 
                                               self.start_x, current_y,
                                               outline=self.draw_color, width=self.line_width)
            
            self.temp_items.append(item)
                    
    def reset(self, event):
        if self.start_x is None or self.start_y is None:
            return
            
        current_x = self.canvas.canvasx(event.x)
        current_y = self.canvas.canvasy(event.y)
        
        # Clear temporary items
        for item in self.temp_items:
            self.canvas.delete(item)
        self.temp_items = []
        
        if self.current_tool in self.shapes:
            try:
                # Ensure coordinates are ordered correctly
                x0, y0, x1, y1 = sorted([self.start_x, current_x])[0], sorted([self.start_y, current_y])[0], \
                                 sorted([self.start_x, current_x])[1], sorted([self.start_y, current_y])[1]
                
                # Draw the final shape on the PIL image
                if self.current_tool == "line":
                    self.draw.line([(self.start_x, self.start_y), (current_x, current_y)], 
                                 fill=self.draw_color, width=self.line_width)
                elif self.current_tool == "rectangle":
                    self.draw.rectangle([x0, y0, x1, y1], 
                                      outline=self.draw_color, width=self.line_width)
                elif self.current_tool == "oval":
                    self.draw.ellipse([x0, y0, x1, y1], 
                                    outline=self.draw_color, width=self.line_width)
                elif self.current_tool == "triangle":
                    self.draw.polygon([self.start_x, self.start_y, current_x, current_y, self.start_x, current_y], 
                                    outline=self.draw_color, width=self.line_width)
                
                self.update_canvas()
            except Exception as e:
                messagebox.showerror("Error", f"Could not complete drawing: {str(e)}")
            
        self.start_x, self.start_y = None, None
        
    def update_canvas(self):
        # Convert PIL image to PhotoImage
        self.tk_image = ImageTk.PhotoImage(self.image)
        
        # Update canvas
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW)
        
    def clear_canvas(self):
        if messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the canvas?"):
            self.canvas.delete("all")
            self.image = Image.new("RGB", (1200, 900), self.bg_color)
            self.draw = ImageDraw.Draw(self.image)
            self.update_canvas()
        
    def save_drawing(self):
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                title="Save drawing as"
            )
            
            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Success", f"Drawing saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")

