from mysql.connector import Error
from typing import Optional, List
from models.saved_operations import OperacionGuardada, TipoOperacion

class OperationsRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def save_operation(self, operacion: OperacionGuardada) -> Optional[int]:
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return None
            cursor = connection.cursor()
            insert_query = """
                INSERT INTO operaciones_guardadas (id_usuario, titulo, operacion, descripcion, tipo_operacion)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                operacion.id_usuario,
                operacion.titulo,
                operacion.operacion,
                operacion.descripcion,
                operacion.tipo_operacion.value
            ))
            connection.commit()
            op_id = cursor.lastrowid
            cursor.close()
            return op_id
        except Error as e:
            print(f"❌ Error al guardar operación: {e}")
            return None

    def get_operations_by_user(self, user_id: int) -> List[OperacionGuardada]:
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return []
            cursor = connection.cursor(dictionary=True)
            select_query = """
                SELECT id_operacion, id_usuario, titulo, operacion, descripcion, tipo_operacion, fecha_creacion
                FROM operaciones_guardadas
                WHERE id_usuario = %s
                ORDER BY fecha_creacion DESC
            """
            cursor.execute(select_query, (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            return [OperacionGuardada.from_dict(row) for row in rows]
        except Error as e:
            print(f"❌ Error al obtener operaciones: {e}")
            return []
        
    def delete_operation(self, operation_id: int) -> bool:
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False
            cursor = connection.cursor()
            delete_query = "DELETE FROM operaciones_guardadas WHERE id_operacion = %s"
            cursor.execute(delete_query, (operation_id,))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error al eliminar operación: {e}")
            return False
        
    def delete_all_operations_by_user(self, user_id: int) -> bool:
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False
            cursor = connection.cursor()
            delete_query = "DELETE FROM operaciones_guardadas WHERE id_usuario = %s"
            cursor.execute(delete_query, (user_id,))
            connection.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error al eliminar todas las operaciones: {e}")
            return False