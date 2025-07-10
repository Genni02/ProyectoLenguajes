# views/inicio_view.py
import tkinter as tk
from tkinter import ttk
from views.dashboard_controller import DashboardController

class InicioView(ttk.Frame):
    def __init__(self, parent, id_usuario):
        super().__init__(parent)
        self.dashboard = DashboardController(password='tu_contraseña_mysql')
        self.id_usuario = id_usuario
        self.crear_tarjetas()
        self.cargar_datos()

    def crear_tarjetas(self):
        self.tarjeta_total = ttk.Label(self, text="Total operaciones: ...", padding=10, relief="ridge")
        self.tarjeta_total.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.tarjeta_funcion = ttk.Label(self, text="Función + usada: ...", padding=10, relief="ridge")
        self.tarjeta_funcion.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.tarjeta_promedio = ttk.Label(self, text="Promedio diario: ...", padding=10, relief="ridge")
        self.tarjeta_promedio.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.tarjeta_dia = ttk.Label(self, text="Día más activo: ...", padding=10, relief="ridge")
        self.tarjeta_dia.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    def cargar_datos(self):
        total = self.dashboard.get_total_operaciones(id_usuario=self.id_usuario, rango='mes')
        tipo_mas_usado = self.dashboard.get_tipo_calculo_mas_usado(self.id_usuario)
        promedio = self.dashboard.get_promedio_diario(self.id_usuario)
        dia_mas = self.dashboard.get_dia_con_mayor_actividad(self.id_usuario)

        self.tarjeta_total.config(text=f"Total operaciones: {total}")
        tipo_nombres = {
          "basico": "Básico",
          "trigonometrica": "Trigonométrica",
          "logaritmica": "Logarítmica",
          "avanzado": "Avanzado",
          "personalizado": "Personalizado"
        }
        tipo = tipo_mas_usado['tipo_calculo'] if tipo_mas_usado else 'N/A'
        self.tarjeta_funcion.config(text=f"Tipo + usado: {tipo_nombres.get(tipo.lower(), tipo)}")

        self.tarjeta_promedio.config(text=f"Promedio diario: {promedio}")
        self.tarjeta_dia.config(text=f"Día más activo: {dia_mas['dia'] if dia_mas else 'N/A'}")

    def cerrar_conexion(self):
        self.dashboard.cerrar_conexion()
