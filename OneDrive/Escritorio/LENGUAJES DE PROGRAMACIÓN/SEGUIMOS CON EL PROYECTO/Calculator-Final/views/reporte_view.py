import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
from utils.styles import get_colors
import mysql.connector

class ReporteView:
    def create_card(self, parent, title, value, column, color):
        """Crea una card visual para el dashboard de estadísticas"""
        card = tk.Frame(parent, bg=color, bd=0, relief='ridge', highlightthickness=0)
        card.grid(row=0, column=column, padx=8, ipadx=10, ipady=10, sticky='nsew')
        parent.grid_columnconfigure(column, weight=1)
        label_title = tk.Label(card, text=title, font=('Arial', 11, 'bold'), bg=color, fg='white')
        label_title.pack(pady=(5, 0), padx=8)
        label_value = tk.Label(card, text=value, font=('Arial', 18, 'bold'), bg=color, fg='white')
        label_value.pack(pady=(0, 8), padx=8)
    def __init__(self, app, parent_frame=None):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.frame = None
        
        # Configurar estilo de matplotlib y seaborn
        try:
            plt.style.use('seaborn-v0_8')
        except OSError:
            # Si el estilo seaborn-v0_8 no está disponible, usar un estilo alternativo
            try:
                plt.style.use('seaborn')
            except OSError:
                plt.style.use('default')
        
        sns.set_palette("husl")
        
    def show(self):
        """Muestra la vista de inicio con estadísticas"""
        if self.frame:
            self.frame.destroy()
            
        # Usar parent_frame si está disponible, sino usar app.calc_frame
        parent = self.parent_frame if self.parent_frame else self.app.calc_frame
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear scroll para el contenido
        canvas = tk.Canvas(self.frame, bg=self.colors['bg'])
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Layout
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Crear contenido
        self.create_welcome_section(scrollable_frame)
        self.create_statistics_section(scrollable_frame)
        
    def create_welcome_section(self, parent):
        """Crear sección de bienvenida con cards de resumen"""
        welcome_frame = ttk.LabelFrame(parent, text="📊 REPORTES Y RESUMEN", padding=20)
        welcome_frame.pack(fill='x', padx=10, pady=10)
        user_name = self.app.current_user.get("name", "Usuario") if self.app.current_user else "Usuario"
        welcome_text = f"""
¡Hola {user_name}! 👋\n\nAquí puedes ver un resumen visual y colorido de tu actividad en la calculadora.\n"""
        welcome_label = tk.Label(welcome_frame, text=welcome_text, font=('Arial', 13, 'bold'), justify='left',
                                bg='#f0f4ff', fg='#1a237e')
        welcome_label.pack(anchor='w', fill='x', pady=(0, 10))

        # Las cards se muestran justo debajo del mensaje de bienvenida y dentro del mismo cuadro
        cards_frame = tk.Frame(welcome_frame, bg='#f0f4ff')
        cards_frame.pack(fill='x', padx=10, pady=(0, 10))
        stats = self.get_saved_calcs_stats()
        self.create_card(cards_frame, "Guardados totales: ", stats['total'], 0, '#1976d2')
        self.create_card(cards_frame, "Favoritos", stats['favoritos'], 1, '#43a047')
        self.create_card(cards_frame, "Último guardado", stats['ultimo'], 2, '#fbc02d')
        self.create_card(cards_frame, "Reutilizaciones", stats['reutilizados'], 3, '#e53935')


    def get_saved_calcs_stats(self):
        # Datos simulados, reemplazar por consulta real
        return {
            'total': 12,
            'favoritos': 4,
            'ultimo': '05/07/2025',
            'reutilizados': 7
        }

    def get_stats_data(self):
        # Datos simulados para el dashboard
        return {
            'operaciones_dia': 23,
            'operaciones_semana': 120,
            'operaciones_mes': 480,
            'tiempo_uso': '28h 10m',
            'media_sesion': 8.9,
            'top_operaciones': [('Suma', 160), ('Resta', 120), ('Multiplicación', 80), ('División', 70), ('Potencia', 50)]
        }
        
    def create_statistics_section(self, parent):
        """Crear sección de estadísticas con gráficos"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Estadísticas de Uso", padding=10)
        stats_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Obtener datos para estadísticas
        stats_data = self.get_statistics_data()
        
        if not stats_data:
            no_data_label = tk.Label(stats_frame, 
                                   text="📈 No hay datos suficientes para mostrar estadísticas.\n¡Comienza a usar la calculadora para ver tus estadísticas aquí!",
                                   font=('Arial', 12), justify='center',
                                   bg=self.colors['bg'], fg=self.colors['text_light'])
            no_data_label.pack(pady=50)
            return
            
        # Crear notebook para organizar gráficos
        notebook = ttk.Notebook(stats_frame)
        notebook.pack(fill='both', expand=True)
        
        # Pestaña 1: Actividad temporal
        self.create_temporal_activity_tab(notebook, stats_data)
        
        # Pestaña 2: Tipos de operaciones
        self.create_operations_types_tab(notebook, stats_data)
        
        # Pestaña 3: Resumen general
        self.create_summary_tab(notebook, stats_data)
        
    def get_statistics_data(self):
        """Obtener datos estadísticos de la base de datos a nivel global (todos los usuarios)"""
        try:
            connection = self.app.db_connection.get_connection()
            if not connection:
                return None
            cursor = connection.cursor(dictionary=True)
            # Consulta principal para obtener estadísticas globales, usando la tabla favoritos
            query = """
            SELECT 
                h.id_calculo,
                h.expresion,
                h.resultado,
                h.tipo_calculo,
                h.timestamp_calculo,
                CASE 
                    WHEN f.id_favorito IS NOT NULL THEN 1
                    ELSE 0
                END AS es_favorito
            FROM historial_calculos h
            LEFT JOIN favoritos f
                ON h.id_calculo = f.id_referencia
                AND f.tipo_favorito = 'calculo'
                AND f.id_usuario = h.id_usuario
            ORDER BY h.timestamp_calculo DESC
            LIMIT 1000
            """
            cursor.execute(query)
            calculations = cursor.fetchall()
            if not calculations:
                return None
            return {
                'calculations': calculations,
                'total_calculations': len(calculations)
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
                
    def create_temporal_activity_tab(self, notebook, stats_data):
        """Crear pestaña de actividad temporal"""
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text="📅 Actividad")
        
        # Crear figura con subplots
        fig = Figure(figsize=(10, 6), facecolor='white')
        
        # Preparar datos temporales
        calculations = stats_data['calculations']
        dates = [calc['timestamp_calculo'] for calc in calculations]
        
        # Gráfico 1: Operaciones por día (últimos 30 días)
        ax1 = fig.add_subplot(2, 2, 1)
        daily_counts = self.get_daily_counts(dates, days=30)
        if daily_counts:
            dates_list = list(daily_counts.keys())
            counts_list = list(daily_counts.values())
            
            ax1.bar(dates_list, counts_list, alpha=0.7, color='skyblue')
            ax1.set_title('Operaciones por Día (Últimos 30 días)', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Número de Operaciones')
            ax1.tick_params(axis='x', rotation=45)
            
        # Gráfico 2: Operaciones por semana (últimas 12 semanas)
        ax2 = fig.add_subplot(2, 2, 2)
        weekly_counts = self.get_weekly_counts(dates, weeks=12)
        if weekly_counts:
            weeks_list = list(weekly_counts.keys())
            counts_list = list(weekly_counts.values())
            
            ax2.plot(weeks_list, counts_list, marker='o', linewidth=2, markersize=6, color='orange')
            ax2.set_title('Operaciones por Semana (Últimas 12 semanas)', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Semana')
            ax2.set_ylabel('Número de Operaciones')
            ax2.grid(True, alpha=0.3)
            
        # Gráfico 3: Heatmap de actividad por hora del día
        ax3 = fig.add_subplot(2, 2, 3)
        hourly_activity = self.get_hourly_activity(dates)
        if hourly_activity:
            hours = list(range(24))
            activity = [hourly_activity.get(h, 0) for h in hours]
            
            bars = ax3.bar(hours, activity, alpha=0.7, color='lightgreen')
            ax3.set_title('Actividad por Hora del Día', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Hora del Día')
            ax3.set_ylabel('Número de Operaciones')
            ax3.set_xticks(range(0, 24, 2))
            
            # Resaltar las horas más activas
            max_activity = max(activity) if activity else 0
            for i, bar in enumerate(bars):
                if activity[i] == max_activity and max_activity > 0:
                    bar.set_color('red')
                    bar.set_alpha(0.8)
        
        # Gráfico 4: Operaciones por mes (último año)
        ax4 = fig.add_subplot(2, 2, 4)
        monthly_counts = self.get_monthly_counts(dates, months=12)
        if monthly_counts:
            months_list = list(monthly_counts.keys())
            counts_list = list(monthly_counts.values())
            
            ax4.pie(counts_list, labels=months_list, autopct='%1.1f%%', startangle=90)
            ax4.set_title('Distribución Mensual (Último Año)', fontsize=12, fontweight='bold')
        
        fig.subplots_adjust(left=0.08, right=0.97, top=0.93, bottom=0.10, wspace=0.35, hspace=0.35)
        
        # Integrar matplotlib en tkinter
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_operations_types_tab(self, notebook, stats_data):
        """Crear pestaña de tipos de operaciones SOLO para el usuario actual"""
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text="🔢 Tipos de Operaciones")

        # Obtener el id del usuario actual
        user_id = None
        if self.app.current_user:
            user_id = self.app.current_user.get('id_usuario') or self.app.current_user.get('id')
        if not user_id:
            # Si no hay usuario, mostrar mensaje
            label = tk.Label(tab_frame, text="No hay usuario autenticado.", font=('Arial', 12))
            label.pack(pady=30)
            return

        # Consultar los cálculos SOLO de este usuario
        try:
            connection = self.app.db_connection.get_connection()
            if not connection:
                raise Exception("No hay conexión a la base de datos")
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT expresion, tipo_calculo, timestamp_calculo, es_favorito
                FROM historial_calculos
                WHERE id_usuario = %s
                ORDER BY timestamp_calculo DESC
                LIMIT 1000
            """
            cursor.execute(query, (user_id,))
            calculations = cursor.fetchall()
        except Exception as e:
            label = tk.Label(tab_frame, text=f"Error al obtener datos: {e}", font=('Arial', 12))
            label.pack(pady=30)
            return
        finally:
            if 'cursor' in locals():
                cursor.close()

        # Crear figura
        fig = Figure(figsize=(10, 6), facecolor='white')

        # Gráfico 1: Distribución de tipos de cálculo (basico, cientifico, matriz, grafico)
        ax1 = fig.add_subplot(2, 2, 1)
        tipo_map = {'basico': 'Básico', 'cientifico': 'Científico', 'matriz': 'Matriz',}
        tipo_counts = {v: 0 for v in tipo_map.values()}
        for calc in calculations:
            tipo = calc['tipo_calculo']
            tipo_legible = tipo_map.get(tipo, tipo)
            if tipo_legible in tipo_counts:
                tipo_counts[tipo_legible] += 1
            else:
                tipo_counts[tipo_legible] = 1
        tipos = list(tipo_counts.keys())
        counts = list(tipo_counts.values())
        if sum(counts) > 0:
            colors = plt.cm.Set3(np.linspace(0, 1, len(tipos)))
            ax1.pie(counts, labels=tipos, autopct='%1.1f%%', startangle=90, colors=colors)
            ax1.set_title('Distribución de Tipos de Cálculo', fontsize=12, fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax1.transAxes)

        # Gráfico 2: Operaciones más utilizadas (análisis de expresiones)
        ax2 = fig.add_subplot(2, 2, 2)
        operation_patterns = self.analyze_operation_patterns(calculations)
        if operation_patterns:
            operations = list(operation_patterns.keys())[:8]  # Top 8
            frequencies = list(operation_patterns.values())[:8]
            bars = ax2.barh(operations, frequencies, color='lightcoral', alpha=0.7)
            ax2.set_title('Operaciones Más Utilizadas (Top 8)', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Frecuencia de Uso')
            for bar in bars:
                width = bar.get_width()
                ax2.text(width, bar.get_y() + bar.get_height()/2, f'{int(width)}', ha='left', va='center')
        else:
            ax2.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax2.transAxes)

        # Gráfico 3: Evolución de complejidad de operaciones
        ax3 = fig.add_subplot(2, 2, 3)
        complexity_over_time = self.analyze_complexity_over_time(calculations)
        if complexity_over_time:
            dates = list(complexity_over_time.keys())
            complexity = list(complexity_over_time.values())
            ax3.plot(dates, complexity, marker='o', linewidth=2, color='purple', alpha=0.7)
            ax3.set_title('Evolución de Complejidad de Operaciones', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Fecha')
            ax3.set_ylabel('Complejidad Promedio')
            ax3.tick_params(axis='x', rotation=45)
            ax3.grid(True, alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax3.transAxes)

        # Gráfico 4: Operaciones favoritas vs normales (usando tabla favoritos)
        ax4 = fig.add_subplot(2, 2, 4)
        # Obtener el id del usuario actual
        user_id = None
        if self.app.current_user:
            user_id = self.app.current_user.get('id_usuario') or self.app.current_user.get('id')
        favoritas = 0
        if user_id:
            try:
                connection = self.app.db_connection.get_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM favoritos WHERE id_usuario = %s AND tipo_favorito = 'calculo'", (user_id,))
                    favoritas = cursor.fetchone()[0]
            except Exception as e:
                favoritas = 0
            finally:
                if 'cursor' in locals():
                    cursor.close()
        normales = len(calculations) - favoritas
        labels = ['Favoritas', 'Normales']
        sizes = [favoritas, normales]
        colors = ['gold', 'lightblue']
        if sum(sizes) > 0:
            ax4.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax4.set_title('Operaciones Favoritas vs Normales', fontsize=12, fontweight='bold')
        else:
            ax4.text(0.5, 0.5, 'Sin datos', ha='center', va='center', transform=ax4.transAxes)

        fig.subplots_adjust(left=0.10, right=0.97, top=0.93, bottom=0.12, wspace=0.35, hspace=0.35)

        # Integrar matplotlib en tkinter
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    def create_summary_tab(self, notebook, stats_data):
        """Crear pestaña de resumen general"""
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text="📈 Resumen General")
        
        # Frame para métricas textuales
        metrics_frame = ttk.LabelFrame(tab_frame, text="📊 Métricas Generales", padding=20)
        metrics_frame.pack(fill='x', padx=10, pady=10)
        
        calculations = stats_data['calculations']
        
        # Calcular métricas
        total_calcs = len(calculations)
        if total_calcs > 0:
            first_calc = min(calc['timestamp_calculo'] for calc in calculations)
            last_calc = max(calc['timestamp_calculo'] for calc in calculations)
            time_span = (last_calc - first_calc).days
            
            favoritas = sum(1 for calc in calculations if calc['es_favorito'])
            
            # Día más activo
            daily_counts = self.get_daily_counts([calc['timestamp_calculo'] for calc in calculations])
            most_active_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else ("N/A", 0)
            
            # Tipo más usado
            tipo_counts = defaultdict(int)
            for calc in calculations:
                tipo_counts[calc['tipo_calculo']] += 1
            most_used_type = max(tipo_counts.items(), key=lambda x: x[1]) if tipo_counts else ("N/A", 0)
            
            metrics_text = f"""
🔢 Total de operaciones realizadas: {total_calcs:,}
⭐ Operaciones marcadas como favoritas: {favoritas:,}
📅 Tiempo total usando la aplicación: {time_span} días
🏆 Día con mayor actividad: {most_active_day[0]} ({most_active_day[1]} operaciones)
🎯 Tipo de operación más usado: {most_used_type[0]} ({most_used_type[1]} veces)
📊 Promedio de operaciones por día: {total_calcs/max(time_span, 1):.1f}
            """
        else:
            metrics_text = "No hay datos disponibles para mostrar métricas."
            
        metrics_label = tk.Label(metrics_frame, text=metrics_text, 
                               font=('Arial', 11), justify='left',
                               bg=self.colors['bg'], fg=self.colors['text'])
        metrics_label.pack(anchor='w')
        
        # Gráfico resumen
        fig = Figure(figsize=(10, 6), facecolor='white')
        ax = fig.add_subplot(1, 1, 1)
        
        if total_calcs > 0:
            # Crear un gráfico de resumen con múltiples métricas
            metrics = ['Total\nOperaciones', 'Operaciones\nFavoritas', 'Días\nActivos', 'Promedio\nDiario']
            values = [
                total_calcs,
                favoritas,
                len(set(calc['timestamp_calculo'].date() for calc in calculations)),
                total_calcs/max(time_span, 1)
            ]
            
            bars = ax.bar(metrics, values, color=['skyblue', 'gold', 'lightgreen', 'lightcoral'], alpha=0.7)
            ax.set_title('Resumen de Actividad', fontsize=14, fontweight='bold')
            ax.set_ylabel('Cantidad')
            
            # Añadir valores en las barras
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'No hay datos para mostrar', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, alpha=0.7)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            
        fig.tight_layout()
        
        # Integrar matplotlib en tkinter
        canvas = FigureCanvasTkAgg(fig, tab_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        
    # Métodos auxiliares para análisis de datos
    def get_daily_counts(self, dates, days=30):
        """Obtener conteo de operaciones por día"""
        daily_counts = defaultdict(int)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        for date in dates:
            date_obj = date.date() if hasattr(date, 'date') else date
            if start_date <= date_obj <= end_date:
                daily_counts[date_obj.strftime('%m/%d')] += 1
                
        return dict(sorted(daily_counts.items()))
        
    def get_weekly_counts(self, dates, weeks=12):
        """Obtener conteo de operaciones por semana"""
        weekly_counts = defaultdict(int)
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)
        
        for date in dates:
            if start_date <= date <= end_date:
                week_start = date - timedelta(days=date.weekday())
                week_label = week_start.strftime('Sem %U')
                weekly_counts[week_label] += 1
                
        return dict(sorted(weekly_counts.items()))
        
    def get_monthly_counts(self, dates, months=12):
        """Obtener conteo de operaciones por mes"""
        monthly_counts = defaultdict(int)
        end_date = datetime.now()
        start_date = end_date.replace(year=end_date.year - 1)
        
        for date in dates:
            if start_date <= date <= end_date:
                month_label = date.strftime('%b %Y')
                monthly_counts[month_label] += 1
                
        return dict(sorted(monthly_counts.items()))
        
    def get_hourly_activity(self, dates):
        """Obtener actividad por hora del día"""
        hourly_activity = defaultdict(int)
        
        for date in dates:
            hour = date.hour
            hourly_activity[hour] += 1
            
        return dict(hourly_activity)
        
    def analyze_operation_patterns(self, calculations):
        """Analizar patrones en las operaciones"""
        patterns = defaultdict(int)
        
        for calc in calculations:
            expr = calc['expresion'].lower()
            
            # Detectar operadores y funciones comunes
            if '+' in expr:
                patterns['Suma (+)'] += 1
            if '-' in expr:
                patterns['Resta (-)'] += 1
            if '*' in expr:
                patterns['Multiplicación (*)'] += 1
            if '/' in expr:
                patterns['División (/)'] += 1
            if '**' in expr or '^' in expr:
                patterns['Potencia (^)'] += 1
            if 'sin(' in expr:
                patterns['Seno (sin)'] += 1
            if 'cos(' in expr:
                patterns['Coseno (cos)'] += 1
            if 'log(' in expr:
                patterns['Logaritmo (log)'] += 1
            if 'sqrt(' in expr:
                patterns['Raíz cuadrada (√)'] += 1
                
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True))
        
    def analyze_complexity_over_time(self, calculations):
        """Analizar la evolución de complejidad de operaciones"""
        complexity_by_date = defaultdict(list)
        
        for calc in calculations:
            date = calc['timestamp_calculo'].date()
            expr = calc['expresion']
            
            # Calcular complejidad basada en operadores y funciones
            complexity = self.calculate_expression_complexity(expr)
            complexity_by_date[date].append(complexity)
            
        # Calcular promedio por fecha
        avg_complexity = {}
        for date, complexities in complexity_by_date.items():
            avg_complexity[date] = sum(complexities) / len(complexities)
            
        return dict(sorted(avg_complexity.items()))
        
    def calculate_expression_complexity(self, expression):
        """Calcular complejidad de una expresión"""
        complexity = 0
        expr = expression.lower()
        
        # Operadores básicos
        complexity += expr.count('+') * 1
        complexity += expr.count('-') * 1
        complexity += expr.count('*') * 1
        complexity += expr.count('/') * 1
        
        # Operadores avanzados
        complexity += expr.count('**') * 2
        complexity += expr.count('^') * 2
        
        # Funciones
        functions = ['sin', 'cos', 'tan', 'log', 'sqrt', 'exp', 'abs']
        for func in functions:
            complexity += expr.count(func + '(') * 3
            
        # Paréntesis (indica agrupaciones)
        complexity += expr.count('(') * 0.5
        
        return max(complexity, 1)  # Mínimo 1