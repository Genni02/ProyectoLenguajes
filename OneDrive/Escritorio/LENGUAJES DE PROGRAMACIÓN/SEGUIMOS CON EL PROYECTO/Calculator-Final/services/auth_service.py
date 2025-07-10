import hashlib
import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from repositories import AuthRepository
from models import DatabaseUser, EstadoCuenta

class AuthService:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository
    
    def hash_password(self, password: str) -> str:
        """Crea un hash seguro de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Valida formato de email básico"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_login_data(self, username_or_email: str, password: str) -> Tuple[bool, str]:
        """Valida los datos de login"""
        if not username_or_email or not password:
            return False, "Por favor complete todos los campos"
        return True, ""
    
    def validate_register_data(self, username: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
        """Valida los datos de registro"""
        if not all([username, email, password, confirm_password]):
            return False, "Por favor complete todos los campos"
            
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
            
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
            
        if not self.validate_email(email):
            return False, "Formato de email inválido"
            
        return True, ""
    
    def authenticate_user(self, username_or_email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Autentica un usuario"""
        # Validar datos
        is_valid, error_msg = self.validate_login_data(username_or_email, password)
        if not is_valid:
            return False, None, error_msg
        
        # Buscar usuario usando el modelo
        user: DatabaseUser = self.auth_repository.find_user_by_username_or_email(username_or_email)
        if not user:
            return False, None, "Usuario no encontrado o cuenta inactiva"
        
        # Verificar contraseña
        hashed_password = self.hash_password(password)
        if user.hash_contrasena != hashed_password:
            return False, None, "Contraseña incorrecta"
        
        # Actualizar último acceso
        self.auth_repository.update_last_access(user.id_usuario)
        
        # Preparar datos del usuario usando el modelo
        user_info = {
            "mode": "authenticated",
            "id": user.id_usuario,
            "name": user.nombre_usuario,
            "email": user.email,
            "verified": user.verificado,
            "avatar_url": user.avatar_url,
            "estado_cuenta": user.estado_cuenta.value
        }
        
        return True, user_info, f"¡Bienvenido {user.nombre_usuario}!"
    
    def register_user(self, username: str, email: str, password: str, confirm_password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """Registra un nuevo usuario"""
        # Validar datos
        is_valid, error_msg = self.validate_register_data(username, email, password, confirm_password)
        if not is_valid:
            return False, None, error_msg
        
        # Verificar si el usuario ya existe
        if self.auth_repository.user_exists(username, email):
            return False, None, "El usuario o email ya están registrados"
        
        # Crear modelo de usuario
        hashed_password = self.hash_password(password)
        new_user = DatabaseUser(
            nombre_usuario=username,
            email=email,
            hash_contrasena=hashed_password
        )
        new_user.estado_cuenta = EstadoCuenta.ACTIVO
        new_user.verificado = False
        new_user.fecha_creacion = datetime.now()
        
        # Crear usuario en la base de datos
        user_id = self.auth_repository.create_user(new_user)
        
        if not user_id:
            return False, None, "Error al crear la cuenta"
        
        # Actualizar el ID del usuario
        new_user.id_usuario = user_id
        
        # Preparar datos del usuario
        user_info = {
            "mode": "authenticated",
            "id": new_user.id_usuario,
            "name": new_user.nombre_usuario,
            "email": new_user.email,
            "verified": new_user.verificado,
            "avatar_url": new_user.avatar_url,
            "estado_cuenta": new_user.estado_cuenta.value
        }
        
        return True, user_info, f"¡Cuenta creada exitosamente! Bienvenido {username}!"
    
    def create_anonymous_user(self) -> Dict[str, Any]:
        """Crea un usuario anónimo"""
        return {
            "mode": "anonymous", 
            "name": "Anónimo", 
            "id": None,
            "email": None,
            "verified": False,
            "avatar_url": None
        }