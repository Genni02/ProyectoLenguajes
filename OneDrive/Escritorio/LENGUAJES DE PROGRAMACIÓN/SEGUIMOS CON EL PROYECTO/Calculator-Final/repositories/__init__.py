"""
Repositorios de la aplicación Calculator.

Este paquete contiene las clases que manejan el acceso a datos,
incluyendo operaciones de base de datos y persistencia.
"""

from .auth_repository import AuthRepository
from .history_repository import HistoryRepository
from .definitions_repository import DefinitionsRepository
from .favorites_repository import FavoritesRepository
from .operations_repository import OperationsRepository

__all__ = ['AuthRepository', 'HistoryRepository', 'DefinitionsRepository', 'FavoritesRepository', 'OperationsRepository']