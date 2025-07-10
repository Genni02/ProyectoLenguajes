import tkinter as tk
from tkinter import ttk
from views.calculator_view import CalculatorView
from views.history_view import HistoryView
from views.saved_view import SavedOperationsView
from views.favorites_view import FavoritesView
from views.export_view import ExportView
from views.notebook_view import NotebookView
from controllers import AuthController, HistoryController, DefinitionsController, FavoritesController, OperationsController
from utils.styles import get_colors
from config import DatabaseConnection
from views.inicio_view import InicioView
from views.reporte_view import ReporteView

class CalculatorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora Científica")
        self.root.state('zoomed')
        self.center_window(1200, 800)
        
        self.colors = get_colors()
        self.root.configure(bg=self.colors['bg'])
        
        # Conexión a la base de datos
        self.db_connection = DatabaseConnection()
        self.test_database_connection()

        # Controladores
        self.auth_controller = AuthController(self)
        self.history_controller = HistoryController(self)
        self.definitions_controller = DefinitionsController(self)
        self.operations_controller  = OperationsController(self)
        self.favorites_controller = FavoritesController(self)
        
        # Estado de la aplicación - SIEMPRE INICIA COMO ANÓNIMO
        self.current_user = self.auth_controller.auth_service.create_anonymous_user()
        self.history = []
        self.saved_operations = []
        self.favorites = []
        self.variables = {}
        self.functions = {}
        
        # Diccionarios para descripciones y parámetros en memoria (usuarios anónimos)
        self.variable_descriptions = {}
        self.function_descriptions = {}
        self.function_parameters = {}
        
        # Configurar UI
        self.setup_ui()
        
        # Vistas (sin inicializar DefinitionsView aquí)
        self.views = {
            'inicio': InicioView(self, self.calc_frame),
            'calculator': CalculatorView(self, self.calc_frame),
            'history': HistoryView(self, self.calc_frame),
            'saved': SavedOperationsView(self, self.calc_frame),
            'favorites': FavoritesView(self, self.calc_frame),
            'export': ExportView(self, self.calc_frame),
            'notebook': NotebookView(self, self.calc_frame),
            'reporte': ReporteView(self, self.calc_frame)

        }
        
        # Mostrar vista inicial
        self.show_view('inicio')
        print("🔓 Aplicación iniciada en modo anónimo")
    
    def center_window(self, width, height):
        """Centra la ventana principal en la pantalla"""
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calcular posición para centrar
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Aplicar geometría
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def test_database_connection(self):
        """Prueba la conexión a la base de datos al iniciar la aplicación"""
        print("🔌 Intentando conectar a la base de datos...")
        connection = self.db_connection.connect()
        if connection:
            print("✅ Base de datos lista para usar")
        else:
            print("❌ Error: No se pudo conectar a la base de datos")
            print("   Verifica que MySQL esté ejecutándose en el puerto 3309")
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header con login y título
        self.create_header(main_frame)
        
        # Contenido principal
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Menu lateral
        self.create_sidebar(content_frame)
        
        # Área de calculadora
        self.calc_frame = tk.Frame(content_frame, bg=self.colors['bg'])
        self.calc_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def create_header(self, parent):
        """Crea el header con título y opciones de login"""
        header_frame = tk.Frame(parent, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Título de la calculadora
        title_label = tk.Label(
            header_frame,
            text="🧮 Calculadora Científica 'NUMINA'",
            font=("Courier New", 18, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        )
        title_label.pack(side=tk.LEFT, padx=20)

        # Área para login generada por el AuthController
        self.auth_controller.create_header(header_frame)
        
    def create_sidebar(self, parent):
        """Crea el menú lateral"""
        self.sidebar_frame = tk.Frame(parent, bg=self.colors['bg'], width=200)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.sidebar_frame.pack_propagate(False)
        
        # Crear el menú inicial
        self.update_sidebar()
        
    def update_sidebar(self):
        """Actualiza el menú lateral según el estado del usuario"""
        # Limpiar sidebar
        for widget in self.sidebar_frame.winfo_children():
            widget.destroy()
            
        menu_title = tk.Label(
            self.sidebar_frame,
            text="📋 MENÚ",
            font=("Courier", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text_dark']
        )
        menu_title.pack(pady=10)
        
        # Opciones básicas (siempre visibles)
        basic_options = [
            ("🏠 Inicio", lambda: self.show_view('inicio')),
            ("🧮 Calculadora", lambda: self.show_view('calculator')),
            ("🧾 Resolución Detallada", lambda: self.show_view('notebook')),
            ("📜 Historial", lambda: self.show_view('history')),
            ("💾 Operaciones Guardadas", lambda: self.show_view('saved')),
            ("🧠 Gestor de Definiciones", lambda: self.show_view('definitions')),
            ("⭐ Favoritos", lambda: self.show_view('favorites')),
            ("📊 Mis Estadísticas", lambda: self.show_view('reporte')),
            ("📤 Exportar Historial", lambda: self.show_view('export'))
        ]
        
        # Agregar opciones básicas
        for text, command in basic_options:
            btn = tk.Button(
                self.sidebar_frame,
                text=text,
                font=("Arial", 10),
                bg=self.colors['numeric'],
                fg=self.colors['text'],
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                command=command
            )
            btn.pack(fill=tk.X, pady=2, padx=5)
        
        # Agregar separador si el usuario está autenticado
        if self.current_user and self.current_user.get("mode") == "authenticated":
            separator = tk.Frame(self.sidebar_frame, height=2, bg=self.colors['text_dark'])
            separator.pack(fill=tk.X, pady=10, padx=5)
            
            # Botón de cerrar sesión (solo si está autenticado)
            logout_btn = tk.Button(
                self.sidebar_frame,
                text="🔒 Cerrar Sesión",
                font=("Arial", 10),
                bg=self.colors['operator'],  # Color diferente para destacar
                fg="white",
                relief=tk.FLAT,
                anchor="w",
                padx=10,
                command=self.auth_controller.logout
            )
            logout_btn.pack(fill=tk.X, pady=2, padx=5)
    
    def show_view(self, view_name):
        """Muestra una vista específica"""
        # Limpiar el frame de contenido
        for widget in self.calc_frame.winfo_children():
            widget.destroy()

        if view_name == 'definitions':
            self.definitions_controller.show_definitions_view(self.calc_frame)
        else:
            if view_name in self.views:
                self.views[view_name].show()
        
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()