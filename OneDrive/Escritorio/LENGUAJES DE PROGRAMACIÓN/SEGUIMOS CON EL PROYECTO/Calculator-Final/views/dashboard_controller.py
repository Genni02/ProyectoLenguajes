import mysql.connector
from datetime import datetime, timedelta

class DashboardController:
    def __init__(self, host='localhost', user='root', password='', database='calculadora_db'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def get_total_operaciones(self, id_usuario=None, rango='mes'):
     cursor = self.conn.cursor()
     if id_usuario:
        cursor.execute("SELECT COUNT(*) FROM operaciones WHERE id_usuario = %s AND fecha >= CURDATE() - INTERVAL 1 MONTH", (id_usuario,))
     else:
        cursor.execute("SELECT COUNT(*) FROM operaciones WHERE fecha >= CURDATE() - INTERVAL 1 MONTH")
     result = cursor.fetchone()
     return result[0] if result else 0


    def get_funcion_mas_usada(self, id_usuario=None):
        query = """
            SELECT nombre_funcion, veces_usada 
            FROM funciones_personalizadas
            WHERE es_publica = TRUE
        """
        if id_usuario:
            query += " AND id_usuario = %s"
            self.cursor.execute(query + " ORDER BY veces_usada DESC LIMIT 1", (id_usuario,))
        else:
            self.cursor.execute(query + " ORDER BY veces_usada DESC LIMIT 1")

        return self.cursor.fetchone()

    def get_tipo_calculo_mas_usado(self, id_usuario=None):
        query = """
            SELECT tipo_calculo, COUNT(*) AS total
            FROM historial_calculos
        """
        if id_usuario:
            query += " WHERE id_usuario = %s"
            self.cursor.execute(query + " GROUP BY tipo_calculo ORDER BY total DESC LIMIT 1", (id_usuario,))
        else:
            self.cursor.execute(query + " GROUP BY tipo_calculo ORDER BY total DESC LIMIT 1")

        return self.cursor.fetchone()

    def get_promedio_diario(self, id_usuario=None):
        query = """
            SELECT ROUND(COUNT(*) / COUNT(DISTINCT DATE(timestamp_calculo)), 2) AS promedio_diario
            FROM historial_calculos
        """
        if id_usuario:
            query += " WHERE id_usuario = %s"
            self.cursor.execute(query, (id_usuario,))
        else:
            self.cursor.execute(query)
        return self.cursor.fetchone()['promedio_diario']

    def get_dia_con_mayor_actividad(self, id_usuario=None):
        query = """
            SELECT DATE(timestamp_calculo) AS dia, COUNT(*) AS total
            FROM historial_calculos
        """
        if id_usuario:
            query += " WHERE id_usuario = %s"
            self.cursor.execute(query + " GROUP BY dia ORDER BY total DESC LIMIT 1", (id_usuario,))
        else:
            self.cursor.execute(query + " GROUP BY dia ORDER BY total DESC LIMIT 1")
        return self.cursor.fetchone()

    def cerrar_conexion(self):
        self.cursor.close()
        self.conn.close()
