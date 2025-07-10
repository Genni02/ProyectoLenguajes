from typing import Optional, List
from tkinter import messagebox
from models import VariableUsuario, FuncionPersonalizada
from services import DefinitionsService
from repositories import DefinitionsRepository
from views import DefinitionsView

class DefinitionsController:
    def __init__(self, app):
        self.app = app
        self.definitions_repository = DefinitionsRepository(app.db_connection)
        self.definitions_service = DefinitionsService(self.definitions_repository)
        self.definitions_view = None
        
        # Asegurar que existen los diccionarios para descripciones en memoria
        if not hasattr(self.app, 'variable_descriptions'):
            self.app.variable_descriptions = {}
        if not hasattr(self.app, 'function_descriptions'):
            self.app.function_descriptions = {}
        if not hasattr(self.app, 'function_parameters'):
            self.app.function_parameters = {}
    
    def show_definitions_view(self, parent_frame):
        """Muestra la vista de definiciones"""
        self.definitions_view = DefinitionsView(
            app=self.app,
            parent_frame=parent_frame,
            controller=self
        )
        self.definitions_view.show()
        self.load_user_data()
    
    def load_user_data(self):
        """Carga los datos del usuario si está autenticado, si no, muestra datos en memoria"""
        print("📂 Iniciando carga de datos de usuario...")
        
        if self.definitions_view:
            if self.is_user_authenticated():
                user_id = self.app.current_user['id']
                print(f"👤 Usuario autenticado ID: {user_id}")
                
                # Cargar variables de BD
                print("🔄 Cargando variables desde BD...")
                success, message, variables = self.definitions_service.get_user_variables(user_id)
                print(f"   Variables - Éxito: {success}, Mensaje: {message}, Cantidad: {len(variables) if success else 0}")
                
                if success:
                    self.definitions_view.load_variables(variables)
                else:
                    print(f"❌ Error cargando variables: {message}")
                    self.definitions_view.load_variables([])
                
                # Cargar funciones de BD
                print("🔄 Cargando funciones desde BD...")
                success, message, functions = self.definitions_service.get_user_functions(user_id)
                print(f"   Funciones - Éxito: {success}, Mensaje: {message}, Cantidad: {len(functions) if success else 0}")
                
                if success:
                    self.definitions_view.load_functions(functions)
                else:
                    print(f"❌ Error cargando funciones: {message}")
                    self.definitions_view.load_functions([])
            else:
                # Usuario anónimo: solo cargar datos en memoria
                print("🔓 Usuario anónimo - cargando datos de memoria")
                print(f"   Variables en memoria: {len(self.app.variables)}")
                print(f"   Funciones en memoria: {len(self.app.functions)}")
                
                self.definitions_view.load_variables([])
                self.definitions_view.load_functions([])
        else:
            print("❌ definitions_view no está inicializada")
    
    def create_variable(self, name: str, value: str, description: str = None) -> bool:
        """Crea una nueva variable"""
        # Validaciones básicas
        if not name or not name.strip():
            messagebox.showerror("Error", "El nombre de la variable es requerido")
            return False
            
        if not value or not value.strip():
            messagebox.showerror("Error", "El valor de la variable es requerido")
            return False
        
        # Validar que el valor sea numérico
        try:
            float(value.strip())
        except ValueError:
            messagebox.showerror("Error", "El valor debe ser numérico")
            return False
        
        # Verificar si la variable ya existe en memoria
        if name.strip() in self.app.variables:
            if not messagebox.askyesno(
                "Variable Existente", 
                f"La variable '{name.strip()}' ya existe.\n¿Deseas reemplazarla?",
                icon="warning"
            ):
                return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: guardar en BD y memoria
            user_id = self.app.current_user['id']
            success, message, variable = self.definitions_service.create_variable(user_id, name, value, description)
            
            if success:
                messagebox.showinfo("Variable Creada", message)
                # Actualizar también las variables en memoria para uso inmediato
                self.app.variables[name.strip()] = value.strip()
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: solo guardar en memoria
            self.app.variables[name.strip()] = value.strip()
            # Guardar descripción por separado para usuarios anónimos
            if description and description.strip():
                self.app.variable_descriptions[name.strip()] = description.strip()
            elif name.strip() in self.app.variable_descriptions:
                # Si no hay descripción nueva, limpiar la anterior
                del self.app.variable_descriptions[name.strip()]
            
            messagebox.showinfo("Variable Creada", f"Variable '{name.strip()}' creada en la sesión actual")
            self.load_user_data()  # Recargar para mostrar cambios
            return True
    
    def update_variable(self, variable: VariableUsuario, new_name: str, new_value: str, new_description: str = None) -> bool:
        """Actualiza una variable existente"""
        # Validaciones básicas
        if not new_name or not new_name.strip():
            messagebox.showerror("Error", "El nombre de la variable es requerido")
            return False
            
        if not new_value or not new_value.strip():
            messagebox.showerror("Error", "El valor de la variable es requerido")
            return False
        
        try:
            float(new_value.strip())
        except ValueError:
            messagebox.showerror("Error", "El valor debe ser numérico")
            return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: actualizar en BD y memoria
            success, message = self.definitions_service.update_variable(variable, new_name, new_value, new_description)
            
            if success:
                messagebox.showinfo("Variable Actualizada", message)
                # Actualizar también en memoria
                old_name = variable.nombre_variable
                if old_name in self.app.variables and old_name != new_name.strip():
                    del self.app.variables[old_name]
                self.app.variables[new_name.strip()] = new_value.strip()
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: actualizar en memoria
            old_name = variable.nombre_variable
            if old_name in self.app.variables and old_name != new_name.strip():
                del self.app.variables[old_name]
                # Actualizar descripción también si cambió el nombre
                if old_name in self.app.variable_descriptions:
                    self.app.variable_descriptions[new_name.strip()] = self.app.variable_descriptions[old_name]
                    del self.app.variable_descriptions[old_name]
            
            self.app.variables[new_name.strip()] = new_value.strip()
            
            # Actualizar descripción
            if new_description and new_description.strip():
                self.app.variable_descriptions[new_name.strip()] = new_description.strip()
            elif new_name.strip() in self.app.variable_descriptions:
                del self.app.variable_descriptions[new_name.strip()]
            
            messagebox.showinfo("Variable Actualizada", f"Variable '{new_name.strip()}' actualizada en la sesión actual")
            self.load_user_data()  # Recargar para mostrar cambios
            return True
    
    def delete_variable(self, variable: VariableUsuario) -> bool:
        """Elimina una variable"""
        if not messagebox.askyesno(
            "Eliminar Variable",
            f"¿Estás seguro de que deseas eliminar la variable '{variable.nombre_variable}'?",
            icon="warning"
        ):
            return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: eliminar de BD y memoria
            success, message = self.definitions_service.delete_variable(variable)
            
            if success:
                messagebox.showinfo("Variable Eliminada", message)
                # Eliminar también de memoria
                if variable.nombre_variable in self.app.variables:
                    del self.app.variables[variable.nombre_variable]
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: eliminar de memoria
            if variable.nombre_variable in self.app.variables:
                del self.app.variables[variable.nombre_variable]
                # Eliminar también la descripción
                if variable.nombre_variable in self.app.variable_descriptions:
                    del self.app.variable_descriptions[variable.nombre_variable]
                messagebox.showinfo("Variable Eliminada", f"Variable '{variable.nombre_variable}' eliminada de la sesión actual")
                self.load_user_data()  # Recargar para mostrar cambios
                return True
            else:
                messagebox.showerror("Error", "Variable no encontrada")
                return False
    
    def create_function(self, name: str, definition: str, parameters: str = None, description: str = None) -> bool:
        """Crea una nueva función"""
        # Validaciones básicas
        if not name or not name.strip():
            messagebox.showerror("Error", "El nombre de la función es requerido")
            return False
            
        if not definition or not definition.strip():
            messagebox.showerror("Error", "La definición de la función es requerida")
            return False
        
        # Verificar si la función ya existe en memoria
        if name.strip() in self.app.functions:
            if not messagebox.askyesno(
                "Función Existente", 
                f"La función '{name.strip()}' ya existe.\n¿Deseas reemplazarla?",
                icon="warning"
            ):
                return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: guardar en BD y memoria
            user_id = self.app.current_user['id']
            success, message, function = self.definitions_service.create_function(user_id, name, definition, parameters, description)
            
            if success:
                messagebox.showinfo("Función Creada", message)
                # Actualizar también en memoria
                self.app.functions[name.strip()] = definition.strip()
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: solo guardar en memoria
            self.app.functions[name.strip()] = definition.strip()
            
            # Guardar parámetros y descripción por separado para usuarios anónimos
            if parameters and parameters.strip():
                self.app.function_parameters[name.strip()] = parameters.strip()
            elif name.strip() in self.app.function_parameters:
                del self.app.function_parameters[name.strip()]
                
            if description and description.strip():
                self.app.function_descriptions[name.strip()] = description.strip()
            elif name.strip() in self.app.function_descriptions:
                del self.app.function_descriptions[name.strip()]
            
            messagebox.showinfo("Función Creada", f"Función '{name.strip()}' creada en la sesión actual")
            self.load_user_data()  # Recargar para mostrar cambios
            return True
    
    def update_function(self, function: FuncionPersonalizada, new_name: str, new_definition: str, new_parameters: str = None, new_description: str = None) -> bool:
        """Actualiza una función existente"""
        # Validaciones básicas
        if not new_name or not new_name.strip():
            messagebox.showerror("Error", "El nombre de la función es requerido")
            return False
            
        if not new_definition or not new_definition.strip():
            messagebox.showerror("Error", "La definición de la función es requerida")
            return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: actualizar en BD y memoria
            success, message = self.definitions_service.update_function(function, new_name, new_definition, new_parameters, new_description)
            
            if success:
                messagebox.showinfo("Función Actualizada", message)
                # Actualizar también en memoria
                old_name = function.nombre_funcion
                if old_name in self.app.functions and old_name != new_name.strip():
                    del self.app.functions[old_name]
                self.app.functions[new_name.strip()] = new_definition.strip()
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: actualizar en memoria
            old_name = function.nombre_funcion
            if old_name in self.app.functions and old_name != new_name.strip():
                del self.app.functions[old_name]
                # Mover descripciones y parámetros también si cambió el nombre
                if old_name in self.app.function_descriptions:
                    self.app.function_descriptions[new_name.strip()] = self.app.function_descriptions[old_name]
                    del self.app.function_descriptions[old_name]
                if old_name in self.app.function_parameters:
                    self.app.function_parameters[new_name.strip()] = self.app.function_parameters[old_name]
                    del self.app.function_parameters[old_name]
            
            self.app.functions[new_name.strip()] = new_definition.strip()
            
            # Actualizar parámetros y descripción
            if new_parameters and new_parameters.strip():
                self.app.function_parameters[new_name.strip()] = new_parameters.strip()
            elif new_name.strip() in self.app.function_parameters:
                del self.app.function_parameters[new_name.strip()]
                
            if new_description and new_description.strip():
                self.app.function_descriptions[new_name.strip()] = new_description.strip()
            elif new_name.strip() in self.app.function_descriptions:
                del self.app.function_descriptions[new_name.strip()]
            
            messagebox.showinfo("Función Actualizada", f"Función '{new_name.strip()}' actualizada en la sesión actual")
            self.load_user_data()  # Recargar para mostrar cambios
            return True
    
    def delete_function(self, function: FuncionPersonalizada) -> bool:
        """Elimina una función"""
        if not messagebox.askyesno(
            "Eliminar Función",
            f"¿Estás seguro de que deseas eliminar la función '{function.nombre_funcion}'?",
            icon="warning"
        ):
            return False
        
        if self.is_user_authenticated():
            # Usuario autenticado: eliminar de BD y memoria
            success, message = self.definitions_service.delete_function(function)
            
            if success:
                messagebox.showinfo("Función Eliminada", message)
                # Eliminar también de memoria
                if function.nombre_funcion in self.app.functions:
                    del self.app.functions[function.nombre_funcion]
                self.load_user_data()
                return True
            else:
                messagebox.showerror("Error", message)
                return False
        else:
            # Usuario anónimo: eliminar de memoria
            if function.nombre_funcion in self.app.functions:
                del self.app.functions[function.nombre_funcion]
                # Eliminar también descripciones y parámetros
                if function.nombre_funcion in self.app.function_descriptions:
                    del self.app.function_descriptions[function.nombre_funcion]
                if function.nombre_funcion in self.app.function_parameters:
                    del self.app.function_parameters[function.nombre_funcion]
                messagebox.showinfo("Función Eliminada", f"Función '{function.nombre_funcion}' eliminada de la sesión actual")
                self.load_user_data()  # Recargar para mostrar cambios
                return True
            else:
                messagebox.showerror("Error", "Función no encontrada")
                return False
    
    def on_user_login(self):
        """Maneja el evento cuando un usuario inicia sesión"""
        print("🔄 Usuario logueado - recargando gestor de definiciones")
        if not self.is_user_authenticated():
            return
        
        # Si hay variables en memoria, preguntar si migrar
        total_variables = len(self.app.variables)
        total_functions = len(self.app.functions)
        
        if total_variables > 0 or total_functions > 0:
            items_text = []
            if total_variables > 0:
                items_text.append(f"{total_variables} variables")
            if total_functions > 0:
                items_text.append(f"{total_functions} funciones")
            
            items_description = " y ".join(items_text)
            
            if messagebox.askyesno(
                "Guardar Definiciones",
                f"Tienes {items_description} en tu sesión anónima.\n"
                "¿Deseas guardarlas en tu cuenta?",
                icon="question"
            ):
                self.migrate_anonymous_definitions()
        
        # Recargar vista si está activa
        if self.definitions_view:
            self.load_user_data()
    
    def migrate_anonymous_definitions(self):
        """Migra las definiciones anónimas a la cuenta del usuario"""
        if not self.is_user_authenticated():
            return
        
        user_id = self.app.current_user['id']
        migrated_variables = 0
        migrated_functions = 0
        
        # Migrar variables
        for name, value in self.app.variables.items():
            description = self.app.variable_descriptions.get(name, "Migrada desde sesión anónima")
            success, message, variable = self.definitions_service.create_variable(
                user_id, name, value, description
            )
            if success:
                migrated_variables += 1
        
        # Migrar funciones
        for name, definition in self.app.functions.items():
            parameters = self.app.function_parameters.get(name, None)
            description = self.app.function_descriptions.get(name, "Migrada desde sesión anónima")
            success, message, function = self.definitions_service.create_function(
                user_id, name, definition, parameters, description
            )
            if success:
                migrated_functions += 1
        
        # Mostrar resultado
        migration_messages = []
        if migrated_variables > 0:
            migration_messages.append(f"{migrated_variables} variables")
        if migrated_functions > 0:
            migration_messages.append(f"{migrated_functions} funciones")
        
        if migration_messages:
            items_description = " y ".join(migration_messages)
            messagebox.showinfo("Migración Completa", f"Se migraron {items_description} exitosamente")
        else:
            messagebox.showwarning("Migración", "No se pudieron migrar las definiciones")
        
        # Recargar datos
        self.load_user_data()
    
    def on_user_logout(self):
        """Maneja el evento cuando un usuario cierra sesión"""
        print("🧹 Limpiando definiciones de usuario autenticado")
        # Solo recargar si la vista está activa y los widgets existen
        if self.definitions_view:
            if (hasattr(self.definitions_view, "var_tree") and self.definitions_view.var_tree and
                self.definitions_view.var_tree.winfo_exists()):
                self.definitions_view.load_variables([])
            if (hasattr(self.definitions_view, "func_tree") and self.definitions_view.func_tree and
                self.definitions_view.func_tree.winfo_exists()):
                self.definitions_view.load_functions([])
    
    def is_user_authenticated(self) -> bool:
        """Verifica si el usuario está autenticado"""
        is_auth = (hasattr(self.app, 'current_user') and 
                  self.app.current_user is not None and 
                  self.app.current_user.get("mode") == "authenticated" and
                  'id' in self.app.current_user)
        
        print(f"🔍 Verificando autenticación: {is_auth}")
        if self.app.current_user:
            print(f"   - Modo: {self.app.current_user.get('mode', 'None')}")
            print(f"   - ID: {self.app.current_user.get('id', 'None')}")
        
        return is_auth