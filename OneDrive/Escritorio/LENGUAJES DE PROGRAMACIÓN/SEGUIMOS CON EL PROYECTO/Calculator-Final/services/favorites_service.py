from typing import List, Optional
from models import TipoFavorito
from datetime import datetime

class FavoritesService:
    def __init__(self, favorites_repository):
        self.repo = favorites_repository

    def toggle_favorite(self, id_usuario: int, tipo_favorito: TipoFavorito, id_referencia: int) -> bool:
        """
        Alterna el estado de favorito y devuelve el nuevo estado.
        True si se agregó como favorito, False si se eliminó.
        """
        if self.repo.exists(id_usuario, tipo_favorito, id_referencia):
            self.repo.delete(id_usuario, tipo_favorito, id_referencia)
            return False
        else:
            fecha_actual = datetime.now()
            self.repo.create(id_usuario, tipo_favorito, id_referencia, fecha_actual)
            return True

    def get_favorite_ids(self, id_usuario: int, tipo_favorito: Optional[TipoFavorito] = None) -> List[int]:
        """Obtiene IDs de referencia favoritos, filtrados por tipo si se especifica"""
        return self.repo.list_ids(id_usuario, tipo_favorito)

    def is_favorite(self, id_usuario: int, tipo_favorito: TipoFavorito, id_referencia: int) -> bool:
        """Verifica si un elemento es favorito"""
        return self.repo.exists(id_usuario, tipo_favorito, id_referencia)