import tkinter as tk
from tkinter import ttk
from utils.styles import get_colors
from datetime import datetime, timedelta
from collections import defaultdict

class InicioView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.frame = None

    def show(self):
        if self.frame:
            self.frame.destroy()

        self.frame = ttk.Frame(self.parent_frame)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_welcome_message()
        self.create_filter_options()
        self.create_cards()

    def create_welcome_message(self):
        welcome_frame = ttk.LabelFrame(self.frame, text="👋 Bienvenido", padding=20)
        welcome_frame.pack(fill='x', padx=10, pady=10)

        user_name = self.app.current_user.get("name", "Usuario") if self.app.current_user else "Usuario"
        welcome_text = f"Hola {user_name}, esta es tu vista general de actividad en la calculadora."

        label = tk.Label(welcome_frame, text=welcome_text, font=('Arial', 13, 'bold'),
                         bg=self.colors['bg'], fg=self.colors['text'])
        label.pack(anchor='w')

    def create_filter_options(self):
        filter_frame = ttk.LabelFrame(self.frame, text="🗓️ Filtro Temporal", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=10)

        self.filter_var = tk.StringVar(value="mes")
        options = [
            ("Por Día", "dia"),
            ("Por Semana", "semana"),
            ("Por Mes", "mes")
        ]

        for text, value in options:
            rb = ttk.Radiobutton(filter_frame, text=text, variable=self.filter_var, value=value, command=self.update_cards)
            rb.pack(side='left', padx=10)

    def create_cards(self):
        self.cards_frame = tk.Frame(self.frame, bg=self.colors['bg'])
        self.cards_frame.pack(fill='x', padx=10, pady=10)
        self.update_cards()

    def update_cards(self):
     for widget in self.cards_frame.winfo_children():
         widget.destroy()

     stats = self.get_stats()

     filtro = self.filter_var.get()
     if filtro == 'dia':
         titulo_actividad = "Día con más actividad"
     elif filtro == 'semana':
         titulo_actividad = "Semana con más actividad"
     elif filtro == 'mes':
         titulo_actividad = "Mes con más actividad"
     else:
         titulo_actividad = "Día con más actividad"

     self.create_card("Operaciones totales", stats['total_operaciones'], 0, '#1976d2')
     self.create_card("Función más usada", stats['funcion_mas_usada'], 1, '#43a047')
     self.create_card("Promedio por día", f"{stats['promedio_diario']:.1f}", 2, '#fbc02d')
     self.create_card(titulo_actividad, stats['dia_mas_activo'], 3, '#e53935')


    def get_stats(self):
        filtro = self.filter_var.get()
        stats = {}
        stats['total_operaciones'] = self.dashboard.get_total_operaciones(rango=filtro)
        tipo_usado = self.dashboard.get_tipo_calculo_mas_usado()
        stats['funcion_mas_usada'] = tipo_usado['tipo_calculo'] if tipo_usado else 'N/A'
        stats['promedio_diario'] = self.dashboard.get_promedio_diario()
        dia = self.dashboard.get_dia_con_mayor_actividad()
        stats['dia_mas_activo'] = dia['dia'] if dia else 'N/A'
        return stats


    def create_card(self, title, value, column, color):
        card = tk.Frame(self.cards_frame, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=column, padx=8, ipadx=10, ipady=10, sticky='nsew')
        self.cards_frame.grid_columnconfigure(column, weight=1)

        label_title = tk.Label(card, text=title, font=('Arial', 11, 'bold'), bg=color, fg='white')
        label_title.pack(pady=(5, 0), padx=8)

        label_value = tk.Label(card, text=value, font=('Arial', 18, 'bold'), bg=color, fg='white')
        label_value.pack(pady=(0, 8), padx=8)

    def get_stats(self):
        filtro = self.filter_var.get()
        connection = self.app.db_connection.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT tipo_calculo, DATE(timestamp_calculo) as fecha
            FROM historial_calculos
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()

        total_operaciones = len(rows)
        por_dia = defaultdict(int)
        tipo_counter = defaultdict(int)

        for row in rows:
            fecha = row['fecha']
            tipo = row['tipo_calculo']

            if filtro == 'dia':
                key = fecha.strftime('%Y-%m-%d')
            elif filtro == 'semana':
                key = fecha.strftime('%Y-W%W')
            else:  # mes
                key = fecha.strftime('%Y-%m')

            por_dia[key] += 1
            tipo_counter[tipo] += 1

        dia_mas_activo = max(por_dia.items(), key=lambda x: x[1])[0] if por_dia else 'N/A'
        funcion_mas_usada = max(tipo_counter.items(), key=lambda x: x[1])[0] if tipo_counter else 'N/A'
        promedio = total_operaciones / max(len(por_dia), 1)

        return {
            'total_operaciones': total_operaciones,
            'funcion_mas_usada': funcion_mas_usada,
            'promedio_diario': promedio,
            'dia_mas_activo': dia_mas_activo
        }
