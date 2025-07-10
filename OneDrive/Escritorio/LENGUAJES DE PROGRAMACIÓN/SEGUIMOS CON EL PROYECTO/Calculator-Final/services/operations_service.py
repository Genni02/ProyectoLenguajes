from typing import List, Dict, Any, Optional
from models.saved_operations import OperacionGuardada, TipoOperacion
from repositories.operations_repository import OperationsRepository

class OperationsService:
    def __init__(self, operations_repository: OperationsRepository):
        self.operations_repository = operations_repository

    def save_operation(self, user_id: int, title: str, expression: str, result: str, tipo: str) -> Optional[int]:
        operacion = OperacionGuardada(
            id_usuario=user_id,
            titulo=title,
            operacion=expression
        )
        operacion.descripcion = str(result)
        operacion.tipo_operacion = TipoOperacion(tipo)
        return self.operations_repository.save_operation(operacion)

    def get_operations_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        ops = self.operations_repository.get_operations_by_user(user_id)
        return [op.to_dict() for op in ops]
    
    def delete_operation(self, operation_id: int) -> bool:
        return self.operations_repository.delete_operation(operation_id)