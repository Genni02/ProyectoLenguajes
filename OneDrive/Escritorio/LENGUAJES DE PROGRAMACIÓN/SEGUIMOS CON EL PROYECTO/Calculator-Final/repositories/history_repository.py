import mysql.connector
from mysql.connector import Error
from typing import Optional, List
from datetime import datetime
from models import HistorialCalculo, TipoCalculo

class HistoryRepository:
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def save_calculation(self, historial: HistorialCalculo) -> Optional[int]:
        """Guarda un cálculo en la base de datos"""
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return None
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO historial_calculos (id_usuario, expresion, resultado, tipo_calculo, 
                                               timestamp_calculo, es_favorito, etiquetas)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            etiquetas_json = None
            if historial.etiquetas:
                import json
                etiquetas_json = json.dumps(historial.etiquetas)
            
            cursor.execute(insert_query, (
                historial.id_usuario,
                historial.expresion,
                historial.resultado,
                historial.tipo_calculo.value,
                historial.timestamp_calculo or datetime.now(),
                historial.es_favorito,
                etiquetas_json
            ))
            connection.commit()
            
            return cursor.lastrowid
            
        except Error as e:
            print(f"❌ Error en repository - save_calculation: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def get_user_history(self, user_id: int, limit: int = 100) -> List[HistorialCalculo]:
        """Obtiene el historial de un usuario"""
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return []
                
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT id_calculo, id_usuario, expresion, resultado, tipo_calculo,
                       timestamp_calculo, es_favorito, etiquetas
                FROM historial_calculos 
                WHERE id_usuario = %s 
                ORDER BY timestamp_calculo DESC 
                LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
            results = cursor.fetchall()
            
            calculations = []
            for row in results:
                calc = HistorialCalculo(
                    id_usuario=row['id_usuario'],
                    expresion=row['expresion'],
                    resultado=row['resultado']
                )
                calc.id_calculo = row['id_calculo']
                calc.tipo_calculo = TipoCalculo(row['tipo_calculo'])
                calc.timestamp_calculo = row['timestamp_calculo']
                calc.es_favorito = row['es_favorito']
                
                # Parsear etiquetas JSON
                if row['etiquetas']:
                    import json
                    calc.etiquetas = json.loads(row['etiquetas'])
                
                calculations.append(calc)
            
            return calculations
            
        except Error as e:
            print(f"❌ Error en repository - get_user_history: {e}")
            return []
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def delete_calculation(self, calculation_id: int) -> bool:
        """Elimina un cálculo específico de la base de datos"""
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            delete_query = "DELETE FROM historial_calculos WHERE id_calculo = %s"
            cursor.execute(delete_query, (calculation_id,))
            connection.commit()
            
            # Verificar si se eliminó alguna fila
            return cursor.rowcount > 0
            
        except Error as e:
            print(f"❌ Error en repository - delete_calculation: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def delete_user_history(self, user_id: int) -> bool:
        """Elimina todo el historial de un usuario"""
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            delete_query = "DELETE FROM historial_calculos WHERE id_usuario = %s"
            cursor.execute(delete_query, (user_id,))
            connection.commit()
            
            return True
            
        except Error as e:
            print(f"❌ Error en repository - delete_user_history: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def save_multiple_calculations(self, calculations: List[HistorialCalculo]) -> bool:
        """Guarda múltiples cálculos en una transacción"""
        try:
            connection = self.db_connection.get_connection()
            if not connection:
                return False
                
            cursor = connection.cursor()
            
            insert_query = """
                INSERT INTO historial_calculos (id_usuario, expresion, resultado, tipo_calculo, 
                                               timestamp_calculo, es_favorito, etiquetas)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            # Preparar datos para inserción múltiple
            data_to_insert = []
            for calc in calculations:
                etiquetas_json = None
                if calc.etiquetas:
                    import json
                    etiquetas_json = json.dumps(calc.etiquetas)
                
                data_to_insert.append((
                    calc.id_usuario,
                    calc.expresion,
                    calc.resultado,
                    calc.tipo_calculo.value,
                    calc.timestamp_calculo or datetime.now(),
                    calc.es_favorito,
                    etiquetas_json
                ))
            
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            
            return True
            
        except Error as e:
            print(f"❌ Error en repository - save_multiple_calculations: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()