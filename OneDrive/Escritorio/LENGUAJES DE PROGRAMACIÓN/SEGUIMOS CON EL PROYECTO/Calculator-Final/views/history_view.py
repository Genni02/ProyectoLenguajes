import tkinter as tk
from tkinter import messagebox
import datetime
from utils.styles import get_colors

class HistoryView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.setup_fonts()
        self.cards_per_row = 3  # Valor por defecto
        
    def setup_fonts(self):
        """Configura las fuentes para la vista de historial"""
        self.title_font = ("Arial", 16, "bold")
        self.entry_font = ("Courier", 9)
        self.result_font = ("Courier", 9, "bold")
        self.timestamp_font = ("Arial", 7)
        self.button_font = ("Arial", 7)
        
    def show(self):
        """Muestra el historial de cálculos"""
        self.clear_view()
        
        # Frame principal
        main_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(
            main_frame,
            text="📜 Historial de Cálculos",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=(0, 15))
        
        # Contenedor con scroll
        self.setup_scrollable_frame(main_frame)
        
        # Botón limpiar
        self.create_clear_button(main_frame)
        
        # Configurar evento de redimensionamiento
        self.parent_frame.bind("<Configure>", self.on_window_resize)
        
    def clear_view(self):
        """Limpia completamente la vista"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
    
    def setup_scrollable_frame(self, parent):
        """Configura el área desplazable del historial"""
        # Frame contenedor
        container = tk.Frame(parent, bg=self.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas y scrollbar
        self.canvas = tk.Canvas(
            container,
            bg=self.colors['bg'],
            highlightthickness=0,
            yscrollincrement=10
        )
        
        scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=self.colors['bg']
        )
        
        # Configurar scroll
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Empaquetado
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mostrar elementos del historial
        self.display_history_items()
    
    def on_window_resize(self, event=None):
        """Maneja el redimensionamiento de la ventana para hacer responsive el grid"""
        if hasattr(self, 'canvas'):
            # Calcular cuántas tarjetas caben por fila
            canvas_width = self.canvas.winfo_width()
            card_min_width = 300  # Ancho mínimo de cada tarjeta
            new_cards_per_row = max(1, canvas_width // card_min_width)
            
            # Solo redibujar si cambió el número de tarjetas por fila
            if new_cards_per_row != self.cards_per_row:
                self.cards_per_row = new_cards_per_row
                self.display_history_items()
    
    def display_history_items(self):
        """Muestra los elementos del historial en grid responsivo"""
        # Limpiar frame por si acaso
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Verificar que no haya elementos vacíos o duplicados
        seen = set()
        filtered_history = []
        
        for entry in self.app.history:
            if entry and 'expression' in entry and 'result' in entry:
                # Crear una clave única para detectar duplicados
                key = (entry['expression'], entry['result'])
                if key not in seen:
                    seen.add(key)
                    filtered_history.append(entry)
        
        if not filtered_history:
            # Mostrar mensaje cuando no hay historial
            tk.Label(
                self.scrollable_frame,
                text="No hay cálculos en el historial",
                font=("Arial", 12),
                bg=self.colors['bg'],
                fg="gray"
            ).pack(pady=50)
            return
        
        # Crear grid responsivo
        self.create_responsive_grid(filtered_history)
    
    def create_responsive_grid(self, entries):
        """Crea un grid responsivo con las entradas del historial"""
        # Mostrar en orden inverso (más reciente primero)
        reversed_entries = list(reversed(entries))
        
        # Crear filas según el número de tarjetas por fila
        for row_idx in range(0, len(reversed_entries), self.cards_per_row):
            # Frame para esta fila
            row_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
            row_frame.pack(fill=tk.X, pady=5)
            
            # Agregar tarjetas a esta fila
            for col_idx in range(self.cards_per_row):
                entry_idx = row_idx + col_idx
                if entry_idx < len(reversed_entries):
                    entry = reversed_entries[entry_idx]
                    self.create_history_card_grid(row_frame, entry, entry_idx, col_idx)
    
    def create_history_card_grid(self, parent, entry, index, column):
        """Crea una tarjeta para una entrada del historial en formato grid"""
        card_width = max(280, (self.canvas.winfo_width() // self.cards_per_row) - 20)
        card_frame = tk.Frame(
            parent,
            bg=self.colors['display'],
            relief=tk.RAISED,
            bd=2,
            width=card_width,
            height=180
        )
        card_frame.pack(side=tk.LEFT, padx=5, pady=2, fill=tk.BOTH, expand=True)
        card_frame.pack_propagate(False)
        card_frame.card_id = f"hist_{index}_{entry['timestamp']}"

        # Contenido de la tarjeta
        self.create_card_content_compact(card_frame, entry)

        # Menú de acciones (dropdown)
        self.create_dropdown_menu(card_frame, entry)
    
    def create_card_content_compact(self, parent, entry):
        """Crea el contenido informativo de la tarjeta en formato compacto"""
        content_frame = tk.Frame(parent, bg=self.colors['display'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=5)
        
        # Expresión (truncada si es muy larga)
        expression_text = entry['expression']
        if len(expression_text) > 35:
            expression_text = expression_text[:32] + "..."
            
        tk.Label(
            content_frame,
            text=f"📝 {expression_text}",
            font=self.entry_font,
            bg=self.colors['display'],
            fg=self.colors['text'],
            anchor="w",
            wraplength=250,
            justify=tk.LEFT
        ).pack(fill=tk.X, pady=(0, 3))
        
        # Resultado (truncado si es muy largo)
        result_text = str(entry['result'])
        if len(result_text) > 25:
            result_text = result_text[:22] + "..."
            
        tk.Label(
            content_frame,
            text=f"💡 {result_text}",
            font=self.result_font,
            bg=self.colors['display'],
            fg=self.colors['text'],
            anchor="w",
            wraplength=250,
            justify=tk.LEFT
        ).pack(fill=tk.X, pady=(0, 3))
        
        # Fecha
        timestamp = datetime.datetime.fromisoformat(entry['timestamp'])
        tk.Label(
            content_frame,
            text=f"🕒 {timestamp.strftime('%d/%m %H:%M')}",
            font=self.timestamp_font,
            bg=self.colors['display'],
            fg="gray",
            anchor="w"
        ).pack(fill=tk.X)
    
    """ def create_action_buttons_compact(self, parent, entry):
        Crea los botones de acción para la tarjeta en formato compacto
        button_frame = tk.Frame(parent, bg=self.colors['display'])
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=(0, 5))
        
        # Botones más pequeños para el grid
        buttons = [
            ("💾", lambda e=entry: self.save_from_history(e), self.colors['operator']),
            ("⎘", lambda e=entry: self.copy_entry(e), self.colors['primary_light']),
            ("🗑️", lambda e=entry: self.delete_entry(e), "#dc3545"),  # Rojo para eliminar
            ("➡️ Usar", lambda e=entry: self.use_expression(e), self.colors['primary'])  # Nuevo botón
        ]
        
        for text, command, color in buttons:
            tk.Button(
                button_frame,
                text=text,
                font=("Arial", 8),
                bg=color,
                fg="white",
                relief=tk.FLAT,
                width=5 if "Usar" in text else 3,
                height=1,
                command=command
            ).pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X) """
    
    def create_dropdown_menu(self, parent, entry):
        """Crea un menú desplegable de acciones en la esquina superior derecha"""
        # Colores
        menu_btn_bg = self.colors['display']
        menu_btn_hover = self.colors['primary_light']
        menu_fg = self.colors['text']
        menu_bg = self.colors['display']

        def on_enter_btn(e):
            menu_button.config(bg=menu_btn_hover, fg="white", cursor="hand2")

        def on_leave_btn(e):
            menu_button.config(bg=menu_btn_bg, fg=menu_fg)

        # Botón de tres puntos verticales, circular y pequeño
        menu_button = tk.Menubutton(
            parent,
            text="⋮",
            font=("Arial", 13, "bold"),
            bg=menu_btn_bg,
            fg=menu_fg,
            relief=tk.FLAT,
            activebackground=menu_btn_hover,
            activeforeground="white",
            borderwidth=0,
            highlightthickness=0,
            width=2,
            height=1,
            direction="below"
        )
        menu_button.place(relx=1.0, y=8, anchor="ne", width=32, height=32)
        menu_button.bind("<Enter>", on_enter_btn)
        menu_button.bind("<Leave>", on_leave_btn)

        # Menú de opciones personalizado (solo colores generales)
        menu = tk.Menu(
            menu_button,
            tearoff=0,
            bg=menu_bg,
            fg=menu_fg,
            activebackground=self.colors['primary_light'],
            activeforeground="white",
            bd=1,
            relief=tk.SOLID
        )

        # Opciones del menú (sin background ni foreground por ítem)
        menu.add_command(
            label="Usar en calculadora",
            command=lambda e=entry: self.use_expression(e)
        )
        menu.add_command(
            label="Guardar",
            command=lambda e=entry: self.save_from_history(e)
        )
        menu.add_command(
            label="Copiar",
            command=lambda e=entry: self.copy_entry(e)
        )
        menu.add_separator()
        menu.add_command(
            label="Eliminar",
            command=lambda e=entry: self.delete_entry(e)
        )

        menu_button.config(menu=menu)
    
    def create_clear_button(self, parent):
        """Crea el botón para limpiar el historial"""
        tk.Button(
            parent,
            text="🗑️ Limpiar Historial",
            font=("Arial", 10),
            bg=self.colors['operator'],
            fg="white",
            relief=tk.FLAT,
            command=self.clear_history
        ).pack(pady=(15, 5))
    
    def delete_entry(self, entry):
        """Elimina una entrada específica del historial"""
        if messagebox.askyesno(
            "Eliminar Cálculo",
            f"¿Estás seguro de que deseas eliminar este cálculo?\n\n"
            f"Expresión: {entry['expression']}\n"
            f"Resultado: {entry['result']}",
            icon="warning"
        ):
            success, message = self.app.history_controller.delete_entry(entry)
            
            if success:
                messagebox.showinfo("Eliminado", message)
                # Actualizar la vista
                self.display_history_items()
            else:
                messagebox.showerror("Error", message)
    
    def use_expression(self, entry):
        """Usa la expresión seleccionada en la calculadora"""
        self.app.history_controller.use_expression_in_calculator(entry['expression'])
    
    def clear_history(self):
        """Limpia todo el historial usando el controller"""
        success, message = self.app.history_controller.clear_history()
        
        if success:
            messagebox.showinfo("Historial Limpiado", message)
            # Actualizar la vista
            self.display_history_items()
        elif message != "Operación cancelada":
            messagebox.showerror("Error", message)
    
    def save_from_history(self, entry):
        """Guarda una entrada del historial"""
        # Verificar si ya está guardado en saved_operations
        is_already_saved = any(
            saved_op.get('expression') == entry['expression'] and 
            saved_op.get('result') == entry['result'] and
            saved_op.get('timestamp') == entry['timestamp']
            for saved_op in self.app.saved_operations
        )
        
        if is_already_saved:
            messagebox.showinfo(
                "Ya guardado",
                "Esta operación ya está en operaciones guardadas"
            )
            return
        
        title = f"Historial_{len(self.app.saved_operations) + 1}"
        self.app.saved_operations.append({
            'title': title,
            'expression': entry['expression'],
            'result': entry['result'],
            'timestamp': entry['timestamp']
        })
        messagebox.showinfo(
            "Guardado",
            "La operación se ha guardado correctamente"
        )

    def copy_entry(self, entry):
        """Copia una entrada al portapapeles"""
        text_to_copy = f"Expresión: {entry['expression']}\nResultado: {entry['result']}"
        self.parent_frame.clipboard_clear()
        self.parent_frame.clipboard_append(text_to_copy)
        messagebox.showinfo(
            "Copiado",
            "El contenido se ha copiado al portapapeles"
        )