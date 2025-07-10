from typing import List, Dict, Any, Tuple
from datetime import datetime
from repositories import HistoryRepository
from models import HistorialCalculo, TipoCalculo

class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository
    
    def convert_legacy_to_model(self, legacy_entry: Dict[str, Any], user_id: int) -> HistorialCalculo:
        """Convierte una entrada legacy del historial a modelo HistorialCalculo"""
        calc = HistorialCalculo(
            id_usuario=user_id,
            expresion=legacy_entry.get('expression', ''),
            resultado=str(legacy_entry.get('result', ''))
        )
        
        # Parsear timestamp
        if 'timestamp' in legacy_entry:
            try:
                calc.timestamp_calculo = datetime.fromisoformat(legacy_entry['timestamp'])
            except (ValueError, TypeError):
                calc.timestamp_calculo = datetime.now()
        else:
            calc.timestamp_calculo = datetime.now()
        
        # Determinar tipo de cálculo basado en la expresión
        calc.tipo_calculo = self.determine_calculation_type(calc.expresion)
        
        return calc
    
    def convert_model_to_legacy(self, calc: HistorialCalculo) -> Dict[str, Any]:
        """Convierte un modelo HistorialCalculo a formato legacy"""
        return {
            'expression': calc.expresion,
            'result': calc.resultado,
            'timestamp': calc.timestamp_calculo.isoformat() if calc.timestamp_calculo else datetime.now().isoformat(),
            'type': calc.tipo_calculo.value,
            'id': calc.id_calculo
        }
    
    def determine_calculation_type(self, expression: str) -> TipoCalculo:
        """Determina el tipo de cálculo basado en la expresión"""
        expression_lower = expression.lower()
        
        # Funciones científicas
        scientific_functions = ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp', 'asin', 'acos', 'atan']
        if any(func in expression_lower for func in scientific_functions):
            return TipoCalculo.CIENTIFICO
        
        # Conversiones de unidades (podrías expandir esto)
        if any(unit in expression_lower for unit in ['m', 'km', 'ft', 'kg', 'lb', '°c', '°f']):
            return TipoCalculo.CONVERSION
        
        # Por defecto es básico
        return TipoCalculo.BASICO
    
    def save_calculation(self, user_id: int, expression: str, result: str, calc_type: TipoCalculo = TipoCalculo.BASICO) -> Tuple[bool, str]:
        """Guarda un cálculo individual"""
        try:
            calc = HistorialCalculo(
                id_usuario=user_id,
                expresion=expression,
                resultado=str(result)
            )
            calc.tipo_calculo = calc_type
            calc.timestamp_calculo = datetime.now()
            
            calc_id = self.history_repository.save_calculation(calc)
            if calc_id:
                calc.id_calculo = calc_id
                return True, "Cálculo guardado correctamente"
            else:
                return False, "Error al guardar el cálculo"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def delete_calculation(self, calculation_id: int) -> Tuple[bool, str]:
        """Elimina un cálculo específico"""
        try:
            success = self.history_repository.delete_calculation(calculation_id)
            if success:
                return True, "Cálculo eliminado correctamente"
            else:
                return False, "Error al eliminar el cálculo o no existe"
                
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def load_user_history(self, user_id: int) -> Tuple[List[Dict[str, Any]], str]:
        """Carga el historial de un usuario y lo convierte a formato legacy"""
        try:
            calculations = self.history_repository.get_user_history(user_id)
            legacy_history = [self.convert_model_to_legacy(calc) for calc in calculations]
            return legacy_history, f"Cargados {len(legacy_history)} cálculos"
            
        except Exception as e:
            return [], f"Error al cargar historial: {str(e)}"
    
    def migrate_anonymous_history(self, anonymous_history: List[Dict[str, Any]], user_id: int) -> Tuple[bool, str]:
        """Migra el historial anónimo a la base de datos"""
        try:
            if not anonymous_history:
                return True, "No hay historial para migrar"
            
            # Convertir historial anónimo a modelos
            calculations = []
            for entry in anonymous_history:
                calc = self.convert_legacy_to_model(entry, user_id)
                calculations.append(calc)
            
            # Guardar en lote
            success = self.history_repository.save_multiple_calculations(calculations)
            
            if success:
                return True, f"Se migraron {len(calculations)} cálculos correctamente"
            else:
                return False, "Error al migrar el historial"
                
        except Exception as e:
            return False, f"Error en migración: {str(e)}"
    
    def clear_user_history(self, user_id: int) -> Tuple[bool, str]:
        """Limpia todo el historial de un usuario"""
        try:
            success = self.history_repository.delete_user_history(user_id)
            if success:
                return True, "Historial eliminado correctamente"
            else:
                return False, "Error al eliminar el historial"
                
        except Exception as e:
            return False, f"Error al eliminar historial: {str(e)}"