from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class EstadoCuenta(Enum):
    ACTIVO = 'activo'
    SUSPENDIDO = 'suspendido'
    ELIMINADO = 'eliminado'

class DatabaseUser:
    def __init__(self, nombre_usuario: str, email: Optional[str] = None, 
                 hash_contrasena: Optional[str] = None, avatar_url: Optional[str] = None):
        self.id_usuario: Optional[int] = None
        self.nombre_usuario = nombre_usuario
        self.email = email
        self.hash_contrasena = hash_contrasena
        self.avatar_url = avatar_url
        self.fecha_creacion: Optional[datetime] = None
        self.ultimo_acceso: Optional[datetime] = None
        self.estado_cuenta = EstadoCuenta.ACTIVO
        self.verificado = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el usuario a un diccionario"""
        return {
            'id_usuario': self.id_usuario,
            'nombre_usuario': self.nombre_usuario,
            'email': self.email,
            'hash_contrasena': self.hash_contrasena,
            'avatar_url': self.avatar_url,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None,
            'estado_cuenta': self.estado_cuenta.value,
            'verificado': self.verificado
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DatabaseUser':
        """Crea un DatabaseUser desde un diccionario"""
        user = cls(
            nombre_usuario=data['nombre_usuario'],
            email=data.get('email'),
            hash_contrasena=data.get('hash_contrasena'),
            avatar_url=data.get('avatar_url')
        )
        user.id_usuario = data.get('id_usuario')
        user.estado_cuenta = EstadoCuenta(data.get('estado_cuenta', 'activo'))
        user.verificado = data.get('verificado', False)
        return user