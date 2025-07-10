from typing import Optional, Dict, Any
from datetime import datetime

class CategoriaFuncion:
    def __init__(self, nombre_categoria: str, descripcion: str = None):
        self.id_categoria: Optional[int] = None
        self.nombre_categoria = nombre_categoria
        self.descripcion = descripcion
        self.icono: Optional[str] = None
        self.color_hex = '#007bff'
        self.orden_visualizacion = 0
        self.es_sistema = True
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_categoria': self.id_categoria,
            'nombre_categoria': self.nombre_categoria,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'color_hex': self.color_hex,
            'orden_visualizacion': self.orden_visualizacion,
            'es_sistema': self.es_sistema
        }

class FuncionPersonalizada:
    def __init__(self, id_usuario: int, nombre_funcion: str, definicion_funcion: str):
        self.id_funcion: Optional[int] = None
        self.id_usuario = id_usuario
        self.id_categoria: Optional[int] = None
        self.nombre_funcion = nombre_funcion
        self.definicion_funcion = definicion_funcion
        self.parametros_funcion: Optional[str] = None
        self.descripcion: Optional[str] = None
        self.ejemplos_uso: Optional[str] = None
        self.es_publica = False
        self.veces_usada = 0
        self.ultima_modificacion: Optional[datetime] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_funcion': self.id_funcion,
            'id_usuario': self.id_usuario,
            'id_categoria': self.id_categoria,
            'nombre_funcion': self.nombre_funcion,
            'definicion_funcion': self.definicion_funcion,
            'parametros_funcion': self.parametros_funcion,
            'descripcion': self.descripcion,
            'ejemplos_uso': self.ejemplos_uso,
            'es_publica': self.es_publica,
            'veces_usada': self.veces_usada,
            'ultima_modificacion': self.ultima_modificacion.isoformat() if self.ultima_modificacion else None
        }

class ConstantePublica:
    def __init__(self, id_usuario: int, nombre_constante: str, valor_constante: float):
        self.id_constante: Optional[int] = None
        self.id_usuario = id_usuario
        self.id_categoria: Optional[int] = None
        self.nombre_constante = nombre_constante
        self.valor_constante = valor_constante
        self.unidad_constante: Optional[str] = None
        self.descripcion: Optional[str] = None
        self.fuente_referencia: Optional[str] = None
        self.es_publica = False
        self.veces_usada = 0
        self.ultima_modificacion: Optional[datetime] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_constante': self.id_constante,
            'id_usuario': self.id_usuario,
            'id_categoria': self.id_categoria,
            'nombre_constante': self.nombre_constante,
            'valor_constante': self.valor_constante,
            'unidad_constante': self.unidad_constante,
            'descripcion': self.descripcion,
            'fuente_referencia': self.fuente_referencia,
            'es_publica': self.es_publica,
            'veces_usada': self.veces_usada,
            'ultima_modificacion': self.ultima_modificacion.isoformat() if self.ultima_modificacion else None
        }

class VariableUsuario:
    def __init__(self, id_usuario: int, nombre_variable: str, valor_variable: str):
        self.id_variable: Optional[int] = None
        self.id_usuario = id_usuario
        self.nombre_variable = nombre_variable
        self.valor_variable = valor_variable
        self.tipo_valor = 'numero'
        self.descripcion: Optional[str] = None
        self.ultima_modificacion: Optional[datetime] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_variable': self.id_variable,
            'id_usuario': self.id_usuario,
            'nombre_variable': self.nombre_variable,
            'valor_variable': self.valor_variable,
            'tipo_valor': self.tipo_valor,
            'descripcion': self.descripcion,
            'ultima_modificacion': self.ultima_modificacion.isoformat() if self.ultima_modificacion else None
        }