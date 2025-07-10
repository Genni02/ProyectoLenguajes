from tkinter import messagebox
from typing import Optional
from services import HistoryService
from repositories import HistoryRepository
from models import TipoCalculo
from datetime import datetime

class HistoryController:
    def __init__(self, app):
        self.app = app
        self.history_repository = HistoryRepository(app.db_connection)
        self.history_service = HistoryService(self.history_repository)
    
    def add_calculation(self, expression: str, result: str, calc_type: TipoCalculo = TipoCalculo.BASICO):
      """Añade un cálculo al historial (memoria o BD según el estado del usuario)"""
      # Crear timestamp UNA sola vez
      current_timestamp = self.get_current_timestamp()
      
      # Crear entrada en formato legacy para compatibilidad
      entry = {
          'expression': expression,
          'result': result,
          'timestamp': current_timestamp,  # Usar el mismo timestamp
          'type': calc_type.value,
      }
      
      existing_entry = next((
          e for e in self.app.history 
          if e['expression'] == expression and 
            e['result'] == result and 
            abs((self.parse_timestamp(e['timestamp']) - self.parse_timestamp(current_timestamp)).total_seconds()) < 1
      ), None)
      
      if existing_entry:
          print("⚠️ Entrada duplicada detectada, no se añadirá")
          return
      
      # Siempre añadir a memoria local primero
      self.app.history.append(entry)
      
      # Si está autenticado, también guardar en BD
      if self.is_user_authenticated():
          user_id = self.app.current_user['id']
          success, message = self.history_service.save_calculation(
              user_id, expression, result, calc_type
          )
          if success:
              # Actualizar la entrada con el ID de la BD
              entry['id'] = self.get_last_calculation_id(user_id)
          else:
              print(f"⚠️ Error al guardar en BD: {message}")
    
    def use_expression_in_calculator(self, expression: str):
        """Cambia a la vista de calculadora y coloca la expresión"""
        self.app.show_view('calculator')
        # Esperar a que la vista esté lista y luego colocar la expresión
        calculator_view = self.app.views['calculator']
        calculator_view.set_expression(expression)

    def parse_timestamp(self, timestamp_str):
      """Convierte string timestamp a datetime object"""
      try:
          # Intentar primero con fromisoformat si está disponible
          if hasattr(datetime, 'fromisoformat'):
              return datetime.fromisoformat(timestamp_str)
          else:
              # Fallback para versiones antiguas de Python
              return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
      except ValueError:
          try:
              # Intentar sin microsegundos
              return datetime.datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
          except ValueError:
              # Fallback final
              return datetime.datetime.now()
        
    def delete_entry(self, entry):
        """Elimina una entrada específica del historial"""
        if self.is_user_authenticated() and 'id' in entry:
            # Usuario autenticado: eliminar de BD y memoria
            calc_id = entry['id']
            success, message = self.history_service.delete_calculation(calc_id)
            
            if success:
                # Eliminar de memoria local también
                if entry in self.app.history:
                    self.app.history.remove(entry)
                return True, "Cálculo eliminado correctamente"
            else:
                return False, message
        else:
            # Usuario anónimo: solo eliminar de memoria
            if entry in self.app.history:
                self.app.history.remove(entry)
                return True, "Cálculo eliminado de la sesión actual"
            else:
                return False, "No se pudo encontrar el cálculo"
    
    def get_last_calculation_id(self, user_id: int) -> Optional[int]:
        """Obtiene el ID del último cálculo guardado"""
        try:
            calculations = self.history_repository.get_user_history(user_id, limit=1)
            if calculations:
                return calculations[0].id_calculo
            return None
        except:
            return None
    
    def on_user_login(self):
        """Maneja el evento cuando un usuario inicia sesión"""
        if not self.is_user_authenticated():
            return
        
        user_id = self.app.current_user['id']
        
        # Si hay historial anónimo, preguntar si migrar
        if self.app.history:
            if messagebox.askyesno(
                "Guardar Historial",
                f"Tienes {len(self.app.history)} cálculos en tu sesión anónima.\n"
                "¿Deseas guardarlos en tu cuenta?",
                icon="question"
            ):
                success, message = self.history_service.migrate_anonymous_history(
                    self.app.history, user_id
                )
                if success:
                    messagebox.showinfo("Migración Completa", message)
                else:
                    messagebox.showerror("Error de Migración", message)
        
        # Cargar historial existente de la BD
        self.load_user_history_from_db()
    
    def load_user_history_from_db(self):
        """Carga el historial del usuario desde la base de datos"""
        if not self.is_user_authenticated():
            return
        
        user_id = self.app.current_user['id']
        db_history, message = self.history_service.load_user_history(user_id)
        
        if db_history:
            # Combinar historial local con el de BD, evitando duplicados
            combined_history = self.merge_histories(self.app.history, db_history)
            self.app.history = combined_history
            print(f"📚 {message}")
        else:
            print(f"⚠️ {message}")
    
    def merge_histories(self, local_history, db_history):
        """Combina historiales local y de BD, eliminando duplicados"""
        # Crear un set de entradas únicas basado en expresión + resultado + timestamp
        seen_entries = set()
        merged_history = []
        
        # Priorizar historial de BD
        for entry in db_history:
            key = (entry['expression'], entry['result'], entry['timestamp'])
            if key not in seen_entries:
                seen_entries.add(key)
                merged_history.append(entry)
        
        # Añadir entradas locales que no estén duplicadas
        for entry in local_history:
            key = (entry['expression'], entry['result'], entry['timestamp'])
            if key not in seen_entries:
                seen_entries.add(key)
                merged_history.append(entry)
        
        # Ordenar por timestamp (más reciente primero)
        merged_history.sort(key=lambda x: x['timestamp'], reverse=True)
        return merged_history
    
    def on_user_logout(self):
        """Maneja el evento cuando un usuario cierra sesión"""
        # Limpiar historial cargado de BD
        self.app.history.clear()
        print("🧹 Historial limpiado al cerrar sesión")
    
    def clear_history(self):
        """Limpia el historial según el estado del usuario"""
        if self.is_user_authenticated():
            # Usuario autenticado: limpiar BD y memoria
            if messagebox.askyesno(
                "Limpiar Historial",
                "¿Estás seguro de que deseas eliminar todo tu historial?\n"
                "Esta acción no se puede deshacer.",
                icon="warning"
            ):
                user_id = self.app.current_user['id']
                success, message = self.history_service.clear_user_history(user_id)
                
                if success:
                    self.app.history.clear()
                    return True, message
                else:
                    return False, message
        else:
            # Usuario anónimo: solo limpiar memoria
            if messagebox.askyesno(
                "Limpiar Historial",
                "¿Estás seguro de que deseas eliminar todo el historial de esta sesión?",
                icon="warning"
            ):
                self.app.history.clear()
                return True, "Historial de sesión eliminado"
        
        return False, "Operación cancelada"
    
    def is_user_authenticated(self):
        """Verifica si el usuario está autenticado"""
        return (self.app.current_user and 
                self.app.current_user.get("mode") == "authenticated" and
                self.app.current_user.get("id") is not None)
    
    def get_current_timestamp(self):
        """Obtiene el timestamp actual en formato ISO"""
        from datetime import datetime
        return datetime.now().isoformat()