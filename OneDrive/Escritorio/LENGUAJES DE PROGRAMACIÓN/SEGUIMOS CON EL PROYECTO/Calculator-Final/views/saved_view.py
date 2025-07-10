import tkinter as tk
from tkinter import messagebox
from utils.styles import get_colors

class SavedOperationsView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.cards_per_row = 3  # Valor por defecto

    def show(self):
        # Limpiar todo
        for w in self.parent_frame.winfo_children():
            w.destroy()

        # Título
        tk.Label(
            self.parent_frame,
            text="💾 Operaciones Guardadas",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=10)

        # Obtener operaciones
        self.ops = self.app.operations_controller.get_all_operations()
        if not self.ops:
            tk.Label(
                self.parent_frame,
                text="No hay operaciones guardadas",
                font=("Arial", 12),
                bg=self.colors['bg'],
                fg="gray"
            ).pack(pady=20)
            # Botón para borrar todo (deshabilitado)
            self.create_clear_button(self.parent_frame, state=tk.DISABLED)
            return

        # --- Scrollable Frame ---
        container = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas = tk.Canvas(container, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Scroll con la rueda del mouse
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Mostrar tarjetas en grid responsivo
        self.display_saved_items()

        # Botón para borrar todo (abajo)
        self.create_clear_button(self.parent_frame)

        # Evento para hacer responsivo el grid
        self.parent_frame.bind("<Configure>", self.on_window_resize)

    def _on_mousewheel(self, event):
        # Para Windows y Linux
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def on_window_resize(self, event=None):
        if hasattr(self, 'canvas'):
            canvas_width = self.canvas.winfo_width()
            card_min_width = 300
            new_cards_per_row = max(1, canvas_width // card_min_width)
            if new_cards_per_row != self.cards_per_row:
                self.cards_per_row = new_cards_per_row
                self.display_saved_items()

    def display_saved_items(self):
        # Limpiar frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        if not hasattr(self, "ops"):
            self.ops = self.app.operations_controller.get_all_operations()
        if not self.ops:
            return
        # Mostrar en orden inverso (más reciente primero)
        reversed_ops = list(reversed(self.ops))
        for row_idx in range(0, len(reversed_ops), self.cards_per_row):
            row_frame = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
            row_frame.pack(fill=tk.X, pady=5)
            for col_idx in range(self.cards_per_row):
                op_idx = row_idx + col_idx
                if op_idx < len(reversed_ops):
                    op = reversed_ops[op_idx]
                    self._create_card(row_frame, op, op_idx)

    def _create_card(self, parent, op, index):
        card_width = max(280, (self.canvas.winfo_width() // self.cards_per_row) - 20)
        cf = tk.Frame(parent, bg="#F3F4F6", relief=tk.RAISED, bd=1, width=card_width, height=170)
        cf.pack(side=tk.LEFT, padx=8, pady=2, fill=tk.BOTH, expand=True)
        cf.pack_propagate(False)

        # Título
        tk.Label(
            cf,
            text=op.get('titulo'),
            font=("Arial", 12, "bold"),
            bg="#F3F4F6",
            fg=self.colors['text']
        ).pack(anchor=tk.W, padx=10, pady=4)

        # Expresión y resultado
        tk.Label(
            cf,
            text=f"Expresión: {op.get('operacion')}",
            font=("Courier", 10),
            bg="#F3F4F6",
            fg=self.colors['text'],
            wraplength=400,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10)
        tk.Label(
            cf,
            text=f"Resultado: {op.get('descripcion')}",
            font=("Courier", 10),
            bg="#F3F4F6",
            fg=self.colors['text'],
            wraplength=400,
            justify=tk.LEFT
        ).pack(anchor=tk.W, padx=10)

        # Tipo, favorito y tags
        info = f"Tipo: {op.get('tipo_operacion', 'expression')}"
        if op.get('favorito'):
            info += "   ⭐ Favorito"
        if op.get('tags'):
            info += "   Tags: " + ", ".join(op.get('tags'))
        tk.Label(
            cf,
            text=info,
            font=("Arial", 9),
            bg="#F3F4F6",
            fg=self.colors['text_dark']
        ).pack(anchor=tk.W, padx=10, pady=2)

        # Botones
        btns = tk.Frame(cf, bg="#F3F4F6")
        btns.pack(anchor=tk.E, pady=5, padx=10)
        tk.Button(
            btns, text="🗑️ Eliminar", font=("Arial", 8),
            bg=self.colors['operator'], fg="white", relief=tk.FLAT,
            command=lambda i=index: self._delete(i)
        ).pack(side=tk.LEFT, padx=4)

        # Determina si es favorito y muestra la estrella correcta
        operation_id = op.get('id') or op.get('id_operacion')
        is_favorite = False
        if hasattr(self.app, "favorites_controller") and hasattr(self.app.favorites_controller, "is_favorite"):
            is_favorite = self.app.favorites_controller.is_favorite(operation_id)
        else:
            is_favorite = op.get('favorito', False)
        star = "★" if is_favorite else "☆"

        tk.Button(
            btns, text=star, font=("Arial", 12),
            bg=self.colors['equals'], fg="white", relief=tk.FLAT,
            command=lambda o=op: self._toggle_fav(o)
        ).pack(side=tk.LEFT, padx=4)

    def _delete(self, idx):
        ops = self.app.operations_controller.get_all_operations()
        op = ops[idx]
        operation_id = op.get('id_operacion') or op.get('id')
        if not messagebox.askyesno("Eliminar", "¿Eliminar esta operación?"):
            return
        self.app.operations_controller.delete_operation(operation_id, idx)
        self.show()

    def create_clear_button(self, parent, state=tk.NORMAL):
        tk.Button(
            parent,
            text="🗑️ Borrar todas las operaciones",
            font=("Arial", 10, "bold"),
            bg=self.colors['operator'],
            fg="white",
            relief=tk.FLAT,
            command=self._delete_all,
            state=state
        ).pack(pady=(10, 15))

    def _delete_all(self):
        if not messagebox.askyesno("Eliminar todo", "¿Eliminar TODAS las operaciones guardadas?"):
            return
        self.app.operations_controller.delete_all_operations()
        self.show()

    def _toggle_fav(self, op):
        operation_id = op.get('id') or op.get('id_operacion')
        if not operation_id:
            messagebox.showerror("Error", "No se encontró el ID de la operación.")
            return

        if hasattr(self.app, "favorites_controller"):
            self.app.favorites_controller.toggle_favorite(operation_id, op)
            messagebox.showinfo("Favorito", "La operación se guardó en favoritos correctamente")
        else:
            op['favorito'] = not op.get('favorito', False)
            messagebox.showinfo("Favorito", "La operación se guardó en favoritos correctamente" if op['favorito'] else "La operación se eliminó de favoritos correctamente")