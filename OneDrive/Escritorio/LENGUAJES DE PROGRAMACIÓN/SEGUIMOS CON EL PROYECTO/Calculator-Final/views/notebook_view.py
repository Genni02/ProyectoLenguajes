import tkinter as tk
from tkinter import messagebox, filedialog
import datetime
from utils.styles import get_colors
from utils.operations import operations
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class NotebookView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.operations = operations()
        self.notebook_text = None
        self.last_expression = None 

    def show(self, expression=None):
        if expression is not None:
            self.last_expression = expression  # Guardar la última expresión

        # Limpiar frame anterior SIEMPRE
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # Título principal
        title_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        title_frame.pack(fill=tk.X, pady=10)
        tk.Label(
            title_frame,
            text="🧾 Resolución Detallada",
            font=("Arial", 16, "bold"),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack()
        tk.Label(
            title_frame,
            text="✏️ Área de solución paso a paso",
            font=("Arial", 10, "italic"),
            bg=self.colors['bg'],
            fg="gray"
        ).pack(pady=(5, 0))

        # Área de solución paso a paso
        text_frame = tk.Frame(self.parent_frame, bg=self.colors['bg'])
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.notebook_text = tk.Text(
            text_frame,
            font=("Courier", 11),
            bg=self.colors['operator'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=10,
            pady=10,
            state=tk.NORMAL  # Habilitado para escribir el resultado
        )
        text_scrollbar = tk.Scrollbar(text_frame, command=self.notebook_text.yview)
        self.notebook_text.configure(yscrollcommand=text_scrollbar.set)
        self.notebook_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botón de guardar
        self._create_control_buttons(self.parent_frame)

        # Calcular y mostrar el paso a paso automáticamente
        self.notebook_text.delete("1.0", tk.END)
        expr_to_show = self.last_expression if self.last_expression else expression
        if isinstance(expr_to_show, str) and expr_to_show.strip():
            self._calcular_y_mostrar(expr_to_show.strip())
        else:
            self.notebook_text.insert(tk.END, "No hay expresión para calcular.")
        self.notebook_text.config(state=tk.DISABLED)

    def _create_control_buttons(self, parent):
        """Crea los botones de control"""
        button_frame = tk.Frame(parent, bg=self.colors['bg'])
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

        button_row2 = tk.Frame(button_frame, bg=self.colors['bg'])
        button_row2.pack(fill=tk.X, pady=2)

        tk.Button(
            button_row2,
            text="💾 Guardar paso a paso",
            font=("Arial", 9, "bold"),
            bg="#FFD700",
            fg="#000000",
            relief=tk.RAISED,
            command=self.save_operations
        ).pack(side=tk.LEFT, padx=8, pady=4, ipadx=8, ipady=2)

    def _calcular_y_mostrar(self, expression):
        """Calcula la expresión recibida y muestra el resultado paso a paso en el área principal"""
        content = expression.strip()
        if not content:
            self.notebook_text.insert(tk.END, "No hay expresión para calcular.")
            return

        header = f"{'='*60}\n"
        header += f"🧮 RESULTADOS - {datetime.datetime.now().strftime('%H:%M:%S')}\n"
        header += f"{'='*60}\n\n"
        self.notebook_text.insert(tk.END, header)

        try:
            result_data = self.operations.process_expression(content)
            output = f"Expresión: {content}\n"
            output += self._format_result_with_steps(result_data)
            output += "\n" + "="*50 + "\n\n"
            self.notebook_text.insert(tk.END, output)
            successful_calcs = 1
            errors = 0
        except Exception as e:
            output = f"Expresión: {content}\n"
            output += f"❌ Error: {str(e)}\n\n"
            output += "="*50 + "\n\n"
            self.notebook_text.insert(tk.END, output)
            successful_calcs = 0
            errors = 1

        # Resumen final
        summary = f"\n{'='*40}\n"
        summary += f"📊 RESUMEN FINAL:\n"
        summary += f"• Cálculos exitosos: {successful_calcs}\n"
        summary += f"• Errores: {errors}\n"
        summary += f"• Total procesado: {successful_calcs + errors}\n"
        summary += f"{'='*40}\n"
        self.notebook_text.insert(tk.END, summary)

    def save_operations(self):
        """Guarda el contenido del área de resultados detallados en un archivo PDF"""
        content = self.notebook_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Sin resultados", "No hay resultados para guardar")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ],
            title="Guardar resultado detallado en PDF",
            initialfile=f"resultado_detallado_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )

        if file_path:
            try:
                c = canvas.Canvas(file_path, pagesize=letter)
                width, height = letter
                lines = content.split('\n')
                y = height - 40  # Margen superior

                for line in lines:
                    c.drawString(40, y, line)
                    y -= 15
                    if y < 40:  # Salto de página si se acaba el espacio
                        c.showPage()
                        y = height - 40

                c.save()
                messagebox.showinfo(
                    "Guardado exitoso",
                    f"Resultado detallado guardado en PDF:\n{file_path}"
                )
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el PDF:\n{str(e)}")

    def _format_result_with_steps(self, result_data):
        # Este método debe devolver el string con los pasos detallados
        if isinstance(result_data, dict) and 'steps' in result_data:
            steps = result_data['steps']
            if isinstance(steps, list):
                return "\n".join(str(step) for step in steps)
            else:
                return str(steps)
        elif isinstance(result_data, dict) and 'result' in result_data:
            return str(result_data['result'])
        else:
            return str(result_data)