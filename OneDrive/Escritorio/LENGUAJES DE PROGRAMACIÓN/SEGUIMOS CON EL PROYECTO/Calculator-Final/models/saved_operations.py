from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class TipoOperacion(Enum):
    EXPRESSION = 'expression'
    SEQUENCE = 'sequence'
    TEMPLATE = 'template'

class OperacionGuardada:
    def __init__(self, id_usuario: int, titulo: str, operacion: str):
        self.id_operacion: Optional[int] = None
        self.id_usuario = id_usuario
        self.titulo = titulo
        self.operacion = operacion
        self.descripcion: Optional[str] = None
        self.tags: Optional[List[str]] = None
        self.es_favorito = False
        self.fecha_creacion: Optional[datetime] = None
        self.fecha_modificacion: Optional[datetime] = None
        self.tipo_operacion = TipoOperacion.EXPRESSION
        self.metadata: Optional[Dict] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_operacion': self.id_operacion,
            'id_usuario': self.id_usuario,
            'titulo': self.titulo,
            'operacion': self.operacion,
            'descripcion': self.descripcion,
            'tags': self.tags,
            'es_favorito': self.es_favorito,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'tipo_operacion': self.tipo_operacion.value,
            'metadata': self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OperacionGuardada':
        operacion = cls(
            id_usuario=data['id_usuario'],
            titulo=data['titulo'],
            operacion=data['operacion']
        )
        operacion.id_operacion = data.get('id_operacion')
        operacion.descripcion = data.get('descripcion')
        operacion.tags = data.get('tags', [])
        operacion.es_favorito = data.get('es_favorito', False)
        tipo_op = data.get('tipo_operacion', 'expression')
        if isinstance(tipo_op, TipoOperacion):
            operacion.tipo_operacion = tipo_op
        else:
            try:
                operacion.tipo_operacion = TipoOperacion(tipo_op.lower())
            except Exception:
                operacion.tipo_operacion = TipoOperacion.EXPRESSION
        operacion.metadata = data.get('metadata')
        return operacion