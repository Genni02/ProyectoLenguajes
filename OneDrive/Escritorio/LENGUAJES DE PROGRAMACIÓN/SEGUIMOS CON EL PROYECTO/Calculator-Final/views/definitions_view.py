import tkinter as tk
from tkinter import ttk, messagebox
from utils.styles import get_colors
from models import VariableUsuario, FuncionPersonalizada
from typing import List, Optional

class DefinitionsView:
    def __init__(self, app, parent_frame, controller):
        self.app = app
        self.parent_frame = parent_frame
        self.controller = controller
        self.colors = get_colors()
        
        # Variables de control
        self.selected_variable: Optional[VariableUsuario] = None
        self.selected_function: Optional[FuncionPersonalizada] = None
        
        # Referencias a widgets
        self.var_tree = None
        self.func_tree = None
        self.var_name_entry = None
        self.var_value_entry = None
        self.var_desc_entry = None
        self.func_name_entry = None
        self.func_def_entry = None
        self.func_params_entry = None
        self.func_desc_entry = None
        
        # Botones de edición
        self.var_edit_btn = None
        self.var_delete_btn = None
        self.func_edit_btn = None
        self.func_delete_btn = None
        
    def show(self):
        """Muestra el gestor de definiciones"""
        # Limpiar vista anterior
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Header con información del usuario
        self.create_header()
        
        # Notebook para variables y funciones
        notebook = ttk.Notebook(self.parent_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña Variables
        var_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(var_frame, text="🧮 Variables")
        self.create_variables_tab(var_frame)
        
        # Pestaña Funciones
        func_frame = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(func_frame, text="📐 Funciones")
        self.create_functions_tab(func_frame)
    
    def create_header(self):
        """Crea el header con información del contexto"""
        header_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            header_frame,
            text="🧠 Gestor de Definiciones",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(side=tk.LEFT, padx=10)

    def create_variables_tab(self, parent):
        """Crea la pestaña de variables"""
        # Frame para agregar/editar variable
        add_frame = tk.Frame(parent, bg=self.colors['bg'])
        add_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Primera fila: Nombre y Valor
        row1 = tk.Frame(add_frame, bg=self.colors['bg'])
        row1.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row1,
            text="Nombre:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.var_name_entry = tk.Entry(row1, width=15)
        self.var_name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row1,
            text="Valor:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=8,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.var_value_entry = tk.Entry(row1, width=15)
        self.var_value_entry.pack(side=tk.LEFT, padx=5)
        
        # Segunda fila: Descripción
        row2 = tk.Frame(add_frame, bg=self.colors['bg'])
        row2.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row2,
            text="Descripción:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.var_desc_entry = tk.Entry(row2, width=40)
        self.var_desc_entry.pack(side=tk.LEFT, padx=5)
        
        # Tercera fila: Botones
        row3 = tk.Frame(add_frame, bg=self.colors['bg'])
        row3.pack(fill=tk.X, pady=5)
        
        tk.Button(
            row3,
            text="➕ Agregar",
            bg=self.colors['operator'],
            fg="white",
            command=self.add_variable,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        self.var_edit_btn = tk.Button(
            row3,
            text="✏️ Editar",
            bg=self.colors['primary_light'],
            fg="white",
            command=self.edit_variable,
            width=10,
            state=tk.DISABLED
        )
        self.var_edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.var_delete_btn = tk.Button(
            row3,
            text="🗑️ Eliminar",
            bg="#dc3545",
            fg="white",
            command=self.delete_variable,
            width=10,
            state=tk.DISABLED
        )
        self.var_delete_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            row3,
            text="🧹 Limpiar",
            bg=self.colors['clear'],
            fg="white",
            command=self.clear_variable_form,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Lista de variables
        var_list_frame = tk.Frame(parent, bg=self.colors['bg'])
        var_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar para la tabla
        tree_frame = tk.Frame(var_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_v = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_h = tk.Scrollbar(tree_frame, orient="horizontal")
        
        self.var_tree = ttk.Treeview(
            tree_frame, 
            columns=('name', 'value', 'description'), 
            show='headings',
            yscrollcommand=scrollbar_v.set,
            xscrollcommand=scrollbar_h.set
        )
        
        self.var_tree.heading('name', text='Nombre')
        self.var_tree.heading('value', text='Valor')
        self.var_tree.heading('description', text='Descripción')
        
        self.var_tree.column('name', width=120)
        self.var_tree.column('value', width=100)
        self.var_tree.column('description', width=250)
        
        scrollbar_v.config(command=self.var_tree.yview)
        scrollbar_h.config(command=self.var_tree.xview)
        
        # Configurar grid
        self.var_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para selección
        self.var_tree.bind('<<TreeviewSelect>>', self.on_variable_select)
        
    def create_functions_tab(self, parent):
        """Crea la pestaña de funciones con funcionalidad completa"""
        # Frame para agregar/editar función
        add_frame = tk.Frame(parent, bg=self.colors['bg'])
        add_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # Primera fila: Nombre y Definición
        row1 = tk.Frame(add_frame, bg=self.colors['bg'])
        row1.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row1,
            text="Nombre:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.func_name_entry = tk.Entry(row1, width=15)
        self.func_name_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row1,
            text="Definición:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(10, 5))
        
        self.func_def_entry = tk.Entry(row1, width=25)
        self.func_def_entry.pack(side=tk.LEFT, padx=5)
        
        # Segunda fila: Parámetros
        row2 = tk.Frame(add_frame, bg=self.colors['bg'])
        row2.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row2,
            text="Parámetros:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.func_params_entry = tk.Entry(row2, width=20)
        self.func_params_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            row2,
            text="(ej: x,y)",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            font=("Arial", 8)
        ).pack(side=tk.LEFT, padx=5)
        
        # Tercera fila: Descripción
        row3 = tk.Frame(add_frame, bg=self.colors['bg'])
        row3.pack(fill=tk.X, pady=2)
        
        tk.Label(
            row3,
            text="Descripción:",
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            width=10,
            anchor='e'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.func_desc_entry = tk.Entry(row3, width=50)
        self.func_desc_entry.pack(side=tk.LEFT, padx=5)
        
        # Cuarta fila: Botones
        row4 = tk.Frame(add_frame, bg=self.colors['bg'])
        row4.pack(fill=tk.X, pady=5)
        
        tk.Button(
            row4,
            text="➕ Agregar",
            bg=self.colors['operator'],
            fg="white",
            command=self.add_function,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        self.func_edit_btn = tk.Button(
            row4,
            text="✏️ Editar",
            bg=self.colors['primary_light'],
            fg="white",
            command=self.edit_function,
            width=10,
            state=tk.DISABLED
        )
        self.func_edit_btn.pack(side=tk.LEFT, padx=5)
        
        self.func_delete_btn = tk.Button(
            row4,
            text="🗑️ Eliminar",
            bg="#dc3545",
            fg="white",
            command=self.delete_function,
            width=10,
            state=tk.DISABLED
        )
        self.func_delete_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            row4,
            text="🧹 Limpiar",
            bg=self.colors['clear'],
            fg="white",
            command=self.clear_function_form,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Lista de funciones
        func_list_frame = tk.Frame(parent, bg=self.colors['bg'])
        func_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tree_frame = tk.Frame(func_list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar_v = tk.Scrollbar(tree_frame, orient="vertical")
        scrollbar_h = tk.Scrollbar(tree_frame, orient="horizontal")
        
        self.func_tree = ttk.Treeview(
            tree_frame, 
            columns=('name', 'definition', 'parameters', 'description'), 
            show='headings',
            yscrollcommand=scrollbar_v.set,
            xscrollcommand=scrollbar_h.set
        )
        
        self.func_tree.heading('name', text='Nombre')
        self.func_tree.heading('definition', text='Definición')
        self.func_tree.heading('parameters', text='Parámetros')
        self.func_tree.heading('description', text='Descripción')
        
        self.func_tree.column('name', width=100)
        self.func_tree.column('definition', width=150)
        self.func_tree.column('parameters', width=100)
        self.func_tree.column('description', width=200)
        
        scrollbar_v.config(command=self.func_tree.yview)
        scrollbar_h.config(command=self.func_tree.xview)
        
        self.func_tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para selección
        self.func_tree.bind('<<TreeviewSelect>>', self.on_function_select)
    
    def on_variable_select(self, event):
        """Maneja la selección de una variable en la tabla"""
        selection = self.var_tree.selection()
        if selection:
            item = self.var_tree.item(selection[0])
            values = item['values']
            
            # Buscar la variable correspondiente
            if hasattr(self, 'variables_list'):
                for var in self.variables_list:
                    if var.nombre_variable == values[0]:
                        self.selected_variable = var
                        break
            else:
                # Crear objeto temporal para usuarios anónimos
                self.selected_variable = VariableUsuario(0, values[0], values[1])
                self.selected_variable.descripcion = values[2] if len(values) > 2 else None
            
            # Llenar el formulario con los datos
            self.var_name_entry.delete(0, tk.END)
            self.var_name_entry.insert(0, values[0])
            
            self.var_value_entry.delete(0, tk.END)
            self.var_value_entry.insert(0, values[1])
            
            self.var_desc_entry.delete(0, tk.END)
            if len(values) > 2 and values[2]:
                self.var_desc_entry.insert(0, values[2])
            
            # Habilitar botones de edición
            self.var_edit_btn.config(state=tk.NORMAL)
            self.var_delete_btn.config(state=tk.NORMAL)
    
    def on_function_select(self, event):
        """Maneja la selección de una función en la tabla"""
        selection = self.func_tree.selection()
        if selection:
            item = self.func_tree.item(selection[0])
            values = item['values']
            
            # Buscar la función correspondiente
            if hasattr(self, 'functions_list'):
                for func in self.functions_list:
                    if func.nombre_funcion == values[0]:
                        self.selected_function = func
                        break
            else:
                # Crear objeto temporal para usuarios anónimos
                self.selected_function = FuncionPersonalizada(0, values[0], values[1])
                self.selected_function.parametros_funcion = values[2] if len(values) > 2 else None
                self.selected_function.descripcion = values[3] if len(values) > 3 else None
            
            # Llenar el formulario con los datos
            self.func_name_entry.delete(0, tk.END)
            self.func_name_entry.insert(0, values[0])
            
            self.func_def_entry.delete(0, tk.END)
            self.func_def_entry.insert(0, values[1])
            
            self.func_params_entry.delete(0, tk.END)
            if len(values) > 2 and values[2]:
                self.func_params_entry.insert(0, values[2])
            
            self.func_desc_entry.delete(0, tk.END)
            if len(values) > 3 and values[3]:
                self.func_desc_entry.insert(0, values[3])
            
            # Habilitar botones de edición
            self.func_edit_btn.config(state=tk.NORMAL)
            self.func_delete_btn.config(state=tk.NORMAL)
    
    def add_variable(self):
        """Agrega una nueva variable"""
        name = self.var_name_entry.get().strip()
        value = self.var_value_entry.get().strip()
        description = self.var_desc_entry.get().strip()
        
        if self.controller.create_variable(name, value, description):
            self.clear_variable_form()
    
    def edit_variable(self):
        """Edita la variable seleccionada"""
        if not self.selected_variable:
            messagebox.showerror("Error", "No hay variable seleccionada")
            return
        
        name = self.var_name_entry.get().strip()
        value = self.var_value_entry.get().strip()
        description = self.var_desc_entry.get().strip()
        
        if self.controller.update_variable(self.selected_variable, name, value, description):
            self.clear_variable_form()
    
    def delete_variable(self):
        """Elimina la variable seleccionada"""
        if not self.selected_variable:
            messagebox.showerror("Error", "No hay variable seleccionada")
            return
        
        if self.controller.delete_variable(self.selected_variable):
            self.clear_variable_form()
    
    def add_function(self):
        """Agrega una nueva función"""
        name = self.func_name_entry.get().strip()
        definition = self.func_def_entry.get().strip()
        parameters = self.func_params_entry.get().strip()
        description = self.func_desc_entry.get().strip()
        
        if self.controller.create_function(name, definition, parameters, description):
            self.clear_function_form()
    
    def edit_function(self):
        """Edita la función seleccionada"""
        if not self.selected_function:
            messagebox.showerror("Error", "No hay función seleccionada")
            return
        
        name = self.func_name_entry.get().strip()
        definition = self.func_def_entry.get().strip()
        parameters = self.func_params_entry.get().strip()
        description = self.func_desc_entry.get().strip()
        
        if self.controller.update_function(self.selected_function, name, definition, parameters, description):
            self.clear_function_form()
    
    def delete_function(self):
        """Elimina la función seleccionada"""
        if not self.selected_function:
            messagebox.showerror("Error", "No hay función seleccionada")
            return
        
        if self.controller.delete_function(self.selected_function):
            self.clear_function_form()
    
    def clear_variable_form(self):
        """Limpia el formulario de variables"""
        self.var_name_entry.delete(0, tk.END)
        self.var_value_entry.delete(0, tk.END)
        self.var_desc_entry.delete(0, tk.END)
        self.selected_variable = None
        self.var_edit_btn.config(state=tk.DISABLED)
        self.var_delete_btn.config(state=tk.DISABLED)
        if self.var_tree.selection():
            self.var_tree.selection_remove(self.var_tree.selection())
    
    def clear_function_form(self):
        """Limpia el formulario de funciones"""
        self.func_name_entry.delete(0, tk.END)
        self.func_def_entry.delete(0, tk.END)
        self.func_params_entry.delete(0, tk.END)
        self.func_desc_entry.delete(0, tk.END)
        self.selected_function = None
        self.func_edit_btn.config(state=tk.DISABLED)
        self.func_delete_btn.config(state=tk.DISABLED)
        if self.func_tree.selection():
            self.func_tree.selection_remove(self.func_tree.selection())
    
    def load_variables(self, variables):
        if not hasattr(self, "var_tree") or not self.var_tree.winfo_exists():
            return  # El widget ya no existe, no hacer nada
        for item in self.var_tree.get_children():
            self.var_tree.delete(item)
        
        # Agregar variables de BD
        for var in variables:
            self.var_tree.insert('', tk.END, values=(
                var.nombre_variable, 
                var.valor_variable, 
                var.descripcion or ""
            ))
        
        # Agregar variables en memoria (para usuarios anónimos o variables de sesión)
        for name, value in self.app.variables.items():
            # Evitar duplicados
            exists = any(var.nombre_variable == name for var in variables)
            if not exists:
                # Para variables de memoria, buscar si tienen descripción en el diccionario de descripciones
                description = getattr(self.app, 'variable_descriptions', {}).get(name, "")
                self.var_tree.insert('', tk.END, values=(name, value, description))
    
    def load_functions(self, functions: List[FuncionPersonalizada]):
        """Carga las funciones en el Treeview"""
        if not hasattr(self, "func_tree") or not self.func_tree.winfo_exists():
            return
        self.functions_list = functions

        for item in self.func_tree.get_children():
            self.func_tree.delete(item)
        
        for func in functions:
            self.func_tree.insert('', tk.END, values=(
                func.nombre_funcion, 
                func.definicion_funcion, 
                func.parametros_funcion or "",
                func.descripcion or ""
            ))
        
        for name, definition in self.app.functions.items():
            exists = any(func.nombre_funcion == name for func in functions)
            if not exists:
                description = getattr(self.app, 'function_descriptions', {}).get(name, "")
                parameters = getattr(self.app, 'function_parameters', {}).get(name, "")
                self.func_tree.insert('', tk.END, values=(name, definition, parameters, description))