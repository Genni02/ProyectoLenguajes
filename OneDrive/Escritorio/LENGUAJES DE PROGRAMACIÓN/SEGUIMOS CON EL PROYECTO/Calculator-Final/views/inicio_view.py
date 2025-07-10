import tkinter as tk
from tkinter import ttk
from datetime import datetime
from utils.styles import get_colors

class InicioView:
    def __init__(self, app, parent_frame=None):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.frame = None
        self.range_var = tk.StringVar(value='Día')

    def show(self):
        if self.frame:
            self.frame.destroy()
        parent = self.parent_frame if self.parent_frame else self.app.calc_frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_welcome_section(self.frame)
        self.create_stats_cards(self.frame)

    def create_welcome_section(self, parent):
        welcome_frame = ttk.LabelFrame(parent, text="🎉 ¡Bienvenido a la Calculadora Científica!", padding=20)
        welcome_frame.pack(fill='x', padx=10, pady=10)
        user_name = self.app.current_user.get("name", "Usuario") if self.app.current_user else "Usuario"
        welcome_text = f"""
¡Hola {user_name}! 👋\n\nEsta es tu calculadora científica personal con capacidades avanzadas.\nAquí puedes realizar cálculos complejos, guardar operaciones favoritas,\ngestionar variables personalizadas y mucho más.\n"""
        welcome_label = tk.Label(welcome_frame, text=welcome_text, font=('Arial', 12), justify='left',
                                bg=self.colors['bg'], fg=self.colors['text'])
        welcome_label.pack(anchor='w')

        # Combo para seleccionar rango
        combo_frame = ttk.Frame(welcome_frame)
        combo_frame.pack(anchor='e', pady=(10, 0))
        ttk.Label(combo_frame, text="Ver por:").pack(side='left')
        combo = ttk.Combobox(combo_frame, textvariable=self.range_var, values=['Día', 'Semana', 'Mes'], state='readonly', width=10)
        combo.pack(side='left', padx=5)
        combo.bind('<<ComboboxSelected>>', lambda e: self.update_cards())

    def create_stats_cards(self, parent):
        self.cards_frame = tk.Frame(parent, bg='#f0f4ff')
        self.cards_frame.pack(fill='x', padx=10, pady=10)
        self.update_cards()

    def update_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        # Simulación de datos (reemplazar por consulta real)
        stats = self.get_stats_data(self.range_var.get())
        # Card: Operaciones realizadas
        self.create_card(self.cards_frame, "Operaciones realizadas", stats['operaciones'], 0, '#1976d2')
        # Card: Tiempo total de uso
        self.create_card(self.cards_frame, "Tiempo total de uso", stats['tiempo_uso'], 1, '#43a047')
        # Card: Días con mayor actividad
        self.create_card(self.cards_frame, "Días con mayor actividad", stats['dias_activos'], 2, '#fbc02d')
        # Card: Media de operaciones por sesión
        self.create_card(self.cards_frame, "Promedio de operaciones por sesión", stats['media_sesion'], 3, '#e53935')
        # Card: Top 5 operaciones más utilizadas
        self.create_top5_card(self.cards_frame, stats['top_operaciones'], 4, '#00838f')

    def create_card(self, parent, title, value, col, color):
        card = tk.Frame(parent, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=col, padx=8, pady=5, sticky='nsew')
        tk.Label(card, text=title, font=('Arial', 10, 'bold'), bg=color, fg='white').pack(pady=(8,0))
        tk.Label(card, text=str(value), font=('Arial', 18, 'bold'), bg=color, fg='white').pack(pady=(0,8))
        parent.grid_columnconfigure(col, weight=1)

    def create_top5_card(self, parent, top5, col, color):
        card = tk.Frame(parent, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=col, padx=8, pady=5, sticky='nsew')
        tk.Label(card, text="Top 5 Operaciones", font=('Arial', 10, 'bold'), bg=color, fg='white').pack(pady=(8,0))
        for i, (op, count) in enumerate(top5, 1):
            tk.Label(card, text=f"{i}. {op} ({count})", font=('Arial', 10), bg=color, fg='white').pack(anchor='w')
        parent.grid_columnconfigure(col, weight=1)

    def get_stats_data(self, rango):
        # Aquí deberías consultar la base de datos según el rango seleccionado
        # Estos son datos simulados para mostrar el diseño
        if rango == 'Día':
            return {
                'operaciones': 23,
                'tiempo_uso': '1h 15m',
                'dias_activos': 'Hoy',
                'media_sesion': 7.6,
                'top_operaciones': [('Suma', 10), ('Resta', 5), ('Multiplicación', 3), ('División', 3), ('Potencia', 2)]
            }
        elif rango == 'Semana':
            return {
                'operaciones': 120,
                'tiempo_uso': '6h 40m',
                'dias_activos': 'Lun, Mié, Vie',
                'media_sesion': 8.2,
                'top_operaciones': [('Suma', 40), ('Resta', 25), ('Multiplicación', 20), ('División', 18), ('Potencia', 17)]
            }
        else:  # Mes
            return {
                'operaciones': 480,
                'tiempo_uso': '28h 10m',
                'dias_activos': '10 días activos',
                'media_sesion': 8.9,
                'top_operaciones': [('Suma', 160), ('Resta', 120), ('Multiplicación', 80), ('División', 70), ('Potencia', 50)]
            }
