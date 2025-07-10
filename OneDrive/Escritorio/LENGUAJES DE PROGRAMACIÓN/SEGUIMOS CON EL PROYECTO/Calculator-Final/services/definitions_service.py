from typing import List, Optional, Tuple
from models import VariableUsuario, FuncionPersonalizada
from repositories import DefinitionsRepository
import re

class DefinitionsService:
    def __init__(self, definitions_repository: DefinitionsRepository):
        self.definitions_repository = definitions_repository
    
    def create_variable(self, user_id: int, name: str, value: str, description: str = None) -> Tuple[bool, str, Optional[VariableUsuario]]:
        """Crea una nueva variable con validaciones"""
        # Validaciones
        if not name or not name.strip():
            return False, "El nombre de la variable es requerido", None
            
        if not value or not value.strip():
            return False, "El valor de la variable es requerido", None
        
        # Validar nombre de variable (solo letras, números y guiones bajos)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name.strip()):
            return False, "El nombre debe comenzar con letra o _ y contener solo letras, números y _", None
        
        # Validar que el valor sea numérico válido
        try:
            float(value.strip())
        except ValueError:
            return False, "El valor debe ser numérico", None
        
        # Crear objeto VariableUsuario
        variable = VariableUsuario(user_id, name.strip(), value.strip())
        variable.descripcion = description.strip() if description else None
        variable.tipo_valor = 'numero'
        
        # Guardar en BD
        success, message, variable_id = self.definitions_repository.create_variable(variable)
        
        if success:
            variable.id_variable = variable_id
            return True, message, variable
        else:
            return False, message, None
    
    def get_user_variables(self, user_id: int) -> Tuple[bool, str, List[VariableUsuario]]:
        """Obtiene las variables del usuario"""
        return self.definitions_repository.get_user_variables(user_id)
    
    def update_variable(self, variable: VariableUsuario, new_name: str, new_value: str, new_description: str = None) -> Tuple[bool, str]:
        """Actualiza una variable existente"""
        # Validaciones
        if not new_name or not new_name.strip():
            return False, "El nombre de la variable es requerido"
            
        if not new_value or not new_value.strip():
            return False, "El valor de la variable es requerido"
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', new_name.strip()):
            return False, "El nombre debe comenzar con letra o _ y contener solo letras, números y _"
        
        try:
            float(new_value.strip())
        except ValueError:
            return False, "El valor debe ser numérico"
        
        # Actualizar objeto
        variable.nombre_variable = new_name.strip()
        variable.valor_variable = new_value.strip()
        variable.descripcion = new_description.strip() if new_description else None
        
        # Guardar cambios
        return self.definitions_repository.update_variable(variable)
    
    def delete_variable(self, variable: VariableUsuario) -> Tuple[bool, str]:
        """Elimina una variable"""
        if not variable.id_variable:
            return False, "Variable no válida para eliminación"
        
        return self.definitions_repository.delete_variable(variable.id_variable, variable.id_usuario)
    
    def create_function(self, user_id: int, name: str, definition: str, parameters: str = None, description: str = None) -> Tuple[bool, str, Optional[FuncionPersonalizada]]:
        """Crea una nueva función personalizada"""
        # Validaciones
        if not name or not name.strip():
            return False, "El nombre de la función es requerido", None
            
        if not definition or not definition.strip():
            return False, "La definición de la función es requerida", None
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name.strip()):
            return False, "El nombre debe comenzar con letra o _ y contener solo letras, números y _", None
        
        # Crear objeto FuncionPersonalizada
        function = FuncionPersonalizada(user_id, name.strip(), definition.strip())
        function.parametros_funcion = parameters.strip() if parameters else None
        function.descripcion = description.strip() if description else None
        
        # Guardar en BD
        success, message, function_id = self.definitions_repository.create_function(function)
        
        if success:
            function.id_funcion = function_id
            return True, message, function
        else:
            return False, message, None
    
    def get_user_functions(self, user_id: int) -> Tuple[bool, str, List[FuncionPersonalizada]]:
        """Obtiene las funciones del usuario"""
        return self.definitions_repository.get_user_functions(user_id)
    
    def update_function(self, function: FuncionPersonalizada, new_name: str, new_definition: str, new_parameters: str = None, new_description: str = None) -> Tuple[bool, str]:
        """Actualiza una función existente"""
        # Validaciones
        if not new_name or not new_name.strip():
            return False, "El nombre de la función es requerido"
            
        if not new_definition or not new_definition.strip():
            return False, "La definición de la función es requerida"
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', new_name.strip()):
            return False, "El nombre debe comenzar con letra o _ y contener solo letras, números y _"
        
        # Actualizar objeto
        function.nombre_funcion = new_name.strip()
        function.definicion_funcion = new_definition.strip()
        function.parametros_funcion = new_parameters.strip() if new_parameters else None
        function.descripcion = new_description.strip() if new_description else None
        
        # Guardar cambios
        return self.definitions_repository.update_function(function)
    
    def delete_function(self, function: FuncionPersonalizada) -> Tuple[bool, str]:
        """Elimina una función"""
        if not function.id_funcion:
            return False, "Función no válida para eliminación"
        
        return self.definitions_repository.delete_function(function.id_funcion, function.id_usuario)