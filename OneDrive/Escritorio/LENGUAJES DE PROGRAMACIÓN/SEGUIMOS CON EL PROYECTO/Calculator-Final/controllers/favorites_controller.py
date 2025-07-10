from typing import List, Dict, Any
from models import TipoFavorito, Favorito
from repositories import FavoritesRepository
from services import FavoritesService

class FavoritesController:
    def __init__(self, app):
        self.app = app
        self.favorites_repository = FavoritesRepository(app.db_connection)
        self.favorites_service = FavoritesService(self.favorites_repository)

    def toggle_favorite(self, operation_id: int, operation_data: Dict[str, Any] = None) -> None:
        """
        Alterna el estado de favorito para una operación.
        Args:
            operation_id: ID de la operación
            operation_data: Datos completos de la operación (para usuarios anónimos)
        """
        user = self.app.current_user
        user_id = user.get("id") if user else None
        tipo = TipoFavorito.OPERACION

        if user_id:
            # Usuario autenticado - usar base de datos
            self.favorites_service.toggle_favorite(
                id_usuario=user_id,
                tipo_favorito=tipo,
                id_referencia=operation_id
            )
            # Actualizar estado en operaciones guardadas (opcional, si quieres reflejarlo en memoria)
            self.app.operations_controller.toggle_favorite(operation_id)
        else:
            # Usuario anónimo - usar memoria
            if operation_data:
                operation_data['favorito'] = not operation_data.get('favorito', False)
                # Asegurarse de que esté en saved_operations si no está
                if not any(
                    (op.get('id') == operation_id or op.get('id_operacion') == operation_id)
                    for op in self.app.saved_operations
                ):
                    self.app.saved_operations.append(operation_data)

    def is_favorite(self, operation_id: int) -> bool:
        """
        Retorna True si la operación es favorita, False si no.
        Soporta usuarios autenticados y anónimos.
        """
        user = self.app.current_user
        user_id = user.get("id") if user else None
        tipo = TipoFavorito.OPERACION

        if user_id:
            fav_ids = self.favorites_service.get_favorite_ids(user_id, tipo)
            return operation_id in fav_ids
        else:
            for op in self.app.saved_operations:
                if op.get('id') == operation_id or op.get('id_operacion') == operation_id:
                    return op.get('favorito', False)
            return False

    def get_favorite_operations(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las operaciones favoritas, tanto de BD como temporales.
        """
        user = self.app.current_user
        user_id = user.get("id") if user else None
        tipo = TipoFavorito.OPERACION

        if user_id:
            # Obtener favoritos de la base de datos
            fav_ids = self.favorites_service.get_favorite_ids(user_id, tipo)
            # Obtener las operaciones completas
            return [
                op for op in self.app.operations_controller.get_all_operations()
                if (op.get('id') or op.get('id_operacion')) in fav_ids
            ]
        else:
            # Usuario anónimo - obtener de memoria
            return [
                op for op in self.app.saved_operations
                if op.get('favorito', False)
            ]
        
    def on_user_logout(self):
        """Limpia favoritos en memoria (modo anónimo)"""
        if hasattr(self.app, "favorites"):
            self.app.favorites.clear()