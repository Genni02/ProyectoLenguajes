from typing import List, Dict, Optional
from datetime import datetime
from models import TipoFavorito, Favorito

class FavoritesRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def exists(self, id_usuario: int, tipo: TipoFavorito, id_referencia: int) -> bool:
        """Check if a favorite exists"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1 FROM favoritos
                    WHERE id_usuario = %s AND tipo_favorito = %s AND id_referencia = %s
                    """,
                    (id_usuario, tipo.value, id_referencia)
                )
                return cur.fetchone() is not None

    def create(self, id_usuario: int, tipo: TipoFavorito, id_referencia: int, fecha_agregado: datetime = None) -> int:
        """Create a new favorite entry"""
        fecha = fecha_agregado or datetime.now()
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO favoritos 
                    (id_usuario, tipo_favorito, id_referencia, fecha_agregado)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (id_usuario, tipo.value, id_referencia, fecha)
                )
                conn.commit()
                return cur.lastrowid

    def delete(self, id_usuario: int, tipo: TipoFavorito, id_referencia: int) -> bool:
        """Delete a favorite, returns True if deleted, False if not found"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM favoritos
                    WHERE id_usuario = %s AND tipo_favorito = %s AND id_referencia = %s
                    """,
                    (id_usuario, tipo.value, id_referencia)
                )
                conn.commit()
                return cur.rowcount > 0

    def list_ids(self, id_usuario: int, tipo: Optional[TipoFavorito] = None) -> List[int]:
        """List favorite IDs for a user, optionally filtered by type"""
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                if tipo:
                    cur.execute(
                        """
                        SELECT id_referencia FROM favoritos
                        WHERE id_usuario = %s AND tipo_favorito = %s
                        ORDER BY fecha_agregado DESC
                        """,
                        (id_usuario, tipo.value)
                    )
                else:
                    cur.execute(
                        """
                        SELECT id_referencia FROM favoritos
                        WHERE id_usuario = %s
                        ORDER BY fecha_agregado DESC
                        """,
                        (id_usuario,)
                    )
                return [row[0] for row in cur.fetchall()]

    def get_favorites_details(self, id_usuario: int, tipo: TipoFavorito) -> List[Dict]:
        """Get complete favorite details including timestamp"""
        with self.db.get_connection() as conn:
            with conn.cursor(dictionary=True) as cur:
                cur.execute(
                    """
                    SELECT id_referencia, fecha_agregado 
                    FROM favoritos
                    WHERE id_usuario = %s AND tipo_favorito = %s
                    ORDER BY fecha_agregado DESC
                    """,
                    (id_usuario, tipo.value)
                )
                return cur.fetchall()