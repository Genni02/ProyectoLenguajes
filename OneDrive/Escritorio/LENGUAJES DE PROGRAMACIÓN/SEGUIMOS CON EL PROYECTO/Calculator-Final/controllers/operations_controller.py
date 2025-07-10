import datetime
from services.operations_service import OperationsService
from repositories.operations_repository import OperationsRepository

class OperationsController:
    def __init__(self, app):
        self.app = app
        self.operations_repository = OperationsRepository(app.db_connection)
        self.operations_service = OperationsService(self.operations_repository)
        self.temp_operations = []

    def save_operation(self, title, expression, result, operation_type):
        user = getattr(self.app, 'current_user', None)
        is_authenticated = user and user.get("mode") != "anonymous"

        if is_authenticated:
            op_id = self.operations_service.save_operation(
                user_id=user["id"],
                title=title,
                expression=expression,
                result=result,
                tipo=operation_type
            )
            return op_id
        else:
            op = {
                "id_temp": len(self.temp_operations) + 1,
                "titulo": title,
                "operacion": expression,
                "descripcion": str(result),
                "tipo_operacion": "expression",
                "fecha": datetime.datetime.now().isoformat()
            }
            self.temp_operations.append(op)
            return op["id_temp"]
    
    def get_all_operations(self):
        ops = []
        user = getattr(self.app, 'current_user', None)
        if user and user.get("mode") != "anonymous":
            ops.extend(self.operations_service.get_operations_for_user(user["id"]))
        ops.extend(self.temp_operations)
        return ops
    
    def delete_operation(self, operation_id, idx=None):
        user = getattr(self.app, 'current_user', None)
        is_authenticated = user and user.get("mode") != "anonymous"
        if is_authenticated:
            return self.operations_service.delete_operation(operation_id)
        else:
            # Eliminar de memoria
            if idx is not None and idx < len(self.temp_operations):
                del self.temp_operations[idx]
                return True
            return False
        
    def delete_all_operations(self):
        user = getattr(self.app, 'current_user', None)
        is_authenticated = user and user.get("mode") != "anonymous"
        if is_authenticated:
            # Eliminar todas de la BD
            return self.operations_repository.delete_all_operations_by_user(user["id"])
        else:
            self.temp_operations.clear()
            return True
        
    def on_user_logout(self):
        """Limpia operaciones guardadas en memoria (modo anónimo)"""
        self.temp_operations.clear()