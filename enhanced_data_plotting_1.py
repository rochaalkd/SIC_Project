import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
from fpdf import FPDF
import os
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import seaborn as sns
from scipy.stats import linregress
import sympy as sp
import re
import math
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

class DataVisualizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title(" Data Visualization")
        # Only set geometry if root is the main window (not Toplevel)
        if not isinstance(root, ttk.Toplevel):
            self.root.geometry("1100x750")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", font=('Helvetica', 10))
        self.style.configure("TLabel", font=('Helvetica', 10))
        self.style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
        
        # Data storage
        self.data = pd.DataFrame()
        self.dimension = tk.IntVar(value=2)  # Default to 2D
        self.column_names = ['X', 'Y', 'Z']  # Default column names
        
        # Math functions reference
        self.math_functions = {
            'Basic': ['x', 'x^2', 'x^3', 'sqrt(x)', 'abs(x)'],
            'Trigonometric': ['sin(x)', 'cos(x)', 'tan(x)', 'asin(x)', 'acos(x)', 'atan(x)'],
            'Hyperbolic': ['sinh(x)', 'cosh(x)', 'tanh(x)', 'asinh(x)', 'acosh(x)', 'atanh(x)'],
            'Exponential': ['exp(x)', 'e^x', '2^x', '10^x'],
            'Logarithmic': ['log(x)', 'log10(x)', 'log2(x)', 'ln(x)'],
            '2D Functions': ['x^2 + y^2', 'sin(x) + cos(y)', 'exp(-(x^2 + y^2))'],
            '3D Functions': ['x^2 + y^2 - z', 'sin(x) + cos(y) - z']
        }
        
        # Setup UI
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding=10)
        
        # Title
        self.title_label = ttk.Label(
            self.main_frame, 
            text=" Data Visualization", 
            font=('Helvetica', 16, 'bold'),
            bootstyle="primary"
        )
        
        # Column naming frame
        self.name_frame = ttk.LabelFrame(self.main_frame, text="Column Names", padding=10)
        self.name_label1 = ttk.Label(self.name_frame, text="1st Column:")
        self.name_entry1 = ttk.Entry(self.name_frame, width=15)
        self.name_label2 = ttk.Label(self.name_frame, text="2nd Column:")
        self.name_entry2 = ttk.Entry(self.name_frame, width=15)
        self.name_label3 = ttk.Label(self.name_frame, text="3rd Column:")
        self.name_entry3 = ttk.Entry(self.name_frame, width=15)
        self.name_button = ttk.Button(
            self.name_frame,
            text="Update Names",
            command=self.update_column_names,
            bootstyle="info-outline",
            width=12
        )
        
        # Function input frame with function selector
        self.function_frame = ttk.LabelFrame(self.main_frame, text="Function Plotting", padding=10)
        
        # Function selection combobox
        self.function_category = ttk.Combobox(
            self.function_frame, 
            values=list(self.math_functions.keys()),
            state="readonly",
            width=15
        )
        self.function_category.set("Basic")
        self.function_category.bind("<<ComboboxSelected>>", self.update_function_examples)
        
        self.function_example = ttk.Combobox(
            self.function_frame,
            values=self.math_functions['Basic'],
            state="readonly",
            width=15
        )
        self.function_example.bind("<<ComboboxSelected>>", self.insert_function_example)
        
        self.function_label = ttk.Label(self.function_frame, text="Enter function (e.g., y=sin(x), z=x^2+y^2):")
        self.function_entry = ttk.Entry(self.function_frame, width=40)
        self.plot_function_btn = ttk.Button(
            self.function_frame,
            text="Plot Function",
            command=self.plot_function,
            bootstyle="info",
            width=12
        )
        
        # Dimension selector
        self.dim_frame = ttk.LabelFrame(self.main_frame, text="Data Dimension (switching clears all data)", padding=10)
        self.dim_1d = ttk.Radiobutton(
            self.dim_frame, text="1D", variable=self.dimension, value=1,
            command=self.update_dimension
        )
        self.dim_2d = ttk.Radiobutton(
            self.dim_frame, text="2D", variable=self.dimension, value=2,
            command=self.update_dimension
        )
        self.dim_3d = ttk.Radiobutton(
            self.dim_frame, text="3D", variable=self.dimension, value=3,
            command=self.update_dimension
        )
        
        # Data table with equal column widths
        self.table_frame = ttk.LabelFrame(self.main_frame, text="Data Table", padding=10)
        self.table = ttk.Treeview(
            self.table_frame,
            columns=('col1', 'col2', 'col3'),
            show='headings',
            selectmode='browse',
            bootstyle="primary"
        )
        
        # Configure equal column widths
        col_width = 150  # Fixed width for all columns
        for col in self.table['columns']:
            self.table.column(col, width=col_width, anchor='center')
            self.table.heading(col, text='')
        
        self.scrollbar = ttk.Scrollbar(self.table_frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=self.scrollbar.set)
        
        # Input fields with updated labels
        self.input_frame = ttk.Frame(self.main_frame, padding=10)
        self.x_label = ttk.Label(self.input_frame, text="")
        self.x_entry = ttk.Entry(self.input_frame)
        self.y_label = ttk.Label(self.input_frame, text="")
        self.y_entry = ttk.Entry(self.input_frame)
        self.z_label = ttk.Label(self.input_frame, text="")
        self.z_entry = ttk.Entry(self.input_frame)
        
        # Buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.add_btn = ttk.Button(
            self.button_frame,
            text="Add Data",
            command=self.insert_data,
            bootstyle="success",
            width=12
        )
        self.edit_btn = ttk.Button(
            self.button_frame,
            text="Edit Data",
            command=self.edit_data,
            bootstyle="warning",
            width=12
        )
        self.delete_btn = ttk.Button(
            self.button_frame,
            text="Delete Data",
            command=self.delete_data,
            bootstyle="danger",
            width=12
        )
        self.clear_btn = ttk.Button(
            self.button_frame,
            text="Clear All",
            command=self.clear_all_data,
            bootstyle="danger-outline",
            width=12
        )
        self.plot_btn = ttk.Button(
            self.button_frame,
            text="Plot Data",
            command=self.plot_data,
            bootstyle="info",
            width=12
        )
        self.stats_btn = ttk.Button(
            self.button_frame,
            text="Show Stats",
            command=self.show_stats,
            bootstyle="secondary",
            width=12
        )
        self.save_btn = ttk.Button(
            self.button_frame,
            text="Save Report",
            command=self.save_to_pdf,
            bootstyle="primary",
            width=15
        )
        
        # Stats frame
        self.stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics Summary", padding=10)
        self.stats_text = tk.Text(
            self.stats_frame, 
            height=10, 
            wrap=tk.WORD, 
            font=('Consolas', 10)
        )
        self.stats_scroll = ttk.Scrollbar(
            self.stats_frame, 
            orient=VERTICAL, 
            command=self.stats_text.yview
        )
        self.stats_text.configure(yscrollcommand=self.stats_scroll.set)
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            bootstyle="secondary",
            relief=SUNKEN,
            anchor=tk.W
        )
    
    def setup_layout(self):
        self.main_frame.pack(fill=tk.BOTH, expand=tk.YES)
        self.title_label.pack(pady=(0, 10))
        
        # Column naming frame
        self.name_frame.pack(fill=tk.X, pady=5)
        self.name_label1.grid(row=0, column=0, padx=5, sticky=tk.E)
        self.name_entry1.grid(row=0, column=1, padx=5)
        self.name_label2.grid(row=0, column=2, padx=5, sticky=tk.E)
        self.name_entry2.grid(row=0, column=3, padx=5)
        self.name_label3.grid(row=0, column=4, padx=5, sticky=tk.E)
        self.name_entry3.grid(row=0, column=5, padx=5)
        self.name_button.grid(row=0, column=6, padx=10)
        
        # Function frame with improved layout
        self.function_frame.pack(fill=tk.X, pady=5)
        
        # First row: Function selection
        ttk.Label(self.function_frame, text="Function Category:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.function_category.grid(row=0, column=1, padx=5, sticky=tk.W)
        ttk.Label(self.function_frame, text="Example:").grid(row=0, column=2, padx=5, sticky=tk.E)
        self.function_example.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Second row: Function entry
        self.function_label.grid(row=1, column=0, columnspan=2, padx=5, sticky=tk.W)
        self.function_entry.grid(row=1, column=2, columnspan=2, padx=5, sticky=tk.EW)
        self.plot_function_btn.grid(row=1, column=4, padx=5)
        
        # Set default names
        self.name_entry1.insert(0, 'X')
        self.name_entry2.insert(0, 'Y')
        self.name_entry3.insert(0, 'Z')
        self.update_column_names()
        
        # Dimension selector
        self.dim_frame.pack(fill=tk.X, pady=5)
        self.dim_1d.pack(side=tk.LEFT, padx=10)
        self.dim_2d.pack(side=tk.LEFT, padx=10)
        self.dim_3d.pack(side=tk.LEFT, padx=10)
        
        # Table
        self.table_frame.pack(fill=tk.BOTH, expand=tk.YES, pady=5)
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Input fields
        self.input_frame.pack(fill=tk.X, pady=5)
        self.x_label.grid(row=0, column=0, padx=5, sticky=tk.E)
        self.x_entry.grid(row=0, column=1, padx=5)
        self.y_label.grid(row=0, column=2, padx=5, sticky=tk.E)
        self.y_entry.grid(row=0, column=3, padx=5)
        self.z_label.grid(row=0, column=4, padx=5, sticky=tk.E)
        self.z_entry.grid(row=0, column=5, padx=5)
        
        # Buttons
        self.button_frame.pack(fill=tk.X, pady=10)
        self.add_btn.grid(row=0, column=0, padx=5, pady=5)
        self.edit_btn.grid(row=0, column=1, padx=5, pady=5)
        self.delete_btn.grid(row=0, column=2, padx=5, pady=5)
        self.clear_btn.grid(row=0, column=3, padx=5, pady=5)
        self.plot_btn.grid(row=0, column=4, padx=5, pady=5)
        self.stats_btn.grid(row=0, column=5, padx=5, pady=5)
        self.save_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Stats frame
        self.stats_frame.pack(fill=tk.BOTH, expand=tk.YES, pady=5)
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.stats_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)
        
        # Bindings
        self.root.bind('<Return>', lambda e: self.insert_data())
        self.root.bind('<Delete>', lambda e: self.delete_data())
        self.table.bind('<<TreeviewSelect>>', self.on_row_select)
        
        # Initial setup
        self.update_dimension()
        self.x_entry.focus_set()
    
    def update_function_examples(self, event=None):
        category = self.function_category.get()
        self.function_example['values'] = self.math_functions[category]
        self.function_example.current(0)
    
    def insert_function_example(self, event=None):
        example = self.function_example.get()
        self.function_entry.delete(0, tk.END)
        self.function_entry.insert(0, example)
    
    def update_column_names(self):
        self.column_names = [
            self.name_entry1.get() or 'X',
            self.name_entry2.get() or 'Y',
            self.name_entry3.get() or 'Z'
        ]
        
        for i, col in enumerate(['col1', 'col2', 'col3']):
            if i < len(self.column_names):
                self.table.heading(col, text=self.column_names[i])
            else:
                self.table.heading(col, text='')
        
        self.x_label.config(text=f"{self.column_names[0]}:")
        self.y_label.config(text=f"{self.column_names[1]}:" if self.dimension.get() >= 2 else "")
        self.z_label.config(text=f"{self.column_names[2]}:" if self.dimension.get() >= 3 else "")
        
        if not self.data.empty:
            self.data.columns = self.column_names[:self.dimension.get()]
        
        self.update_status("Column names updated")
    
    def clear_all_data(self):
        for item in self.table.get_children():
            self.table.delete(item)
        
        self.data = pd.DataFrame(columns=self.column_names[:self.dimension.get()])
        
        self.x_entry.delete(0, tk.END)
        self.y_entry.delete(0, tk.END)
        self.z_entry.delete(0, tk.END)
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.config(state=tk.DISABLED)
        
        self.update_status("Cleared all data")
    
    def update_dimension(self):
        if not self.data.empty:
            if not messagebox.askyesno(
                "Confirm Clear Data",
                "Switching dimensions will clear all current data. Continue?",
                icon='warning'
            ):
                prev_dim = 1 if self.dimension.get() != 1 else 2
                self.dimension.set(prev_dim)
                return
        
        dim = self.dimension.get()
        self.clear_all_data()
        
        for i, col in enumerate(['col1', 'col2', 'col3']):
            if i < dim:
                self.table.heading(col, text=self.column_names[i])
                self.table.column(col, width=150, stretch=False)
            else:
                self.table.heading(col, text='')
                self.table.column(col, width=0, stretch=False)
        
        self.y_entry.config(state=tk.NORMAL if dim >= 2 else tk.DISABLED)
        self.z_entry.config(state=tk.NORMAL if dim >= 3 else tk.DISABLED)
        
        self.x_label.config(text=f"{self.column_names[0]}:")
        self.y_label.config(text=f"{self.column_names[1]}:" if dim >= 2 else "")
        self.z_label.config(text=f"{self.column_names[2]}:" if dim >= 3 else "")
        
        self.x_entry.focus_set()
        self.update_status(f"Switched to {dim}D mode (data cleared)")
    
    def insert_data(self, event=None):
        dim = self.dimension.get()
        vals = [
            self.x_entry.get(),
            self.y_entry.get() if dim >= 2 else "0",
            self.z_entry.get() if dim >= 3 else "0"
        ]
        
        try:
            data_values = [float(vals[i]) if i < dim else np.nan for i in range(3)]
            
            self.table.insert('', 'end', values=[vals[i] for i in range(dim)])
            
            new_row = {self.column_names[i]: data_values[i] for i in range(dim)}
            self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
            
            self.x_entry.delete(0, tk.END)
            if dim >= 2: self.y_entry.delete(0, tk.END)
            if dim >= 3: self.z_entry.delete(0, tk.END)
            self.x_entry.focus_set()
            
            self.update_status(f"Added {dim}D data point")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def edit_data(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to edit")
            return
        
        dim = self.dimension.get()
        vals = [
            self.x_entry.get(),
            self.y_entry.get() if dim >= 2 else "0",
            self.z_entry.get() if dim >= 3 else "0"
        ]
        
        try:
            data_values = [float(vals[i]) if i < dim else np.nan for i in range(3)]
            
            self.table.item(selected_item, values=[vals[i] for i in range(dim)])
            
            index = self.table.index(selected_item)
            self.data.loc[index] = {self.column_names[i]: data_values[i] for i in range(dim)}
            
            self.update_status(f"Updated row {index+1}")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")
    
    def delete_data(self, event=None):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to delete")
            return
        
        index = self.table.index(selected_item)
        self.table.delete(selected_item)
        self.data = self.data.drop(index).reset_index(drop=True)
        self.update_status(f"Deleted row {index+1}")
    
    def on_row_select(self, event):
        selected = self.table.selection()
        if not selected:
            return
        
        values = self.table.item(selected[0], 'values')
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, values[0])
        
        if self.dimension.get() >= 2:
            self.y_entry.delete(0, tk.END)
            if len(values) > 1:
                self.y_entry.insert(0, values[1])
        
        if self.dimension.get() >= 3:
            self.z_entry.delete(0, tk.END)
            if len(values) > 2:
                self.z_entry.insert(0, values[2])
    
    def parse_function(self, func_str):
        func_str = func_str.replace('^', '**')
        func_str = func_str.replace('ln(', 'log(')
        
        transformations = (standard_transformations + (implicit_multiplication_application,))
        
        if '=' in func_str:
            lhs, rhs = func_str.split('=', 1)
            lhs = lhs.strip()
            rhs = rhs.strip()
            
            dep_var = lhs
            try:
                expr = parse_expr(rhs, transformations=transformations)
            except:
                expr = sp.sympify(rhs)
        else:
            dep_var = 'y'
            try:
                expr = parse_expr(func_str, transformations=transformations)
            except:
                expr = sp.sympify(func_str)
        
        variables = sorted([str(v) for v in expr.free_symbols], key=lambda x: x.lower())
        
        return dep_var, expr, variables
    
    def plot_function(self):
        func_str = self.function_entry.get().strip()
        if not func_str:
            messagebox.showwarning("Warning", "Please enter a function to plot")
            return
        
        dim = self.dimension.get()
        
        try:
            dep_var, expr, variables = self.parse_function(func_str)
            
            if dim == 1 and len(variables) > 1:
                raise ValueError("1D mode only supports functions of one variable")
            if dim == 2 and len(variables) > 2:
                raise ValueError("2D mode only supports functions of one or two variables")
            if dim == 3 and len(variables) > 3:
                raise ValueError("3D mode only supports functions of up to three variables")
            
            plt.close('all')
            
            if dim == 1:
                x_sym = sp.symbols('x')
                
                if dep_var.lower() != 'y':
                    y_sym = sp.symbols('y')
                    f = sp.lambdify((x_sym, y_sym), expr - sp.sympify(dep_var), modules=['numpy', {'log': np.log}])
                    
                    x_vals = np.linspace(-10, 10, 400)
                    y_vals = np.linspace(-10, 10, 400)
                    X, Y = np.meshgrid(x_vals, y_vals)
                    Z = f(X, Y)
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.contour(X, Y, Z, levels=[0], colors='r')
                    ax.set_title(f'Implicit Plot: {func_str}')
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.grid(True)
                else:
                    f = sp.lambdify(x_sym, expr, modules=['numpy', {'log': np.log}])
                    
                    try:
                        test_vals = np.linspace(-10, 10, 20)
                        f(test_vals)
                        x_vals = np.linspace(-10, 10, 400)
                    except:
                        try:
                            test_vals = np.linspace(0.1, 10, 20)
                            f(test_vals)
                            x_vals = np.linspace(0.1, 10, 400)
                        except:
                            x_vals = np.linspace(-5, 5, 400)
                    
                    y_vals = f(x_vals)
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.plot(x_vals, y_vals, 'r-', linewidth=2, label=f'{dep_var} = {sp.pretty(expr)}')
                    ax.set_title(f'Function Plot: {dep_var} = {expr}')
                    ax.set_xlabel('x')
                    ax.set_ylabel(dep_var)
                    ax.grid(True)
                    ax.legend()
            
            elif dim == 2:
                if '=' in func_str:
                    if dep_var.lower() == 'y':
                        x_sym = sp.symbols('x')
                        f = sp.lambdify(x_sym, expr, modules=['numpy', {'log': np.log}])
                        
                        x_vals = np.linspace(-10, 10, 400)
                        y_vals = f(x_vals)
                        
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.plot(x_vals, y_vals, 'r-', linewidth=2, label=f'y = {expr}')
                        ax.set_title(f'Function Plot: y = {expr}')
                        ax.set_xlabel('x')
                        ax.set_ylabel('y')
                        ax.grid(True)
                        ax.legend()
                    else:
                        x_sym, y_sym = sp.symbols('x y')
                        f = sp.lambdify((x_sym, y_sym), expr - sp.sympify(dep_var), modules=['numpy', {'log': np.log}])
                        
                        x_vals = np.linspace(-10, 10, 100)
                        y_vals = np.linspace(-10, 10, 100)
                        X, Y = np.meshgrid(x_vals, y_vals)
                        Z = f(X, Y)
                        
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.contour(X, Y, Z, levels=[0], colors='r', linewidths=2)
                        ax.set_title(f'Implicit Plot: {func_str}')
                        ax.set_xlabel('x')
                        ax.set_ylabel('y')
                        ax.grid(True)
                else:
                    x_sym = sp.symbols('x')
                    f = sp.lambdify(x_sym, expr, modules=['numpy', {'log': np.log}])
                    
                    x_vals = np.linspace(-10, 10, 400)
                    y_vals = f(x_vals)
                    
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.plot(x_vals, y_vals, 'r-', linewidth=2, label=f'y = {expr}')
                    ax.set_title(f'Function Plot: y = {expr}')
                    ax.set_xlabel('x')
                    ax.set_ylabel('y')
                    ax.grid(True)
                    ax.legend()
            
            elif dim == 3:
                if dep_var.lower() != 'z':
                    raise ValueError("For 3D, please use z=f(x,y) format")
                
                x_sym, y_sym = sp.symbols('x y')
                f = sp.lambdify((x_sym, y_sym), expr, modules=['numpy', {'log': np.log}])
                
                x_vals = np.linspace(-10, 10, 50)
                y_vals = np.linspace(-10, 10, 50)
                X, Y = np.meshgrid(x_vals, y_vals)
                Z = f(X, Y)
                
                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
                surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.8)
                fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)
                ax.set_title(f'3D Function Plot: z = {expr}')
                ax.set_xlabel('x')
                ax.set_ylabel('y')
                ax.set_zlabel('z')
                
                offset = Z.min() - 0.1 * (Z.max() - Z.min())
                ax.contour(X, Y, Z, zdir='z', offset=offset, cmap='viridis')
                ax.contour(X, Y, Z, zdir='x', offset=x_vals.min() - 1, cmap='viridis')
                ax.contour(X, Y, Z, zdir='y', offset=y_vals.max() + 1, cmap='viridis')
                
                ax.set_zlim(offset, Z.max())
            
            plt.tight_layout()
            plt.show()
            self.update_status(f"Plotted function: {func_str}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to plot function:\n{str(e)}")
            self.update_status(f"Error plotting function: {str(e)}")
    
    def plot_data(self):
        if self.data.empty:
            messagebox.showwarning("Warning", "No data to plot")
            return
        
        plt.close('all')
        dim = self.dimension.get()
        data = self.data.dropna(axis=1, how='all').copy()
        
        if dim == 1:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            plt.subplot(2, 1, 1)
            sns.histplot(data.iloc[:, 0], kde=True, color='skyblue')
            plt.title(f'{self.column_names[0]} Distribution')
            plt.xlabel(self.column_names[0])
            plt.ylabel('Frequency')
            sns.rugplot(data.iloc[:, 0], color='red')
            
            plt.subplot(2, 1, 2)
            sns.boxplot(x=data.iloc[:, 0], color='lightgreen')
            plt.xlabel(self.column_names[0])
            plt.title('Box Plot')
            
        elif dim == 2:
            fig, ax = plt.subplots(figsize=(8, 6))
            
            sns.scatterplot(data=data, x=data.columns[0], y=data.columns[1], color='blue', s=100, alpha=0.7)
            plt.title(f'{self.column_names[0]} vs {self.column_names[1]}')
            plt.xlabel(self.column_names[0])
            plt.ylabel(self.column_names[1])
            
            if len(data) > 1:
                sns.regplot(data=data, x=data.columns[0], y=data.columns[1], scatter=False, color='red')
                
                corr = data.corr().iloc[0, 1]
                plt.text(0.05, 0.95, f'ρ = {corr:.3f}', transform=ax.transAxes,
                         bbox=dict(facecolor='white', alpha=0.8))
            
            plt.grid(True, linestyle='--', alpha=0.6)
            
        elif dim == 3:
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            sc = ax.scatter(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2], 
                           c=data.iloc[:, 2], cmap='viridis', marker='o', s=100)
            
            cbar = fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
            cbar.set_label(self.column_names[2])
            
            ax.set_title(f'{self.column_names[0]} vs {self.column_names[1]} vs {self.column_names[2]}')
            ax.set_xlabel(self.column_names[0])
            ax.set_ylabel(self.column_names[1])
            ax.set_zlabel(self.column_names[2])
            
            ax.grid(True, linestyle='--', alpha=0.6)
        
        plt.tight_layout()
        plt.show()
        self.update_status(f"Plotted {dim}D data")
    
    def show_stats(self):
        if self.data.empty:
            messagebox.showwarning("Warning", "No data to analyze")
            return
        
        dim = self.dimension.get()
        stats_data = self.data.dropna(axis=1, how='all').copy()
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        self.stats_text.insert(tk.END, "Descriptive Statistics:\n")
        self.stats_text.insert(tk.END, stats_data.describe().to_string())
        self.stats_text.insert(tk.END, "\n\n")
        
        if dim >= 2:
            self.stats_text.insert(tk.END, "Correlation Matrix:\n")
            self.stats_text.insert(tk.END, stats_data.corr().to_string())
            self.stats_text.insert(tk.END, "\n\n")
            
            if dim == 2 and len(stats_data) > 1:
                slope, intercept, r_value, p_value, std_err = linregress(
                    stats_data.iloc[:, 0], stats_data.iloc[:, 1]
                )
                self.stats_text.insert(tk.END, "Linear Regression:\n")
                self.stats_text.insert(tk.END, f"Slope: {slope:.4f}\n")
                self.stats_text.insert(tk.END, f"Intercept: {intercept:.4f}\n")
                self.stats_text.insert(tk.END, f"R-squared: {r_value**2:.4f}\n")
                self.stats_text.insert(tk.END, f"P-value: {p_value:.4f}\n")
                self.stats_text.insert(tk.END, f"Standard Error: {std_err:.4f}\n")
        
        self.stats_text.config(state=tk.DISABLED)
        self.update_status("Calculated statistics")
    
    def save_to_pdf(self):
        if self.data.empty:
            messagebox.showwarning("Warning", "No data to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report"
        )
        
        if not file_path:
            return
        
        try:
            temp_dir = os.path.join(os.path.dirname(file_path), "temp_report")
            os.makedirs(temp_dir, exist_ok=True)
            
            dim = self.dimension.get()
            data = self.data.dropna(axis=1, how='all').copy()
            
            fig = plt.figure(figsize=(8, 6))
            if dim == 1:
                plt.subplot(2, 1, 1)
                sns.histplot(data.iloc[:, 0], kde=True, color='skyblue')
                plt.title(f'{self.column_names[0]} Distribution')
                plt.xlabel(self.column_names[0])
                plt.ylabel('Frequency')
                sns.rugplot(data.iloc[:, 0], color='red')
                
                plt.subplot(2, 1, 2)
                sns.boxplot(x=data.iloc[:, 0], color='lightgreen')
                plt.xlabel(self.column_names[0])
                plt.title('Box Plot')
                
            elif dim == 2:
                ax = fig.add_subplot(111)
                sns.scatterplot(data=data, x=data.columns[0], y=data.columns[1], color='blue', s=100, alpha=0.7)
                plt.title(f'{self.column_names[0]} vs {self.column_names[1]}')
                plt.xlabel(self.column_names[0])
                plt.ylabel(self.column_names[1])
                if len(data) > 1:
                    sns.regplot(data=data, x=data.columns[0], y=data.columns[1], scatter=False, color='red')
                plt.grid(True, linestyle='--', alpha=0.6)
                
            elif dim == 3:
                ax = fig.add_subplot(111, projection='3d')
                sc = ax.scatter(data.iloc[:, 0], data.iloc[:, 1], data.iloc[:, 2], 
                               c=data.iloc[:, 2], cmap='viridis', marker='o', s=100)
                cbar = fig.colorbar(sc, ax=ax, shrink=0.5, aspect=5)
                cbar.set_label(self.column_names[2])
                ax.set_title(f'{self.column_names[0]} vs {self.column_names[1]} vs {self.column_names[2]}')
                ax.set_xlabel(self.column_names[0])
                ax.set_ylabel(self.column_names[1])
                ax.set_zlabel(self.column_names[2])
                ax.grid(True, linestyle='--', alpha=0.6)
            
            plot_path = os.path.join(temp_dir, "plot.png")
            fig.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            
            stats_path = os.path.join(temp_dir, "stats.txt")
            self.stats_text.config(state=tk.NORMAL)
            with open(stats_path, 'w') as f:
                f.write(self.stats_text.get(1.0, tk.END))
            self.stats_text.config(state=tk.DISABLED)
            
            data_path = os.path.join(temp_dir, "data.csv")
            self.data.to_csv(data_path, index=False)
            
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font("Arial", 'B', 16)
            pdf.set_text_color(0, 102, 204)
            pdf.cell(0, 10, " Data Summarization", 0, 1, 'C')
            
            pdf.set_font("Arial", 'I', 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
            pdf.cell(0, 10, f"Data Dimension: {self.dimension.get()}D", 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font("Arial", 'B', 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, "Data Visualization:", 0, 1)
            pdf.image(plot_path, x=30, w=150)
            pdf.ln(10)
            
            pdf.cell(0, 10, "Statistical Summary:", 0, 1)
            pdf.set_font("Courier", '', 10)
            with open(stats_path, 'r') as f:
                for line in f:
                    pdf.cell(0, 5, line.strip(), 0, 1)
            
            pdf.ln(10)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "Data Table:", 0, 1)
            
            pdf.set_fill_color(220, 230, 242)
            pdf.set_font("Arial", 'B', 10)
            for col in self.data.columns:
                pdf.cell(40, 10, col, 1, 0, 'C', 1)
            pdf.ln()
            
            pdf.set_font("Arial", '', 10)
            fill = False
            for _, row in self.data.iterrows():
                pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
                for col in self.data.columns:
                    val = row[col]
                    pdf.cell(40, 10, f"{val:.4f}" if not np.isnan(val) else "N/A", 1, 0, 'C', fill)
                pdf.ln()
                fill = not fill
            
            pdf.ln(10)
            pdf.set_font("Arial", 'I', 8)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 10, " ", 0, 0, 'C')
            
            pdf.output(file_path)
            
            import shutil
            shutil.rmtree(temp_dir)
            
            messagebox.showinfo("Success", f"Report saved successfully:\n{file_path}")
            self.update_status("Report saved to PDF")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.after(3000, lambda: self.status_bar.config(text="Ready"))

