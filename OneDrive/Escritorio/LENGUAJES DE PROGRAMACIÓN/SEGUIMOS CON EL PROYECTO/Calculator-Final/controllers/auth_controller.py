import tkinter as tk
from tkinter import messagebox
from services import AuthService
from repositories import AuthRepository
from views import AuthView

class AuthController:
    def __init__(self, app):
        self.app = app
        self.auth_repository = AuthRepository(app.db_connection)
        self.auth_service = AuthService(self.auth_repository)
        self.auth_view = AuthView(app, self.handle_login, self.handle_register)
        
    def create_header(self, parent):
        """Crea el header con opciones de login"""
        header_frame = tk.Frame(parent, bg=self.app.colors['bg'], height=60)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)

        # Botón de login
        login_frame = tk.Frame(header_frame, bg=self.app.colors['bg'])
        login_frame.pack(side=tk.RIGHT, pady=15)
        
        # Solo mostrar el botón de iniciar sesión (ya que siempre empieza como anónimo)
        self.login_button = tk.Button(
            login_frame,
            text="👤 Anónimo - Iniciar Sesión",
            font=("Arial", 10),
            bg=self.app.colors['operator'],
            fg="white",
            relief=tk.FLAT,
            padx=15,
            command=self.show_login_dialog
        )
        self.login_button.pack(side=tk.RIGHT, padx=5)
        
    def show_login_dialog(self):
        """Muestra el diálogo de login"""
        self.auth_view.show_login_dialog()
        
    def handle_login(self, username_or_email: str, password: str, window):
        """Maneja el proceso de login"""
        success, user_info, message = self.auth_service.authenticate_user(username_or_email, password)
        
        if success:
            self.app.current_user = user_info
            self.login_button.config(text=f"👤 {user_info['name']}")
            window.destroy()
            messagebox.showinfo("Login", message)
            print(f"✅ Usuario logueado: {user_info['name']}")
            
            # Manejar migración de historial
            self.app.history_controller.on_user_login()
            
            # Manejar migración de definiciones
            self.app.definitions_controller.on_user_login()
            
            # Actualizar el sidebar para mostrar el botón de cerrar sesión
            self.app.update_sidebar()
        else:
            messagebox.showerror("Error", message)
    
    def handle_register(self, username: str, email: str, password: str, confirm_password: str, window):
        """Maneja el proceso de registro"""
        success, user_info, message = self.auth_service.register_user(username, email, password, confirm_password)
        
        if success:
            self.app.current_user = user_info
            self.login_button.config(text=f"👤 {user_info['name']}")
            window.destroy()
            messagebox.showinfo("Registro", message)
            print(f"✅ Usuario registrado: {user_info['name']}")
            
            # Manejar migración de definiciones para nuevo usuario
            self.app.definitions_controller.on_user_login()
            
            # Actualizar el sidebar para mostrar el botón de cerrar sesión
            self.app.update_sidebar()
        else:
            messagebox.showerror("Error", message)
            
    def logout(self):
        """Cierra la sesión y vuelve al modo anónimo"""
        if self.app.current_user and self.app.current_user.get("mode") != "anonymous":
            if messagebox.askyesno("Cerrar Sesión", "¿Estás seguro que deseas cerrar sesión?"):
                print(f"🔒 Cerrando sesión de: {self.app.current_user.get('name', 'Usuario')}")
                
                # Limpiar historial de BD
                self.app.history_controller.on_user_logout()
                
                # Limpiar definiciones de BD
                self.app.definitions_controller.on_user_logout()
                
                # Limpiar operaciones guardadas en memoria
                self.app.operations_controller.on_user_logout()
                
                # Limpiar favoritos en memoria
                self.app.favorites_controller.on_user_logout()
                
                # Volver al modo anónimo
                self.app.current_user = self.auth_service.create_anonymous_user()
                self.login_button.config(text="👤 Anónimo - Iniciar Sesión")
                
                self.app.saved_operations.clear()
                self.app.favorites.clear()
                self.app.show_view('calculator')
                self.app.update_sidebar()
                
                messagebox.showinfo("Sesión", "Sesión cerrada. Ahora estás en modo anónimo")
                print("🔓 Volviendo al modo anónimo")
        else:
            messagebox.showinfo("Info", "Ya estás en modo anónimo")