import tkinter as tk
from typing import Callable

class AuthView:
    def __init__(self, app, on_login_callback: Callable, on_register_callback: Callable):
        self.app = app
        self.on_login_callback = on_login_callback
        self.on_register_callback = on_register_callback

    def center_dialog(self, window, width, height):
        """Centra un diálogo en la pantalla"""
        # Obtener dimensiones de la pantalla
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calcular posición para centrar
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Aplicar geometría
        window.geometry(f"{width}x{height}+{x}+{y}")

    def show_login_dialog(self):
        """Muestra el diálogo de login"""
        login_window = tk.Toplevel(self.app.root)
        login_window.title("Iniciar Sesión")
        login_window.configure(bg=self.app.colors['bg'])
        login_window.resizable(False, False)
        
        # Centrar la ventana
        self.center_dialog(login_window, 350, 280)
        login_window.transient(self.app.root)
        login_window.grab_set()
        
        # Título
        tk.Label(
            login_window,
            text="👤 Iniciar Sesión",
            font=("Arial", 14, "bold"),
            bg=self.app.colors['bg'],
            fg=self.app.colors['text_dark']
        ).pack(pady=20)
        
        # Mensaje informativo
        tk.Label(
            login_window,
            text="Actualmente estás navegando como anónimo.\n¡Inicia sesión para guardar tu progreso!",
            font=("Arial", 9),
            bg=self.app.colors['bg'],
            fg=self.app.colors['text'],
            justify=tk.CENTER
        ).pack(pady=(0, 15))
        
        # Campos de entrada
        tk.Label(login_window, text="Usuario o Email:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        username_entry = tk.Entry(login_window, font=("Arial", 10), width=25)
        username_entry.pack(pady=5)
        username_entry.focus()
        
        tk.Label(login_window, text="Contraseña:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        password_entry = tk.Entry(login_window, font=("Arial", 10), show="*", width=25)
        password_entry.pack(pady=5)
        
        # Botones
        button_frame = tk.Frame(login_window, bg=self.app.colors['bg'])
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(
            button_frame,
            text="Iniciar Sesión",
            bg=self.app.colors['operator'],
            fg="white",
            width=12,
            command=lambda: self.on_login_callback(username_entry.get(), password_entry.get(), login_window)
        )
        login_btn.pack(side=tk.LEFT, padx=5)
        
        register_btn = tk.Button(
            button_frame,
            text="Crear Cuenta",
            bg=self.app.colors['numeric'],
            fg=self.app.colors['text'],
            width=12,
            command=lambda: self.show_register_dialog(login_window)
        )
        register_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para continuar como anónimo (cancelar)
        cancel_btn = tk.Button(
            button_frame,
            text="Continuar Anónimo",
            bg=self.app.colors['bg'],
            fg=self.app.colors['text_dark'],
            width=15,
            relief=tk.FLAT,
            command=login_window.destroy
        )
        cancel_btn.pack(pady=(10, 0))
        
        # Bind Enter key
        password_entry.bind('<Return>', lambda e: self.on_login_callback(username_entry.get(), password_entry.get(), login_window))
        
    def show_register_dialog(self, parent_window=None):
        """Muestra el diálogo de registro"""
        if parent_window:
            parent_window.destroy()
            
        register_window = tk.Toplevel(self.app.root)
        register_window.title("Crear Cuenta")
        register_window.configure(bg=self.app.colors['bg'])
        register_window.resizable(False, False)
        
        # Centrar la ventana
        self.center_dialog(register_window, 350, 320)
        register_window.transient(self.app.root)
        register_window.grab_set()
        
        tk.Label(
            register_window,
            text="📝 Crear Nueva Cuenta",
            font=("Arial", 14, "bold"),
            bg=self.app.colors['bg'],
            fg=self.app.colors['text_dark']
        ).pack(pady=15)
        
        # Mensaje informativo
        tk.Label(
            register_window,
            text="¡Crea tu cuenta para guardar tu progreso!",
            font=("Arial", 9),
            bg=self.app.colors['bg'],
            fg=self.app.colors['text']
        ).pack(pady=(0, 10))
        
        # Campos de entrada
        tk.Label(register_window, text="Nombre de Usuario:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        username_entry = tk.Entry(register_window, font=("Arial", 10), width=25)
        username_entry.pack(pady=3)
        username_entry.focus()
        
        tk.Label(register_window, text="Email:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        email_entry = tk.Entry(register_window, font=("Arial", 10), width=25)
        email_entry.pack(pady=3)
        
        tk.Label(register_window, text="Contraseña:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        password_entry = tk.Entry(register_window, font=("Arial", 10), show="*", width=25)
        password_entry.pack(pady=3)
        
        tk.Label(register_window, text="Confirmar Contraseña:", bg=self.app.colors['bg'], fg=self.app.colors['text_dark']).pack()
        confirm_password_entry = tk.Entry(register_window, font=("Arial", 10), show="*", width=25)
        confirm_password_entry.pack(pady=3)
        
        # Botones
        button_frame = tk.Frame(register_window, bg=self.app.colors['bg'])
        button_frame.pack(pady=15)
        
        tk.Button(
            button_frame,
            text="Crear Cuenta",
            bg=self.app.colors['operator'],
            fg="white",
            width=12,
            command=lambda: self.on_register_callback(
                username_entry.get(), 
                email_entry.get(),
                password_entry.get(), 
                confirm_password_entry.get(),
                register_window
            )
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            bg=self.app.colors['numeric'],
            fg=self.app.colors['text'],
            width=12,
            command=register_window.destroy
        ).pack(side=tk.LEFT, padx=5)