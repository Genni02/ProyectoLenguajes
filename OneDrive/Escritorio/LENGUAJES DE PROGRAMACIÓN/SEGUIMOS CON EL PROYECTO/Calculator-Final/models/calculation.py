import datetime
from typing import Dict, Any

class Calculation:
    def __init__(self, expression: str, result: str):
        self.expression = expression
        self.result = result
        self.timestamp = datetime.datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el cálculo a un diccionario"""
        return {
            'expression': self.expression,
            'result': self.result,
            'timestamp': self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Calculation':
        """Crea un Calculation desde un diccionario"""
        calc = cls(data['expression'], data['result'])
        calc.timestamp = data['timestamp']
        return calc