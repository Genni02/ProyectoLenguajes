import tkinter as tk
from tkinter import filedialog, messagebox
import json
import csv
import datetime


class ExportView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = app.colors 
        
    def show(self):
        """Muestra la interfaz de exportación mejorada"""
        # Limpiar frame anterior
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
            
        # Título principal
        title_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            title_frame,
            text="📤 Exportar Historial",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack()
        
        # Frame principal de opciones
        options_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        options_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Sección: Qué exportar
        self._create_content_selection(options_frame)
        
        # Sección: Filtro por fechas
        self._create_date_filter(options_frame)
        
        # Sección: Formatos de exportación
        self._create_export_buttons(options_frame)
        
        # Resumen de datos
        self._create_export_summary(options_frame)
    
    def _create_content_selection(self, parent):
        """Crea la sección de selección de contenido"""
        what_frame = tk.LabelFrame(
            parent,
            text="📋 ¿Qué deseas exportar?",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED,
            bd=2
        )
        what_frame.pack(fill=tk.X, pady=10)
        
        self.export_option = tk.StringVar(value="all")
        
        options = [
            ("📚 Todo el historial", "all"),
            ("⭐ Solo favoritos", "favorites"),
            ("💾 Operaciones guardadas", "saved")
        ]
        
        for text, value in options:
            tk.Radiobutton(
                what_frame,
                text=text,
                variable=self.export_option,
                value=value,
                font=("Arial", 11),
                bg=self.colors['bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['numeric']
            ).pack(anchor="w", padx=10, pady=5)
    
    def _create_date_filter(self, parent):
        """Crea la sección de filtro por fechas"""
        date_frame = tk.LabelFrame(
            parent,
            text="📅 Filtro por fechas (opcional)",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED,
            bd=2
        )
        date_frame.pack(fill=tk.X, pady=10)
        
        self.use_date_filter = tk.BooleanVar()
        date_check = tk.Checkbutton(
            date_frame,
            text="🔍 Usar filtro de fechas",
            variable=self.use_date_filter,
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            selectcolor=self.colors['numeric'],
            command=self._toggle_date_filter
        )
        date_check.pack(anchor="w", padx=10, pady=5)
        
        # Frame para entradas de fecha
        self.date_entries_frame = tk.Frame(date_frame, bg=self.colors['bg'])
        self.date_entries_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # Fecha desde
        from_frame = tk.Frame(self.date_entries_frame, bg=self.colors['bg'])
        from_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            from_frame,
            text="Desde:",
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.from_date = tk.Entry(
            from_frame,
            font=("Arial", 10),
            width=12,
            state=tk.DISABLED
        )
        self.from_date.pack(side=tk.LEFT, padx=5)
        self.from_date.insert(0, "2025-01-01")
        
        # Fecha hasta
        to_frame = tk.Frame(self.date_entries_frame, bg=self.colors['bg'])
        to_frame.pack(fill=tk.X, pady=2)
        
        tk.Label(
            to_frame,
            text="Hasta:",
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.to_date = tk.Entry(
            to_frame,
            font=("Arial", 10),
            width=12,
            state=tk.DISABLED
        )
        self.to_date.pack(side=tk.LEFT, padx=5)
        self.to_date.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
    
    def _create_export_buttons(self, parent):
        """Crea los botones de exportación"""
        format_frame = tk.LabelFrame(
            parent,
            text="⬇️ Formato de exportación",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED,
            bd=2
        )
        format_frame.pack(fill=tk.X, pady=10)
        
        # Botones de exportación modernos
        export_buttons_frame = tk.Frame(format_frame, bg=self.colors['bg'])
        export_buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # MODIFICADO: Aseguramos que cada botón llama a export_data con el formato correcto
        pdf_btn = tk.Button(
            export_buttons_frame,
            text="📄 Exportar PDF",
            font=("Arial", 11, "bold"),
            bg="#DC2626",
            fg="white",
            relief=tk.FLAT,
            width=15,
            height=2,
            command=lambda: self.export_data("pdf")
        )
        pdf_btn.pack(side=tk.LEFT, padx=5)

        excel_btn = tk.Button(
            export_buttons_frame,
            text="📊 Exportar Excel",
            font=("Arial", 11, "bold"),
            bg="#059669",
            fg="white",
            relief=tk.FLAT,
            width=15,
            height=2,
            command=lambda: self.export_data("excel")
        )
        excel_btn.pack(side=tk.LEFT, padx=5)

        txt_btn = tk.Button(
            export_buttons_frame,
            text="📝 Exportar TXT",
            font=("Arial", 11, "bold"),
            bg=self.colors['operator'],
            fg="white",
            relief=tk.FLAT,
            width=15,
            height=2,
            command=lambda: self.export_data("txt")
        )
        txt_btn.pack(side=tk.LEFT, padx=5)
        
        # Separador
        tk.Frame(format_frame, height=1, bg=self.colors['text']).pack(fill=tk.X, padx=10, pady=5)
        
        # Botones de formatos originales
        original_frame = tk.Frame(format_frame, bg=self.colors['bg'])
        original_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            original_frame,
            text="Formatos básicos:",
            font=("Arial", 10),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor="w")
        
        basic_buttons_frame = tk.Frame(original_frame, bg=self.colors['bg'])
        basic_buttons_frame.pack(fill=tk.X, pady=5)
        
        self.format_var = tk.StringVar(value="json")
        formats = [("JSON", "json"), ("CSV", "csv")]
        
        for text, value in formats:
            rb = tk.Radiobutton(
                basic_buttons_frame,
                text=text,
                variable=self.format_var,
                value=value,
                bg=self.colors['bg'],
                fg=self.colors['text'],
                selectcolor=self.colors['bg']
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Botón de exportar básico
        basic_export_button = tk.Button(
            basic_buttons_frame,
            text="📤 Exportar básico",
            font=("Arial", 10),
            bg=self.colors['numeric'],
            fg=self.colors['text'],
            command=self.export_history
        )
        basic_export_button.pack(side=tk.LEFT, padx=10)
    
    def _create_export_summary(self, parent):
        """Crea el resumen de exportación"""
        summary_frame = tk.LabelFrame(
            parent,
            text="📊 Resumen de datos",
            font=("Arial", 12, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text'],
            relief=tk.RAISED,
            bd=2
        )
        summary_frame.pack(fill=tk.X, pady=10)
        
        self.summary_text = tk.Text(
            summary_frame,
            height=4,
            font=("Courier", 10),
            bg=self.colors['text'],
            fg=self.colors['display'],
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.summary_text.pack(fill=tk.X, padx=10, pady=10)
        
        # Actualizar resumen inicial
        self._update_export_summary()
        
        # Botón para actualizar resumen
        refresh_button = tk.Button(
            summary_frame,
            text="🔄 Actualizar resumen",
            font=("Arial", 9),
            bg=self.colors['numeric'],
            fg=self.colors['text'],
            relief=tk.FLAT,
            command=self._update_export_summary
        )
        refresh_button.pack(pady=5)
    
    def _toggle_date_filter(self):
        """Activa/desactiva el filtro de fechas"""
        if self.use_date_filter.get():
            self.from_date.config(state=tk.NORMAL)
            self.to_date.config(state=tk.NORMAL)
        else:
            self.from_date.config(state=tk.DISABLED)
            self.to_date.config(state=tk.DISABLED)
    
    def _update_export_summary(self):
        """Actualiza el resumen de exportación"""
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        
        # Usar la misma lógica de filtrado que history_view.py
        filtered_history = self._get_filtered_history()
        total_favorites = len(getattr(self.app, 'favorites', []))
        total_saved = len(getattr(self.app, 'saved_operations', []))
        
        summary = f"📈 Estadísticas de datos:\n"
        summary += f"• Total historial filtrado: {len(filtered_history)} cálculos\n"
        summary += f"• Total favoritos: {total_favorites} elementos\n"
        summary += f"• Total guardados: {total_saved} operaciones\n"
        
        if hasattr(self.app, 'current_user') and self.app.current_user:
            summary += f"• Usuario actual: {self.app.current_user}"
        else:
            summary += f"• Modo: Anónimo"
        
        self.summary_text.insert("1.0", summary)
        self.summary_text.config(state=tk.DISABLED)
    
    def _get_filtered_history(self):
        """Aplica el mismo filtro de history_view.py para eliminar duplicados y entradas vacías"""
        if not hasattr(self.app, 'history') or not self.app.history:
            return []
        
        # Usar la misma lógica de filtrado que en history_view.py
        seen = set()
        filtered_history = []
        
        for entry in self.app.history:
            if entry and 'expression' in entry and 'result' in entry:
                # Crear una clave única para detectar duplicados
                key = (entry['expression'], entry['result'])
                if key not in seen:
                    seen.add(key)
                    filtered_history.append(entry)
        
        # Devolver en orden inverso (más reciente primero) como en history_view.py
        return list(reversed(filtered_history))
    
    def export_data(self, format_type):
        """Exporta los datos en el formato especificado (nueva funcionalidad)"""
        try:
            # Obtener datos según la opción seleccionada
            data_to_export = self._get_export_data()
            
            if not data_to_export:
                messagebox.showwarning("Sin datos", "No hay datos para exportar con los filtros seleccionados.")
                return
            
            # Solicitar ubicación de guardado
            file_path = self._get_save_path(format_type)
            if not file_path:
                return
            
            # Exportar según el formato
            if format_type == "pdf":
                self._export_to_pdf(data_to_export, file_path)
            elif format_type == "excel":
                self._export_to_excel(data_to_export, file_path)
            elif format_type == "txt":
                self._export_to_txt_notebook_style(data_to_export, file_path)
            
            messagebox.showinfo("Exportación exitosa", f"Datos exportados a:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error de exportación", f"Error al exportar: {str(e)}")
    
    def _get_export_data(self):
        """Obtiene los datos a exportar según las opciones seleccionadas"""
        option = self.export_option.get()
        
        if option == "all":
            # Usar la misma lógica de filtrado que history_view.py
            data = self._get_filtered_history()
        elif option == "favorites":
            data = getattr(self.app, 'favorites', []).copy()
        elif option == "saved":
            data = getattr(self.app, 'saved_operations', []).copy()
        else:
            data = []
        
        # Aplicar filtro de fechas si está activado
        if hasattr(self, 'use_date_filter') and self.use_date_filter.get() and data:
            data = self._filter_by_date(data)
        
        return data
    
    def _filter_by_date(self, data):
        """Filtra los datos por rango de fechas"""
        try:
            from_date = datetime.datetime.strptime(self.from_date.get(), "%Y-%m-%d")
            to_date = datetime.datetime.strptime(self.to_date.get(), "%Y-%m-%d")
            to_date = to_date.replace(hour=23, minute=59, second=59)
            
            filtered_data = []
            for item in data:
                if 'timestamp' in item:
                    try:
                        item_date = datetime.datetime.fromisoformat(item['timestamp'])
                        if from_date <= item_date <= to_date:
                            filtered_data.append(item)
                    except:
                        filtered_data.append(item)  # Incluir si no se puede parsear la fecha
                else:
                    filtered_data.append(item)  # Incluir si no tiene timestamp
            
            return filtered_data
        except:
            return data
    
    def _get_save_path(self, format_type):
        """Obtiene la ruta donde guardar el archivo"""
        extensions = {
            "pdf": [("PDF files", "*.pdf")],
            "excel": [("Excel files", "*.xlsx")],
            "txt": [("Text files", "*.txt")]
        }
        
        default_name = f"calculadora_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return filedialog.asksaveasfilename(
            defaultextension=f".{format_type}",
            filetypes=extensions[format_type],
            initialfile=default_name,
            title=f"Guardar como {format_type.upper()}"
        )
    
    def _export_to_txt_notebook_style(self, data, file_path):
        """Exporta los datos a formato TXT usando el estilo de notebook_view.py"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # Encabezado similar al notebook_view.py
                f.write("="*60 + "\n")
                f.write("HISTORIAL DE OPERACIONES - CALCULADORA CIENTÍFICA\n")
                f.write("="*60 + "\n\n")
                
                # Información del reporte
                f.write(f"Fecha de exportación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Usuario: {getattr(self.app, 'current_user', 'Anónimo') or 'Anónimo'}\n")
                f.write(f"Total de registros: {len(data)}\n")
                f.write(f"Tipo de exportación: {self.export_option.get().replace('_', ' ').title()}\n")
                
                # Aplicar filtro por fechas si está activo
                if hasattr(self, 'use_date_filter') and self.use_date_filter.get():
                    f.write(f"Filtro de fechas: {self.from_date.get()} a {self.to_date.get()}\n")
                
                f.write("\nDETALLE DE OPERACIONES:\n")
                f.write("-" * 30 + "\n\n")
                
                # Procesar cada entrada usando el estilo de notebook_view.py
                for i, operation in enumerate(data, 1):
                    f.write(f"Operación #{i:03d}:\n")
                    f.write(f"Expresión: {operation.get('expression', 'N/A')}\n")
                    f.write(f"Resultado: {operation.get('result', 'N/A')}\n")
                    
                    # Formatear fecha si existe
                    if 'timestamp' in operation:
                        try:
                            timestamp = datetime.datetime.fromisoformat(operation['timestamp'])
                            f.write(f"Fecha: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                        except:
                            f.write(f"Fecha: {operation['timestamp']}\n")
                    
                    # Agregar título si es una operación guardada
                    if 'title' in operation:
                        f.write(f"Título: {operation['title']}\n")
                    
                    f.write("-" * 40 + "\n\n")
                
                # Resumen final al estilo notebook_view.py
                f.write("\n" + "="*40 + "\n")
                f.write("📊 RESUMEN FINAL:\n")
                f.write(f"• Total de operaciones exportadas: {len(data)}\n")
                f.write(f"• Formato de exportación: TXT (estilo notebook)\n")
                f.write(f"• Generado el: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*40 + "\n")
                f.write("🎯 Fin del reporte de exportación\n")
                f.write("="*40 + "\n")
                
        except Exception as e:
            raise Exception(f"Error al escribir archivo TXT: {str(e)}")
    
    def _export_to_txt_advanced(self, data, file_path):
        """Método alternativo de exportación TXT (mantener para compatibilidad)"""
        self._export_to_txt_notebook_style(data, file_path)
    
    def _export_to_excel(self, data, file_path):
        """Exporta los datos a formato Excel"""
        try:
            import pandas as pd
            import openpyxl
            
            # Preparar datos para DataFrame
            export_data = []
            for item in data:
                row = {
                    'Expresión': item.get('expression', 'N/A'),
                    'Resultado': str(item.get('result', 'N/A')),
                    'Fecha': item.get('timestamp', 'N/A'),
                    'Título': item.get('title', '')
                }
                export_data.append(row)
            
            # Crear DataFrame y exportar
            df = pd.DataFrame(export_data)
            
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Historial', index=False)
                
                # Configurar formato
                workbook = writer.book
                worksheet = writer.sheets['Historial']
                
                # Ajustar ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                    
        except ImportError:
            # Si no están las librerías, mostrar error y no exportar
            raise Exception("Para exportar a Excel, necesitas instalar: pip install pandas openpyxl")

    
    def _export_to_csv_advanced(self, data, file_path):
        """Exporta a CSV como alternativa a Excel"""
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Encabezados
            writer.writerow(['Expresión', 'Resultado', 'Fecha', 'Hora', 'Título'])
            
            # Datos
            for item in data:
                if 'timestamp' in item:
                    try:
                        timestamp = datetime.datetime.fromisoformat(item['timestamp'])
                        fecha = timestamp.strftime('%Y-%m-%d')
                        hora = timestamp.strftime('%H:%M:%S')
                    except:
                        fecha = item.get('timestamp', 'N/A')
                        hora = 'N/A'
                else:
                    fecha = 'N/A'
                    hora = 'N/A'
                
                writer.writerow([
                    item.get('expression', 'N/A'),
                    item.get('result', 'N/A'),
                    fecha,
                    hora,
                    item.get('title', 'N/A')
                ])
    
    def _export_to_pdf(self, data, file_path):
        """Exporta los datos a formato PDF"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            
            # Crear documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            
            story.append(Paragraph("🧮 CALCULADORA CIENTÍFICA RETRO", title_style))
            story.append(Paragraph("Reporte de Exportación", styles['Heading2']))
            story.append(Spacer(1, 12))
            
            # Información del reporte
            info_data = [
                ['Fecha de exportación:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Usuario:', getattr(self.app, 'current_user', 'Anónimo') or 'Anónimo'],
                ['Total de registros:', str(len(data))],
                ['Tipo de datos:', getattr(self, 'export_option', tk.StringVar()).get().replace('_', ' ').title()]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Tabla de datos
            if data:
                story.append(Paragraph("Detalle de Cálculos", styles['Heading3']))
                story.append(Spacer(1, 12))
                
                # Encabezados de tabla
                table_data = [['#', 'Expresión', 'Resultado', 'Fecha']]
                
                # Datos
                for i, item in enumerate(data, 1):
                    if 'timestamp' in item:
                        try:
                            timestamp = datetime.datetime.fromisoformat(item['timestamp'])
                            fecha_str = timestamp.strftime('%Y-%m-%d %H:%M')
                        except:
                            fecha_str = str(item.get('timestamp', 'N/A'))[:16]
                    else:
                        fecha_str = 'N/A'
                    
                    expression = str(item.get('expression', 'N/A'))
                    result = str(item.get('result', 'N/A'))
                    
                    table_data.append([
                        str(i),
                        expression[:30] + ('...' if len(expression) > 30 else ''),
                        result[:20] + ('...' if len(result) > 20 else ''),
                        fecha_str
                    ])
                
                data_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 2*inch, 1.5*inch])
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(data_table)
            
            # Construir PDF
            doc.build(story)
            
        except ImportError:
            messagebox.showinfo("Instalando dependencia", "reportlab no está instalado. Exportando como TXT...")
            self._export_to_txt_notebook_style(data, file_path.replace('.pdf', '.txt'))
    
    # Mantener métodos originales para compatibilidad
    def export_history(self):
        """Exporta el historial al formato seleccionado (método original)"""
        # Usar la misma lógica de filtrado que history_view.py
        filtered_history = self._get_filtered_history()
        
        if not filtered_history:
            messagebox.showwarning("Exportar", "No hay historial para exportar")
            return
            
        file_types = {
            "json": [("JSON files", "*.json")],
            "txt": [("Text files", "*.txt")],
            "csv": [("CSV files", "*.csv")]
        }
        
        file_ext = {
            "json": ".json",
            "txt": ".txt",
            "csv": ".csv"
        }
        
        format = self.format_var.get()
        file_path = filedialog.asksaveasfilename(
            defaultextension=file_ext[format],
            filetypes=file_types[format],
            title="Guardar historial como"
        )
        
        if not file_path:
            return
            
        try:
            if format == "json":
                self.export_to_json(file_path, filtered_history)
            elif format == "txt":
                # Usar el nuevo método de exportación TXT
                self._export_to_txt_notebook_style(filtered_history, file_path)
            elif format == "csv":
                self.export_to_csv(file_path, filtered_history)
                
            messagebox.showinfo("Exportar", "Historial exportado exitosamente!")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {str(e)}")
            
    def export_to_json(self, file_path, data):
        """Exporta el historial a JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    def export_to_text(self, file_path, data):
        """Exporta el historial a texto (método original - redirige al nuevo)"""
        self._export_to_txt_notebook_style(data, file_path)
                
    def export_to_csv(self, file_path, data):
        """Exporta el historial a CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Expresión", "Resultado", "Fecha"])
            for entry in data:
                writer.writerow([
                    entry.get('expression', 'N/A'), 
                    entry.get('result', 'N/A'), 
                    entry.get('timestamp', 'N/A')
                ])