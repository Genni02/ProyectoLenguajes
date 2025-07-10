from typing import List, Optional, Tuple
from models import VariableUsuario, FuncionPersonalizada, ConstantePublica
from datetime import datetime

class DefinitionsRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    def create_variable(self, variable: VariableUsuario) -> Tuple[bool, str, Optional[int]]:
        """Crea una nueva variable en la base de datos"""
        connection = None
        try:
            print(f"🔗 Intentando conectar a BD para crear variable '{variable.nombre_variable}'")
            connection = self.db_connection.get_connection()
            if not connection:
                print("❌ No se pudo conectar a la base de datos")
                return False, "No se pudo conectar a la base de datos", None
                
            print("✅ Conexión exitosa, ejecutando inserción...")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO variables_usuario (id_usuario, nombre_variable, valor_variable, tipo_valor, descripcion, ultima_modificacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                variable.id_usuario,
                variable.nombre_variable,
                variable.valor_variable,
                variable.tipo_valor,
                variable.descripcion,
                datetime.now()
            ))
            
            variable_id = cursor.lastrowid
            connection.commit()
            print(f"✅ Variable creada con ID: {variable_id}")
            return True, "Variable creada exitosamente", variable_id
            
        except Exception as e:
            print(f"❌ Error al crear variable: {str(e)}")
            if connection:
                connection.rollback()
            return False, f"Error al crear variable: {str(e)}", None
        finally:
            if connection:
                connection.close()
                print("🔗 Conexión cerrada")
    
    def get_user_variables(self, user_id: int) -> Tuple[bool, str, List[VariableUsuario]]:
        """Obtiene todas las variables de un usuario"""
        connection = None
        try:
            print(f"🔗 Intentando conectar a BD para obtener variables del usuario {user_id}")
            connection = self.db_connection.get_connection()
            if not connection:
                print("❌ No se pudo conectar a la base de datos")
                return False, "No se pudo conectar a la base de datos", []
                
            print("✅ Conexión exitosa, ejecutando consulta...")
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_variable, id_usuario, nombre_variable, valor_variable, tipo_valor, descripcion, ultima_modificacion
                FROM variables_usuario
                WHERE id_usuario = %s
                ORDER BY nombre_variable
            """, (user_id,))
            
            rows = cursor.fetchall()
            print(f"📊 Consulta ejecutada, filas encontradas: {len(rows)}")
            variables = []
            
            for row in rows:
                variable = VariableUsuario(row['id_usuario'], row['nombre_variable'], row['valor_variable'])
                variable.id_variable = row['id_variable']
                variable.tipo_valor = row['tipo_valor']
                variable.descripcion = row['descripcion']
                variable.ultima_modificacion = row['ultima_modificacion']
                variables.append(variable)
                print(f"   Variable: {variable.nombre_variable} = {variable.valor_variable}")
                
            message = f"Se encontraron {len(variables)} variables"
            print(f"✅ {message}")
            return True, message, variables
            
        except Exception as e:
            error_msg = f"Error al obtener variables: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg, []
        finally:
            if connection:
                connection.close()
                print("🔗 Conexión cerrada")
    
    def update_variable(self, variable: VariableUsuario) -> Tuple[bool, str]:
        """Actualiza una variable existente"""
        connection = None
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False, "No se pudo conectar a la base de datos"
                
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE variables_usuario
                SET nombre_variable = %s, valor_variable = %s, tipo_valor = %s, descripcion = %s, ultima_modificacion = %s
                WHERE id_variable = %s AND id_usuario = %s
            """, (
                variable.nombre_variable,
                variable.valor_variable,
                variable.tipo_valor,
                variable.descripcion,
                datetime.now(),
                variable.id_variable,
                variable.id_usuario
            ))
            
            if cursor.rowcount > 0:
                connection.commit()
                return True, "Variable actualizada exitosamente"
            else:
                return False, "Variable no encontrada"
                
        except Exception as e:
            if connection:
                connection.rollback()
            return False, f"Error al actualizar variable: {str(e)}"
        finally:
            if connection:
                connection.close()
    
    def delete_variable(self, variable_id: int, user_id: int) -> Tuple[bool, str]:
        """Elimina una variable"""
        connection = None
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False, "No se pudo conectar a la base de datos"
                
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM variables_usuario
                WHERE id_variable = %s AND id_usuario = %s
            """, (variable_id, user_id))
            
            if cursor.rowcount > 0:
                connection.commit()
                return True, "Variable eliminada exitosamente"
            else:
                return False, "Variable no encontrada"
                
        except Exception as e:
            if connection:
                connection.rollback()
            return False, f"Error al eliminar variable: {str(e)}"
        finally:
            if connection:
                connection.close()
    
    def create_function(self, function: FuncionPersonalizada) -> Tuple[bool, str, Optional[int]]:
        """Crea una nueva función personalizada"""
        connection = None
        try:
            print(f"🔗 Intentando conectar a BD para crear función '{function.nombre_funcion}'")
            connection = self.db_connection.get_connection()
            if not connection:
                print("❌ No se pudo conectar a la base de datos")
                return False, "No se pudo conectar a la base de datos", None
                
            print("✅ Conexión exitosa, ejecutando inserción...")
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO funciones_personalizadas (id_usuario, id_categoria, nombre_funcion, definicion_funcion, 
                                                     parametros_funcion, descripcion, ejemplos_uso, es_publica, 
                                                     veces_usada, ultima_modificacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                function.id_usuario,
                function.id_categoria,
                function.nombre_funcion,
                function.definicion_funcion,
                function.parametros_funcion,
                function.descripcion,
                function.ejemplos_uso,
                function.es_publica,
                function.veces_usada,
                datetime.now()
            ))
            
            function_id = cursor.lastrowid
            connection.commit()
            print(f"✅ Función creada con ID: {function_id}")
            return True, "Función creada exitosamente", function_id
            
        except Exception as e:
            print(f"❌ Error al crear función: {str(e)}")
            if connection:
                connection.rollback()
            return False, f"Error al crear función: {str(e)}", None
        finally:
            if connection:
                connection.close()
                print("🔗 Conexión cerrada")
    
    def get_user_functions(self, user_id: int) -> Tuple[bool, str, List[FuncionPersonalizada]]:
        """Obtiene todas las funciones de un usuario"""
        connection = None
        try:
            print(f"🔗 Intentando conectar a BD para obtener funciones del usuario {user_id}")
            connection = self.db_connection.get_connection()
            if not connection:
                print("❌ No se pudo conectar a la base de datos")
                return False, "No se pudo conectar a la base de datos", []
                
            print("✅ Conexión exitosa, ejecutando consulta...")
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_funcion, id_usuario, id_categoria, nombre_funcion, definicion_funcion, 
                       parametros_funcion, descripcion, ejemplos_uso, es_publica, veces_usada, ultima_modificacion
                FROM funciones_personalizadas
                WHERE id_usuario = %s
                ORDER BY nombre_funcion
            """, (user_id,))
            
            rows = cursor.fetchall()
            print(f"📊 Consulta ejecutada, filas encontradas: {len(rows)}")
            functions = []
            
            for row in rows:
                function = FuncionPersonalizada(row['id_usuario'], row['nombre_funcion'], row['definicion_funcion'])
                function.id_funcion = row['id_funcion']
                function.id_categoria = row['id_categoria']
                function.parametros_funcion = row['parametros_funcion']
                function.descripcion = row['descripcion']
                function.ejemplos_uso = row['ejemplos_uso']
                function.es_publica = row['es_publica']
                function.veces_usada = row['veces_usada']
                function.ultima_modificacion = row['ultima_modificacion']
                functions.append(function)
                print(f"   Función: {function.nombre_funcion} = {function.definicion_funcion}")
                
            message = f"Se encontraron {len(functions)} funciones"
            print(f"✅ {message}")
            return True, message, functions
            
        except Exception as e:
            error_msg = f"Error al obtener funciones: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg, []
        finally:
            if connection:
                connection.close()
                print("🔗 Conexión cerrada")
    
    def update_function(self, function: FuncionPersonalizada) -> Tuple[bool, str]:
        """Actualiza una función existente"""
        connection = None
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False, "No se pudo conectar a la base de datos"
                
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE funciones_personalizadas
                SET nombre_funcion = %s, definicion_funcion = %s, parametros_funcion = %s, descripcion = %s, ultima_modificacion = %s
                WHERE id_funcion = %s AND id_usuario = %s
            """, (
                function.nombre_funcion,
                function.definicion_funcion,
                function.parametros_funcion,
                function.descripcion,
                datetime.now(),
                function.id_funcion,
                function.id_usuario
            ))
            
            if cursor.rowcount > 0:
                connection.commit()
                return True, "Función actualizada exitosamente"
            else:
                return False, "Función no encontrada"
                
        except Exception as e:
            if connection:
                connection.rollback()
            return False, f"Error al actualizar función: {str(e)}"
        finally:
            if connection:
                connection.close()
    
    def delete_function(self, function_id: int, user_id: int) -> Tuple[bool, str]:
        """Elimina una función"""
        connection = None
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False, "No se pudo conectar a la base de datos"
                
            cursor = connection.cursor()
            cursor.execute("""
                DELETE FROM funciones_personalizadas
                WHERE id_funcion = %s AND id_usuario = %s
            """, (function_id, user_id))
            
            if cursor.rowcount > 0:
                connection.commit()
                return True, "Función eliminada exitosamente"
            else:
                return False, "Función no encontrada"
                
        except Exception as e:
            if connection:
                connection.rollback()
            return False, f"Error al eliminar función: {str(e)}"
        finally:
            if connection:
                connection.close()