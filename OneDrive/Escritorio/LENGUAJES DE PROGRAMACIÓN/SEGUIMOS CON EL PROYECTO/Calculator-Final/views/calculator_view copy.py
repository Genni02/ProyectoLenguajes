import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from utils.styles import get_colors
from utils.operations import operations
from tkinter import font as tkfont

class RoundedButton(tk.Canvas):
    def __init__(self, master=None, text="", radius=25, btnforeground="#000000", btnbackground="#ffffff", 
                 clicked=None, *args, **kwargs):
        super(RoundedButton, self).__init__(master, *args, **kwargs)
        self.config(bg=self.master['bg'], highlightthickness=0)
        self.btnbackground = btnbackground
        self.btnforeground = btnforeground
        self.clicked = clicked
        self.radius = radius
        self.text_content = text
        self._click_in_progress = False  # Prevenir clics múltiples 
        
        # No crear el texto aquí, lo haremos en el método draw
        self.text_id = None
        self.rect_id = None
        
        self.bind("<Configure>", self.draw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw(self, event=None):
        self.delete("all")  # Limpiar todo el canvas
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        if width <= 1 or height <= 1:  # Evitar dibujar si las dimensiones son inválidas
            return
        
        # Crear el rectángulo redondeado primero
        self.rect_id = self.create_round_rect(0, 0, width, height, self.radius, 
                                            fill=self.btnbackground, outline="")
        
        # Crear el texto centrado
        self.text_id = self.create_text(width/2, height/2, 
                                      text=self.text_content, 
                                      fill=self.btnforeground, 
                                      font=("Helvetica", 10, "bold"))
        
        # Asegurarse de que el texto esté sobre el rectángulo
        self.tag_raise(self.text_id)
        
        # NO configurar bindings adicionales aquí para evitar duplicados
        
    def create_round_rect(self, x1, y1, x2, y2, r=25, **kwargs):
        points = (x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, 
                 x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1)
        return self.create_polygon(points, **kwargs, smooth=True)
        
    def on_click(self, event=None):
        # Prevenir clics múltiples
        if self._click_in_progress:
            return
            
        self._click_in_progress = True
        
        if self.clicked:
            try:
                self.clicked()
            except Exception as e:
                print(f"Error en click: {e}")
        
        self.on_leave(None)
        
        # Resetear flag después de un breve delay
        self.after(100, lambda: setattr(self, '_click_in_progress', False))
        
    def on_enter(self, event):
        if self.rect_id:  # Verificar que existe
            self.itemconfig(self.rect_id, fill=self.lighten_color(self.btnbackground, 20))
        
    def on_leave(self, event):
        if self.rect_id:  # Verificar que existe
            self.itemconfig(self.rect_id, fill=self.btnbackground)
        
    def lighten_color(self, color, amount):
        """Aclara el color en la cantidad especificada"""
        from colorsys import rgb_to_hls, hls_to_rgb
        import re
        
        match = re.match(r'#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', color.lower())
        if match:
            r, g, b = [int(x, 16) for x in match.groups()]
        else:
            return color
            
        h, l, s = rgb_to_hls(r/255, g/255, b/255)
        l = min(1, l * (1 + amount/100))
        r, g, b = [int(x*255) for x in hls_to_rgb(h, l, s)]
        return f'#{r:02x}{g:02x}{b:02x}'

class CalculatorView:
    def __init__(self, app, parent_frame):
        self.app = app
        self.parent_frame = parent_frame
        self.colors = get_colors()
        self.setup_styles()
        self.setup_fonts()
        self.current_calculation = None
        # Inicializar el motor de operaciones
        self.operations = operations()
        
    def setup_styles(self):
        """Configura los estilos personalizados"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configurar el estilo del notebook
        self.style.configure('TNotebook', background=self.colors['bg'])
        self.style.configure('TNotebook.Tab', 
                           background=self.colors['numeric'],
                           foreground=self.colors['text_dark'],
                           font=('Helvetica', 10, 'bold'),
                           padding=[10, 5],
                           borderwidth=0)
        self.style.map('TNotebook.Tab', 
                      background=[('selected', self.colors['primary'])],
                      foreground=[('selected', 'white')])
        
        # Configurar estilo para los frames con bordes redondeados
        self.style.configure('Rounded.TFrame', 
                           background=self.colors['bg'],
                           borderwidth=0,
                           relief='flat')
        
    def setup_fonts(self):
        """Configura las fuentes personalizadas"""
        self.title_font = tkfont.Font(family='Helvetica', size=12, weight='bold')
        self.subtitle_font = tkfont.Font(family='Helvetica', size=11)
        self.entry_font = tkfont.Font(family='Consolas', size=12)
        self.result_font = tkfont.Font(family='Consolas', size=11)
        self.button_font = tkfont.Font(family='Helvetica', size=10, weight='bold')
        
    def show(self):
        """Muestra la interfaz principal de la calculadora"""
        self.create_symbol_panels_area()
        self.create_input_area()
        self.create_results_area()
        
    def create_rounded_frame(self, parent, **kwargs):
        """Crea un frame con bordes redondeados"""
        frame = tk.Frame(parent, bg=self.colors['bg'], **kwargs)
        return frame
        
    def create_symbol_panels_area(self):
        """Área de paneles de símbolos con pestañas y diseño moderno"""
        container = self.create_rounded_frame(self.parent_frame)
        container.pack(fill=tk.X, padx=15, pady=(15, 10))
        
        # Sombra sutil
        shadow = tk.Frame(container, bg='#e0e0e0')
        shadow.pack(fill=tk.X, pady=(0, 2))
        
        # Frame principal de los símbolos
        symbols_frame = self.create_rounded_frame(container)
        symbols_frame.pack(fill=tk.X, padx=1, pady=1)
        
        notebook = ttk.Notebook(symbols_frame, style='TNotebook')
        notebook.pack(fill=tk.X, padx=5, pady=5)
        
        tabs = {
            "Básicas": ["+", "-", "*", "/", "%", "^", "(", ")", "√", "π", "e"],
            "Variables": ["α", "β", "γ", "θ", "λ", "μ", "σ", "φ", "ψ", "ω", "x", "y"],
            "Trigonométricas": ["sin", "cos", "tan", "cot", "sec", "csc", "asin", "acos", "atan"],
            "Logarítmicas": ["log", "ln", "log10", "exp", "log2"],
            "Cálculo": ["∫", "∂", "Σ", "∏", "lim", "d/dx"],
            "Matrices": ["[", "]", "det", "inv", "T", "×"]
        }

        for tab, symbols in tabs.items():
            frame = self.create_rounded_frame(notebook, padx=5, pady=5)
            notebook.add(frame, text=f"   {tab}   ")
            
            for idx, symbol in enumerate(symbols):
                # Crear función lambda con captura correcta del símbolo
                def create_click_handler(s):
                    return lambda: self.insert_symbol(s)
                
                RoundedButton(
                    frame,
                    text=symbol,
                    radius=15,
                    btnbackground=self.colors['numeric'],
                    btnforeground=self.colors['text_dark'],
                    width=60,
                    height=30,
                    clicked=create_click_handler(symbol)
                ).grid(row=idx // 6, column=idx % 6, padx=3, pady=3, sticky='nsew')
                
            # Configurar expansión uniforme de columnas
            for i in range(6):
                frame.grid_columnconfigure(i, weight=1)
                
    def create_input_area(self):
        """Campo de ingreso de expresiones con diseño moderno"""
        container = self.create_rounded_frame(self.parent_frame)
        container.pack(fill=tk.X, padx=15, pady=10)
        
        # Sombra sutil
        shadow = tk.Frame(container, bg='#e0e0e0')
        shadow.pack(fill=tk.X, pady=(0, 2))
        
        frame = self.create_rounded_frame(container)
        frame.pack(fill=tk.X, padx=1, pady=1)
        
        # Etiqueta con estilo moderno
        tk.Label(
            frame,
            text="Ingrese su expresión:",
            font=self.subtitle_font,
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            anchor='w'
        ).pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Frame del campo de entrada con bordes redondeados
        entry_container = self.create_rounded_frame(frame, highlightbackground='#cccccc', 
                                                  highlightthickness=1, highlightcolor='#cccccc')
        entry_container.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Scroll horizontal para el campo de entrada
        xscrollbar = tk.Scrollbar(entry_container, orient=tk.HORIZONTAL)
        xscrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.expression_entry = tk.Text(
            entry_container,
            height=3,
            font=self.entry_font,
            bg=self.colors['display'],
            fg=self.colors['text_dark'],
            wrap=tk.NONE,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            insertbackground=self.colors['text_dark'],
            xscrollcommand=xscrollbar.set
        )
        xscrollbar.config(command=self.expression_entry.xview)
        self.expression_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Botón de cálculo con estilo moderno
        btn_frame = self.create_rounded_frame(frame)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        RoundedButton(
            btn_frame,
            text="CALCULAR",
            radius=20,
            btnbackground=self.colors['equals'],
            btnforeground='white',
            width=120,
            height=40,
            clicked=self.calculate
        ).pack(side=tk.RIGHT)
        
    def create_results_area(self):
        """Área de resultados con diseño moderno"""
        container = self.create_rounded_frame(self.parent_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Sombra sutil
        shadow = tk.Frame(container, bg='#e0e0e0')
        shadow.pack(fill=tk.BOTH, expand=True, pady=(0, 2))
        
        frame = self.create_rounded_frame(container)
        frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Encabezado del área de resultados
        header_frame = self.create_rounded_frame(frame)
        header_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Título "Resultado:"
        tk.Label(
            header_frame,
            text="Resultado:",
            font=self.title_font,
            bg=self.colors['bg'],
            fg=self.colors['text_dark'],
            anchor='w'
        ).pack(side=tk.LEFT)
        
        # Botón guardar con estilo moderno
        RoundedButton(
            header_frame,
            text="💾 GUARDAR",
            radius=15,
            btnbackground=self.colors['operator'],
            btnforeground='white',
            width=100,
            height=30,
            clicked=self.save_current_calculation
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón copiar
        RoundedButton(
            header_frame,
            text="⎘ COPIAR",
            radius=15,
            btnbackground=self.colors['primary_light'],
            btnforeground='white',
            width=100,
            height=30,
            clicked=self.copy_result
        ).pack(side=tk.RIGHT)
        
        # Área del texto del resultado con bordes redondeados
        text_container = self.create_rounded_frame(frame, highlightbackground='#cccccc', 
                                                highlightthickness=1, highlightcolor='#cccccc')
        text_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar vertical
        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            text_container,
            font=self.result_font,
            bg=self.colors['display'],
            fg=self.colors['text_dark'],
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=15,
            pady=15,
            state=tk.DISABLED,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.result_text.yview)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
    def insert_symbol(self, symbol):
        """Inserta un símbolo en el campo de entrada"""
        try:
            # Insertar el símbolo en la posición actual del cursor
            cursor_pos = self.expression_entry.index(tk.INSERT)
            self.expression_entry.insert(cursor_pos, symbol)
            # Mantener el foco en el campo de entrada
            self.expression_entry.focus_set()
        except Exception as e:
            print(f"Error insertando símbolo '{symbol}': {e}")
    
    def set_expression(self, expression):
        """Coloca una expresión en el campo de entrada"""
        self.expression_entry.delete("1.0", tk.END)
        self.expression_entry.insert("1.0", expression)
        self.expression_entry.focus_set()

    def calculate(self):
        """Calcula la expresión ingresada usando la clase operations"""
        expression = self.expression_entry.get("1.0", tk.END).strip()
        if not expression:
            self.animate_error(self.expression_entry)
            return
            
        try:
            # Animación de carga
            self.animate_calculation()
            
            # Validar expresión usando operations
            if not self.operations.is_valid_expression(expression):
                self.display_error("Expresión matemática no válida")
                self.current_calculation = None
                return
            
            # Procesar la expresión usando operations
            result_data = self.operations.process_expression(expression)
            
            # Mostrar resultado con pasos detallados
            self.display_detailed_result(expression, result_data)
            
            # Determinar tipo de cálculo usando operations
            operation_info = self.operations.get_operation_info(expression)
            calc_type = self.determine_calculation_type_from_info(operation_info)
            
            # Agregar al historial
            self.app.history_controller.add_calculation(expression, result_data['result'], calc_type)
            
            # Guardar referencia para el botón "Guardar"
            self.current_calculation = {
                'expression': expression,
                'result': result_data['result'],
                'steps': result_data['steps'],
                'timestamp': datetime.datetime.now().isoformat(),
                'type': calc_type.value,
                'operation_type': operation_info['type']
            }
            
        except Exception as e:
            self.display_error(f"Error en el cálculo: {str(e)}")
            self.current_calculation = None
    
    def determine_calculation_type_from_info(self, operation_info):
     from models import TipoCalculo

     print(f"DEBUG: tipo detectado = {operation_info.get('type')}")

     type_mapping = {
         'basic_operations': TipoCalculo.BASICO,
         'fraction': TipoCalculo.BASICO,
         'symbolic': TipoCalculo.CIENTIFICO,
         'derivative': TipoCalculo.CIENTIFICO,
         'integral': TipoCalculo.CIENTIFICO,
         'equation': TipoCalculo.CIENTIFICO,
         'matrix': TipoCalculo.MATRIZ,
         'trigonometric': TipoCalculo.CIENTIFICO,
         'logarithmic': TipoCalculo.CIENTIFICO,
         'calculus': TipoCalculo.CIENTIFICO,
         'variable': TipoCalculo.CIENTIFICO
     }

     return type_mapping.get(operation_info.get('type', ''), TipoCalculo.BASICO)



    
    def save_current_calculation(self):
        """Guarda el cálculo actual usando el operations controller."""
        if not hasattr(self, 'current_calculation') or not self.current_calculation:
            self.show_notification("No hay cálculo para guardar")
            return
        
        try:
            # Construimos un título único usando datetime
            title = (
                f"Cálculo_{self.current_calculation.get('type')}_"
                f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # Llamada al controller
            operation_id = self.app.operations_controller.save_operation(
                title=title,
                expression=self.current_calculation['expression'],
                result=self.current_calculation['result'],
                # Asegúrate de que coincida con la clave que usas internamente:
                operation_type=self.current_calculation.get('type', 'expression')
            )
            
            if operation_id:
                self.show_notification("Cálculo guardado exitosamente")
                # Opcional: refrescar la vista de guardados si está visible
                if self.app.views.get('saved'):
                    self.app.views['saved'].show()
                # Limpiar la referencia
                self.current_calculation = None
            else:
                self.show_notification("Error al guardar el cálculo")
                
        except Exception as e:
            # Muestra el mensaje de error en la UI
            self.show_notification(f"Error: {str(e)}")

    def animate_calculation(self):
        """Animación durante el cálculo"""
        original_bg = self.expression_entry.cget('bg')
        self.expression_entry.config(bg='#f0f0f0')
        self.parent_frame.update()
        self.parent_frame.after(200, lambda: self.expression_entry.config(bg=original_bg))
        
    def animate_error(self, widget):
        """Animación de error (shake)"""
        x = widget.winfo_x()
        for i in range(0, 3):
            for dx in (5, -5, 5, -5):
                widget.place(x=x+dx)
                self.parent_frame.update()
                self.parent_frame.after(30)
        widget.place(x=x)
        
    def display_detailed_result(self, expression, result_data):
        """Muestra el resultado con pasos detallados de la clase operations"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Mostrar resultado principal
        output = f"✦ RESULTADO FINAL:\n{result_data['result']}\n\n"
        
        # Mostrar pasos detallados si están disponibles
        if 'steps' in result_data and result_data['steps']:
            output += "✦ PROCESO DE CÁLCULO:\n"
            output += "=" * 50 + "\n"
            for step in result_data['steps']:
                output += f"{step}\n"
        
        # Información adicional
        output += "\n" + "=" * 50 + "\n"
        output += f"✦ Información adicional:\n"
        output += f"   • Expresión original: {expression}\n"
        output += f"   • Tipo de operación: {result_data.get('type', 'unknown')}\n"
        output += f"   • Evaluado: {timestamp}\n"
        
        self.result_text.insert("1.0", output)
        self.result_text.config(state=tk.DISABLED)
        
        # Animación de éxito
        self.animate_success()
        
    def animate_success(self):
        """Animación de éxito al mostrar resultado"""
        original_bg = self.result_text.cget('bg')
        self.result_text.config(state=tk.NORMAL)
        self.result_text.tag_configure('highlight', background='#e8f5e9')
        self.result_text.tag_add('highlight', '1.0', 'end')
        self.parent_frame.update()
        
        def restore():
            self.result_text.tag_remove('highlight', '1.0', 'end')
            self.result_text.config(state=tk.DISABLED)
            
        self.parent_frame.after(500, restore)
        
    def display_error(self, message):
        """Muestra un mensaje de error con formato"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        
        self.result_text.tag_configure('error', foreground='#c62828')
        self.result_text.insert("1.0", "✖ Error:\n", 'error')
        self.result_text.insert(tk.END, message)
        
        self.result_text.config(state=tk.DISABLED)
        
    def copy_result(self):
        """Copia el resultado al portapapeles"""
        result = self.result_text.get("1.0", tk.END).strip()
        if result:
            self.parent_frame.clipboard_clear()
            self.parent_frame.clipboard_append(result)
            
            # Mostrar notificación flotante
            self.show_notification("Resultado copiado al portapapeles")
            
    def show_notification(self, message):
        """Muestra una notificación flotante"""
        notification = tk.Toplevel(self.parent_frame)
        notification.wm_overrideredirect(True)
        notification.wm_geometry("+%d+%d" % (
            self.parent_frame.winfo_rootx() + self.parent_frame.winfo_width() - 200,
            self.parent_frame.winfo_rooty() + 50
        ))
        
        label = tk.Label(
            notification,
            text=message,
            font=('Helvetica', 10),
            bg='#333333',
            fg='white',
            padx=15,
            pady=8
        )
        label.pack()
        
        # Animación de desvanecimiento
        notification.attributes('-alpha', 0)
        for i in range(0, 101, 10):
            notification.attributes('-alpha', i/100)
            notification.update()
            notification.after(20)
            
        notification.after(2000, lambda: notification.destroy())