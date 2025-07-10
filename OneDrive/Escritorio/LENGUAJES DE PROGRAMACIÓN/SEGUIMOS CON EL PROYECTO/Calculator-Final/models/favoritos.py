from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TipoFavorito(Enum):
    CALCULO = 'calculo'
    FUNCION = 'funcion'
    CONSTANTE = 'constante'
    OPERACION = 'operacion'

class Favorito:
    def __init__(self, id_usuario: int, tipo_favorito: TipoFavorito, id_referencia: int):
        self.id_favorito: Optional[int] = None
        self.id_usuario = id_usuario
        self.tipo_favorito = tipo_favorito
        self.id_referencia = id_referencia
        self.fecha_agregado: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_favorito': self.id_favorito,
            'id_usuario': self.id_usuario,
            'tipo_favorito': self.tipo_favorito.value,
            'id_referencia': self.id_referencia,
            'fecha_agregado': self.fecha_agregado.isoformat() if self.fecha_agregado else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Favorito':
        favorito = cls(
            id_usuario=data['id_usuario'],
            tipo_favorito=TipoFavorito(data['tipo_favorito']),
            id_referencia=data['id_referencia']
        )
        favorito.id_favorito = data.get('id_favorito')
        favorito.fecha_agregado = data.get('fecha_agregado')
        return favorito