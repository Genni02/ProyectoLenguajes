import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from utils.styles import get_colors
from config.conection import DatabaseConnection
import mysql.connector
from mysql.connector import Error

class InicioView:
    def __init__(self, app, parent_frame=None):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.frame = None
        self.range_var = tk.StringVar(value='Día')
        self.start_time = datetime.now()  # Tiempo de inicio de la aplicación
        self.time_label = None  # Label para mostrar el tiempo de uso

    def show(self):
        if self.frame:
            self.frame.destroy()
        parent = self.parent_frame if self.parent_frame else self.app.calc_frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_welcome_section(self.frame)
        self.create_time_usage_section(self.frame)
        self.create_date_selection_section(self.frame)  # Sección para seleccionar el rango
        self.create_stats_cards(self.frame)

        self.update_time_usage()  # Iniciar actualización del tiempo de uso

    def create_welcome_section(self, parent):
        welcome_frame = ttk.LabelFrame(parent, text="🎉 ¡Bienvenido a la Calculadora Científica!", padding=20)
        welcome_frame.pack(fill='x', padx=10, pady=10)
        
        user_name = self.app.current_user.get("nombre_usuario", "Usuario") if self.app.current_user else "Usuario"
        welcome_text = f"""
¡Hola {user_name}! 👋\n\nBienvenido a NUMINA, el hogar de tus pensamientos numéricos. Te presentamos un vistazo general del uso de nuestra plataforma.\nExplora cómo miles de usuarios interactúan con la calculadora científica avanzada en tiempo real.\n"""
        welcome_label = tk.Label(welcome_frame, text=welcome_text, font=('Arial', 11), justify='left',
                                 bg=self.colors['bg'], fg=self.colors['text'])
        welcome_label.pack(anchor='w')

    def create_time_usage_section(self, parent):
        time_frame = ttk.LabelFrame(parent, text="⏳ Tiempo de uso", padding=20)
        time_frame.pack(fill='x', padx=10, pady=10)
        
        self.time_label = tk.Label(time_frame, text="0:00:00", font=('Arial', 18, 'bold'), fg='black')
        self.time_label.pack(anchor='center')

    def update_time_usage(self):
        # Calcular el tiempo transcurrido
        elapsed_time = datetime.now() - self.start_time
        hours, remainder = divmod(elapsed_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_label.config(text=f"{int(hours)}:{int(minutes):02}:{int(seconds):02}")
        
        # Volver a programar la actualización cada segundo
        self.frame.after(1000, self.update_time_usage)

    def create_date_selection_section(self, parent):
        date_frame = ttk.LabelFrame(parent, text="📅 Seleccionar rango de visualización", padding=20)
        date_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(date_frame, text="Ver por:").pack(side='left')
        combo = ttk.Combobox(date_frame, textvariable=self.range_var, values=['Día', 'Semana', 'Mes'], state='readonly', width=10)
        combo.pack(side='left', padx=5)
        combo.bind('<<ComboboxSelected>>', lambda e: self.update_cards())

    def create_stats_cards(self, parent):
        self.cards_frame = tk.Frame(parent, bg='#f0f4ff')
        self.cards_frame.pack(fill='x', padx=10, pady=10)
        self.update_cards()

    def update_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        
        stats = self.get_stats_data()
        
        # Tarjetas de estadísticas
        self.create_card(self.cards_frame, "Operaciones realizadas", stats['operaciones'], 0, '#1976d2')
        self.create_card(self.cards_frame, "Tiempo total de uso", stats['tiempo_uso'], 1, '#43a047')
        self.create_card(self.cards_frame, "Días con mayor actividad", stats['dias_activos'], 2, '#fbc02d')
        self.create_card(self.cards_frame, "Promedio de operaciones por sesión", stats['media_sesion'], 3, '#e53935')
        self.create_top5_card(self.cards_frame, stats['top_operaciones'], 4, '#00838f')
        self.create_card(self.cards_frame, "Usuarios creados", stats['usuarios_creados'], 5, '#6c757d')
        self.create_card(self.cards_frame, "Total de historial de cálculos", stats['historial_calculos'], 6, '#17a2b8')  # Tarjeta para historial de cálculos
        self.create_card(self.cards_frame, "Última creación de cuenta", stats['ultima_creacion'], 7, '#9c27b0')  # Tarjeta para última creación

    def create_card(self, parent, title, value, col, color):
        card = tk.Frame(parent, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=col, padx=8, pady=5, sticky='nsew')
        tk.Label(card, text=title, font=('Arial', 10, 'bold'), bg=color, fg='white').pack(pady=(8, 0))
        tk.Label(card, text=str(value), font=('Arial', 18, 'bold'), bg=color, fg='white').pack(pady=(0, 8))
        parent.grid_columnconfigure(col, weight=1)

    def create_top5_card(self, parent, top5, col, color):
        card = tk.Frame(parent, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=col, padx=8, pady=5, sticky='nsew')
        tk.Label(card, text="Top 5 Operaciones", font=('Arial', 10, 'bold'), bg=color, fg='white').pack(pady=(8, 0))
        for i, (op, count) in enumerate(top5, 1):
            tk.Label(card, text=f"{i}. {op} ({count})", font=('Arial', 10), bg=color, fg='white').pack(anchor='w')
        parent.grid_columnconfigure(col, weight=1)

    def get_stats_data(self):
        db = DatabaseConnection()
        connection = db.get_connection()
        stats = {
            'operaciones': 0,
            'tiempo_uso': 'N/A',
            'dias_activos': 'N/A',
            'media_sesion': 0,
            'top_operaciones': [],
            'usuarios_creados': 0,
            'historial_calculos': 0,  # Inicialización de historial_calculos
            'ultima_creacion': 'N/A'
        }

        if connection:
            try:
                cursor = connection.cursor()

                # Obtener total de usuarios creados
                cursor.execute("SELECT COUNT(*) FROM usuarios")
                stats['usuarios_creados'] = cursor.fetchone()[0]

                # Obtener total de historial de cálculos
                cursor.execute("SELECT COUNT(*) FROM historial_calculos")
                stats['historial_calculos'] = cursor.fetchone()[0]

                # Obtener la fecha de la última creación de cuenta
                cursor.execute("SELECT fecha_creacion FROM usuarios ORDER BY fecha_creacion DESC LIMIT 1")
                result = cursor.fetchone()
                stats['ultima_creacion'] = result[0].strftime('%Y-%m-%d %H:%M:%S') if result else 'No hay registros'

                # Simulación de datos según un rango
                stats.update({
                    'operaciones': 480,
                    'tiempo_uso': '28h 10m',
                    'dias_activos': '10 días activos',
                    'media_sesion': 8.9,
                    'top_operaciones': [('Suma', 160), ('Resta', 120)]
                })

            except Error as e:
                print(f"Error al consultar la base de datos: {e}")
            finally:
                cursor.close()
                db.disconnect()

        return stats
