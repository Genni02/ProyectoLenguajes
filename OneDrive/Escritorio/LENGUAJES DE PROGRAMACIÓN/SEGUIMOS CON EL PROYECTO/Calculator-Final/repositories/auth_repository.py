import mysql.connector
from mysql.connector import Error
from typing import Optional
from models import DatabaseUser

class AuthRepository:
  def __init__(self, db_connection):
    self.db_connection = db_connection
  
  def find_user_by_username_or_email(self, username_or_email: str) -> Optional[DatabaseUser]:
    """Busca un usuario por nombre de usuario o email"""
    try:
      connection = self.db_connection.get_connection()
      if not connection:
        return None
          
      cursor = connection.cursor(dictionary=True)
      
      query = """
        SELECT id_usuario, nombre_usuario, email, hash_contrasena, 
                estado_cuenta, verificado, fecha_creacion, ultimo_acceso, avatar_url
        FROM usuarios 
        WHERE (nombre_usuario = %s OR email = %s) AND estado_cuenta = 'activo'
      """
      cursor.execute(query, (username_or_email, username_or_email))
      user_data = cursor.fetchone()
      
      if user_data:
        user = DatabaseUser.from_dict(user_data)
        return user
      return None
        
    except Error as e:
        print(f"❌ Error en repository - find_user_by_username_or_email: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
  
  def update_last_access(self, user_id: int) -> bool:
      """Actualiza el último acceso del usuario"""
      try:
          connection = self.db_connection.get_connection()
          if not connection:
              return False
              
          cursor = connection.cursor()
          
          update_query = """
              UPDATE usuarios 
              SET ultimo_acceso = CURRENT_TIMESTAMP 
              WHERE id_usuario = %s
          """
          cursor.execute(update_query, (user_id,))
          connection.commit()
          return True
          
      except Error as e:
          print(f"❌ Error en repository - update_last_access: {e}")
          return False
      finally:
          if 'cursor' in locals():
              cursor.close()
  
  def user_exists(self, username: str, email: str) -> bool:
      """Verifica si un usuario o email ya existen"""
      try:
          connection = self.db_connection.get_connection()
          if not connection:
              return True  # Asumir que existe para evitar duplicados
              
          cursor = connection.cursor()
          
          check_query = """
              SELECT COUNT(*) as count FROM usuarios 
              WHERE nombre_usuario = %s OR email = %s
          """
          cursor.execute(check_query, (username, email))
          result = cursor.fetchone()
          
          return result[0] > 0
          
      except Error as e:
          print(f"❌ Error en repository - user_exists: {e}")
          return True  # Asumir que existe para evitar errores
      finally:
          if 'cursor' in locals():
              cursor.close()
  
  def create_user(self, user: DatabaseUser) -> Optional[int]:
      """Crea un nuevo usuario y retorna su ID"""
      try:
          connection = self.db_connection.get_connection()
          if not connection:
              return None
              
          cursor = connection.cursor()
          
          insert_query = """
              INSERT INTO usuarios (nombre_usuario, email, hash_contrasena, 
                                  fecha_creacion, estado_cuenta, verificado, avatar_url)
              VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
          """
          cursor.execute(insert_query, (
              user.nombre_usuario, 
              user.email, 
              user.hash_contrasena,
              user.estado_cuenta.value,
              user.verificado,
              user.avatar_url
          ))
          connection.commit()
          
          return cursor.lastrowid
          
      except Error as e:
          print(f"❌ Error en repository - create_user: {e}")
          return None
      finally:
          if 'cursor' in locals():
              cursor.close()