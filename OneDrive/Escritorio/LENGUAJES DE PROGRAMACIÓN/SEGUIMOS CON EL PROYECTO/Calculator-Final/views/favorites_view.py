import tkinter as tk
from tkinter import messagebox
import datetime
from utils.styles import get_colors

class FavoritesView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.fav_controller = self.app.favorites_controller

    def show(self):
        """Muestra los favoritos"""
        for widget in self.parent_frame.winfo_children():
            widget.destroy()  # Limpiar vista antes de mostrar

        tk.Label(
            self.parent_frame,
            text="⭐ Favoritos",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        ).pack(pady=10)

        favorites = self.fav_controller.get_favorite_operations()
        if not favorites:
            tk.Label(
                self.parent_frame,
                text="No hay favoritos guardados",
                font=("Arial", 12),
                bg=self.colors['bg'],
                fg="gray"
            ).pack(pady=20)
            return

        # Lista de favoritos con scroll
        fav_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        fav_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        canvas = tk.Canvas(fav_frame, bg=self.colors['bg'])
        scrollbar = tk.Scrollbar(fav_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for fav in favorites:
            self.create_favorite_card(scrollable_frame, fav)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_favorite_card(self, parent, favorite):
        """Crea una tarjeta para un favorito"""
        card_frame = tk.Frame(
            parent, 
            bg=self.colors['display'],
            relief=tk.RAISED,
            bd=1
        )
        card_frame.pack(fill=tk.X, pady=5, padx=5)

        info_frame = tk.Frame(card_frame, bg=self.colors['display'])
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        if 'titulo' in favorite:
            tk.Label(
                info_frame,
                text=f"Título: {favorite['titulo']}",
                font=("Courier", 10, "bold"),
                bg=self.colors['display'],
                fg=self.colors['text_dark'],
                anchor="w"
            ).pack(fill=tk.X)

        tk.Label(
            info_frame,
            text=f"Expresión: {favorite.get('operacion', favorite.get('expression', ''))}",
            font=("Courier", 10),
            bg=self.colors['display'],
            fg=self.colors['text'],
            anchor="w"
        ).pack(fill=tk.X)

        tk.Label(
            info_frame,
            text=f"Resultado: {favorite.get('descripcion', favorite.get('result', ''))}",
            font=("Courier", 10),
            bg=self.colors['display'],
            fg=self.colors['text'],
            anchor="w"
        ).pack(fill=tk.X)

        fecha = favorite.get('fecha') or favorite.get('fecha_agregado')
        if fecha:
            fecha_str = fecha.split('T')[0] if isinstance(fecha, str) else str(fecha)
            tk.Label(
                info_frame,
                text=f"Fecha: {fecha_str}",
                font=("Arial", 8),
                bg=self.colors['display'],
                fg="gray",
                anchor="w"
            ).pack(fill=tk.X)

        button_frame = tk.Frame(card_frame, bg=self.colors['display'])
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Soporta ambos posibles nombres de ID
        operation_id = favorite.get('id') or favorite.get('id_operacion')

        # Botón USAR
        tk.Button(
            button_frame,
            text="Usar",
            font=("Arial", 8),
            bg=self.colors['equals'],
            fg="white",
            relief=tk.FLAT,
            command=lambda fav=favorite: self.use_favorite(fav)
        ).pack(side=tk.LEFT, padx=2)

        # Botón QUITAR DE FAVORITOS
        tk.Button(
            button_frame,
            text="🗑️ Quitar de Favoritos",
            font=("Arial", 8),
            bg=self.colors['operator'],
            fg="white",
            relief=tk.FLAT,
            command=lambda: self.toggle_favorite(operation_id, favorite)
        ).pack(side=tk.LEFT, padx=2)

    def toggle_favorite(self, operation_id, favorite):
        """Alterna el estado de favorito usando el controlador"""
        if messagebox.askyesno("Confirmación", "¿Quitar de favoritos?"):
            self.fav_controller.toggle_favorite(operation_id, favorite)
            self.show()

    def use_favorite(self, favorite):
        """Coloca la operación y resultado en el input principal de la app"""
        # Ajusta esto según cómo tu app maneje el input principal
        if hasattr(self.app, "set_expression_from_favorite"):
            self.app.set_expression_from_favorite(
                favorite.get('operacion', favorite.get('expression', '')),
                favorite.get('descripcion', favorite.get('result', ''))
            )
        else:
            # Fallback: muestra un mensaje
            messagebox.showinfo(
                "Usar favorito",
                f"Expresión: {favorite.get('operacion', favorite.get('expression', ''))}\n"
                f"Resultado: {favorite.get('descripcion', favorite.get('result', ''))}"
            )