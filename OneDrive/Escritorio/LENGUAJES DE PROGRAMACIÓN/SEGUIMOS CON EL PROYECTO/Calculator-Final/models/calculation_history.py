from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class TipoCalculo(Enum):
    BASICO = 'basico'
    CIENTIFICO = 'cientifico'
    CONVERSION = 'conversion'
    MATRIZ = 'matriz'
    GRAFICO = 'grafico'

class HistorialCalculo:
    def __init__(self, id_usuario: int, expresion: str, resultado: str):
        self.id_calculo: Optional[int] = None
        self.id_usuario = id_usuario
        self.expresion = expresion
        self.resultado = resultado
        self.tipo_calculo = TipoCalculo.BASICO
        self.timestamp_calculo: Optional[datetime] = None
        self.es_favorito = False
        self.etiquetas: Optional[List[str]] = None
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id_calculo': self.id_calculo,
            'id_usuario': self.id_usuario,
            'expresion': self.expresion,
            'resultado': self.resultado,
            'tipo_calculo': self.tipo_calculo.value,
            'timestamp_calculo': self.timestamp_calculo.isoformat() if self.timestamp_calculo else None,
            'es_favorito': self.es_favorito,
            'etiquetas': self.etiquetas
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistorialCalculo':
        calculo = cls(
            id_usuario=data['id_usuario'],
            expresion=data['expresion'],
            resultado=data['resultado']
        )
        calculo.id_calculo = data.get('id_calculo')
        calculo.tipo_calculo = TipoCalculo(data.get('tipo_calculo', 'basico'))
        calculo.es_favorito = data.get('es_favorito', False)
        calculo.etiquetas = data.get('etiquetas', [])
        return calculo