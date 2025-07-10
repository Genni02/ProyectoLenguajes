import math
import re
import sympy as sp
from sympy import symbols, Eq, solve, Matrix, diff, integrate, Rational, simplify, expand, factor
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from fractions import Fraction

class operations:
    def __init__(self):
        """Inicializa la clase de operaciones matemáticas"""
        self.allowed_functions = {
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sqrt': math.sqrt, 'log': math.log10, 'ln': math.log,
            'log10': math.log10, 'log2': math.log2, 'exp': math.exp,
            'abs': abs, 'pow': pow, 'pi': math.pi, 'e': math.e,
            'ceil': math.ceil, 'floor': math.floor, 'round': round,
            'factorial': math.factorial, 'degrees': math.degrees, 'radians': math.radians
        }
        
        # Símbolos comunes para álgebra simbólica
        self.x, self.y, self.z = sp.symbols('x y z')
        self.t = sp.symbols('t')

        # Diccionario de plantillas/símbolos especiales
        self.symbol_templates = {
            "x²": "x^2",
            "x^□": "x^a",      # 'a' como placeholder
            "log_□": "log_a(x)", # logaritmo base a de x
            "√□": "sqrt(x)",
            "√[□]{□}": "root(a, x)", # raíz a-ésima de x
            "x°": "x^o",       # 'o' como placeholder para grados
            "□": "a",          # placeholder genérico
        }
    
    def _preprocess_templates(self, expression):
        """
        Reemplaza los símbolos y plantillas especiales por su equivalente matemático.
        """
        # Primero, reemplazar todos los símbolos definidos en self.symbol_templates
        for symbol, replacement in self.symbol_templates.items():
            expression = expression.replace(symbol, replacement)

        # Reemplazar cuadros vacíos (□, ◻, etc.) por 'a' (o el placeholder que prefieras)
        expression = expression.replace("□", "a")
        expression = expression.replace("◻", "a")

        # Reemplazar plantillas específicas con paréntesis vacíos por variables
        # Ejemplo: x^() -> x^a, log_() -> log_a(x), sqrt() -> sqrt(x), root(,) -> root(a, x)
        import re
        expression = re.sub(r'x\^\(\)', 'x^a', expression)
        expression = re.sub(r'log_\(\)', 'log_a(x)', expression)
        expression = re.sub(r'sqrt\(\)', 'sqrt(x)', expression)
        expression = re.sub(r'root\((,)?\)', 'root(a, x)', expression)
        expression = re.sub(r'root\(([^,]+),([^)]+)\)', r'root(\1, \2)', expression)

        # Reemplazar potencias ^ por **
        import re
        # Solo reemplaza ^ cuando está entre símbolos válidos para evitar errores
        expression = re.sub(r'(\w)\^(\w|\()', r'\1**\2', expression)

        return expression
    
    def process_expression(self, expression):
        """Procesa y evalúa una expresión matemática con pasos específicos según el tipo"""
        if not expression or not expression.strip():
            raise ValueError("Expresión vacía")
        
        # Símbolos y plantillas 
        expression = self._preprocess_templates(expression.strip())
        
        # Detectar tipo de operación y procesar con pasos específicos
        if self._is_equation(expression):
            return self.solve_equation(expression)
        elif self._is_matrix_operation(expression):
            return self.process_matrix(expression)
        elif self._is_derivative(expression):
            return self.calculate_derivative(expression)
        elif self._is_integral(expression):
            return self.calculate_integral(expression)
        elif self._is_fraction(expression):
            return self.process_fraction(expression)
        elif self._contains_variables(expression):
            return self.process_symbolic(expression)
        else:
            # Operaciones básicas (suma, resta, multiplicación, división)
            return self._process_basic_operations(expression)
    
    def _is_equation(self, expression):
        """Verifica si es una ecuación (contiene =)"""
        return '=' in expression and expression.count('=') == 1
    
    def _is_matrix_operation(self, expression):
        """Verifica si es una operación con matrices"""
        return '[' in expression and ']' in expression
    
    def _is_derivative(self, expression):
        """Verifica si es una derivada"""
        return any(keyword in expression.lower() for keyword in ['d/dx', 'derivative', 'diff'])
    
    def _is_integral(self, expression):
        """Verifica si es una integral"""
        return any(keyword in expression.lower() for keyword in ['integral', 'integrate', '∫'])
    
    def _is_fraction(self, expression):
        """Verifica si es una fracción para procesar exactamente"""
        return '/' in expression and not any(func in expression for func in ['sin', 'cos', 'log', 'sqrt'])
    
    def _contains_variables(self, expression):
        """Verifica si contiene variables (x, y, z, t)"""
        return any(var in expression for var in ['x', 'y', 'z', 't']) and '=' not in expression
    
    def _handle_implicit_multiplication(self, expression):
        """Maneja la multiplicación implícita en expresiones"""
        patterns = [
            (r'(\d)([a-zA-Z])', r'\1*\2'),
            (r'(\d)\(', r'\1*('),
            (r'([a-zA-Z])\(', r'\1*('),
            (r'\)([a-zA-Z])', r')*\1'),
            (r'\)(\d)', r')*\1'),
            (r'\)\(', r')*('),
        ]
        
        for pattern, replacement in patterns:
            expression = re.sub(pattern, replacement, expression)
        
        return expression
    
    # ==================== OPERACIONES BÁSICAS ====================
    def _process_basic_operations(self, expression):
        """Procesa operaciones básicas: suma, resta, multiplicación, división"""
        try:
            steps = []
            steps.append("🔢 OPERACIONES BÁSICAS")
            steps.append("=" * 40)
            steps.append(f"🎯 Expresión a calcular: {expression}")
            
            # Limpiar expresión
            cleaned_expression = self._clean_expression(expression)
            if cleaned_expression != expression:
                steps.append(f"🔧 Expresión limpia: {cleaned_expression}")
            
            # Validar
            if not self._validate_expression(cleaned_expression):
                return {
                    'result': "❌ Expresión no válida",
                    'steps': steps + ["❌ La expresión contiene caracteres no permitidos"],
                    'type': 'error'
                }
            
            # Detectar tipo de operación básica
            operation_type = self._detect_basic_operation_type(cleaned_expression)
            steps.append(f"📝 Tipo de operación: {operation_type}")
            
            # Explicar orden de operaciones
            steps.append("📚 ORDEN DE OPERACIONES (PEMDAS/BODMAS):")
            steps.append("   1️⃣ Paréntesis y corchetes")
            steps.append("   2️⃣ Exponentes y raíces")
            steps.append("   3️⃣ Multiplicación y División (de izquierda a derecha)")
            steps.append("   4️⃣ Suma y Resta (de izquierda a derecha)")
            
            # Mostrar pasos específicos según la operación
            calculation_steps = self._explain_basic_calculation_steps(cleaned_expression)
            steps.extend(calculation_steps)
            
            # Evaluar
            result = self._safe_eval(self._replace_functions_and_constants(cleaned_expression))
            steps.append(f"✅ RESULTADO FINAL: {result}")
            
            return {
                'result': f"🔢 Resultado: {result}",
                'steps': steps,
                'type': 'basic_operations'
            }
            
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': steps + [f"❌ Error: {str(e)}"],
                'type': 'error'
            }
    
    def _detect_basic_operation_type(self, expression):
        """Detecta el tipo específico de operación básica"""
        if '+' in expression and '-' not in expression and '*' not in expression and '/' not in expression:
            return "SUMA"
        elif '-' in expression and '+' not in expression and '*' not in expression and '/' not in expression:
            return "RESTA"
        elif '*' in expression and '+' not in expression and '-' not in expression and '/' not in expression:
            return "MULTIPLICACIÓN"
        elif '/' in expression and '+' not in expression and '-' not in expression and '*' not in expression:
            return "DIVISIÓN"
        elif '**' in expression or '^' in expression:
            return "POTENCIACIÓN"
        else:
            return "OPERACIÓN MIXTA"
    
    def _explain_basic_calculation_steps(self, expression):
        """Explica los pasos de cálculo para operaciones básicas"""
        steps = []
        steps.append("🔍 PROCESO DE CÁLCULO:")
        
        # Detectar si hay paréntesis
        if '(' in expression:
            steps.append("1️⃣ Resolvemos primero lo que está entre paréntesis")
            # Aquí podrías agregar lógica más específica para mostrar el contenido de paréntesis
        
        # Detectar operaciones específicas
        if '+' in expression:
            parts = expression.split('+')
            if len(parts) == 2:
                steps.append(f"2️⃣ Sumamos: {parts[0].strip()} + {parts[1].strip()}")
                steps.append(f"   💡 Recordamos: suma significa agregar cantidades")
        
        if '-' in expression and not expression.startswith('-'):
            parts = expression.split('-')
            if len(parts) == 2:
                steps.append(f"2️⃣ Restamos: {parts[0].strip()} - {parts[1].strip()}")
                steps.append(f"   💡 Recordamos: resta significa quitar una cantidad de otra")
        
        if '*' in expression:
            parts = expression.split('*')
            if len(parts) == 2:
                steps.append(f"2️⃣ Multiplicamos: {parts[0].strip()} × {parts[1].strip()}")
                steps.append(f"   💡 Recordamos: multiplicar es sumar repetidas veces")
        
        if '/' in expression:
            parts = expression.split('/')
            if len(parts) == 2:
                steps.append(f"2️⃣ Dividimos: {parts[0].strip()} ÷ {parts[1].strip()}")
                steps.append(f"   💡 Recordamos: dividir es repartir en partes iguales")
                # Verificar división por cero
                try:
                    denominator = float(parts[1].strip())
                    if denominator == 0:
                        steps.append("   ⚠️ ATENCIÓN: División por cero no está definida")
                except:
                    pass
        
        if '**' in expression:
            parts = expression.split('**')
            if len(parts) == 2:
                steps.append(f"2️⃣ Calculamos potencia: {parts[0].strip()}^{parts[1].strip()}")
                steps.append(f"   💡 Recordamos: potencia es multiplicar la base por sí misma")
        
        return steps
    
    # ==================== ÁLGEBRA SIMBÓLICA ====================
    def process_symbolic(self, expression):
        """Procesa expresiones de álgebra simbólica"""
        try:
            steps = []
            steps.append("🎭 ÁLGEBRA SIMBÓLICA")
            steps.append("=" * 40)
            steps.append(f"🎯 Expresión simbólica: {expression}")
            
            # Manejar multiplicación implícita
            processed_expr = self._handle_implicit_multiplication(expression)
            if processed_expr != expression:
                steps.append(f"📝 Multiplicación explícita: {processed_expr}")
            
            transformations = standard_transformations + (implicit_multiplication_application,)
            expr = parse_expr(processed_expr, transformations=transformations)
            steps.append(f"✅ Expresión procesada: {expr}")
            
            result_text = f"📝 Expresión original: {expr}\n"
            
            # Análisis paso a paso
            steps.append("📚 ANÁLISIS ALGEBRAICO:")
            
            # 1. Simplificar
            steps.append("1️⃣ SIMPLIFICACIÓN:")
            simplified = simplify(expr)
            if simplified != expr:
                steps.append(f"   ✨ Aplicamos reglas algebraicas: {expr} → {simplified}")
                steps.append(f"   💡 Combinamos términos semejantes y reducimos fracciones")
                result_text += f"✨ Simplificada: {simplified}\n"
            else:
                steps.append("   ℹ️ La expresión ya está en su forma más simple")
            
            # 2. Expandir
            steps.append("2️⃣ EXPANSIÓN:")
            expanded = expand(expr)
            if expanded != expr:
                steps.append(f"   📈 Desarrollamos productos: {expr} → {expanded}")
                steps.append(f"   💡 Aplicamos propiedad distributiva: a(b+c) = ab + ac")
                result_text += f"📈 Expandida: {expanded}\n"
            else:
                steps.append("   ℹ️ No hay productos que expandir")
            
            # 3. Factorizar
            steps.append("3️⃣ FACTORIZACIÓN:")
            try:
                factored = factor(expr)
                if factored != expr:
                    steps.append(f"   🔧 Factorizamos: {expr} → {factored}")
                    steps.append(f"   💡 Encontramos factores comunes o aplicamos fórmulas")
                    result_text += f"🔧 Factorizada: {factored}\n"
                else:
                    steps.append("   ℹ️ No se puede factorizar más")
            except:
                steps.append("   ⚠️ No se pudo factorizar esta expresión")
            
            # 4. Evaluación numérica
            steps.append("4️⃣ EVALUACIÓN NUMÉRICA:")
            try:
                if not expr.has(sp.Symbol):
                    numeric_value = expr.evalf()
                    steps.append(f"   🔢 Valor numérico: {numeric_value}")
                    result_text += f"🔢 Valor numérico: {numeric_value}"
                else:
                    steps.append("   ℹ️ Contiene variables, necesita valores específicos para evaluar")
            except:
                steps.append("   ⚠️ No se pudo evaluar numéricamente")
            
            return {
                'result': result_text.strip(),
                'steps': steps,
                'type': 'symbolic'
            }
            
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': [f"❌ Error en álgebra simbólica: {str(e)}"],
                'type': 'error'
            }
    
    # ==================== DERIVADAS E INTEGRALES ====================
    def calculate_derivative(self, expression):
        """Calcula derivadas con pasos detallados de cálculo"""
        try:
            steps = []
            steps.append("📐 CÁLCULO DE DERIVADAS")
            steps.append("=" * 40)
            steps.append(f"🎯 Expresión a derivar: {expression}")
            
            # Procesar formato
            func, var = self._parse_derivative_expression(expression)
            steps.append(f"📝 Función: f({var}) = {func}")
            steps.append(f"🔍 Variable de derivación: {var}")
            
            # Explicar concepto
            steps.append("📚 CONCEPTO DE DERIVADA:")
            steps.append("   💡 La derivada mide la razón de cambio instantánea")
            steps.append("   📊 Geométricamente: pendiente de la recta tangente")
            steps.append("   🔬 Físicamente: velocidad si f(x) es posición")
            
            # Aplicar reglas paso a paso
            steps.append("📐 REGLAS DE DERIVACIÓN:")
            derivative_steps = self._explain_derivative_rules_detailed(func)
            steps.extend(derivative_steps)
            
            # Calcular resultado
            derivative = diff(func, var)
            steps.append(f"✅ RESULTADO: f'({var}) = {derivative}")
            
            # Verificar reglas aplicadas
            steps.append("🔍 VERIFICACIÓN:")
            verification_steps = self._verify_derivative_rules(func, derivative)
            steps.extend(verification_steps)
            
            return {
                'result': f"📐 Derivada: {derivative}",
                'steps': steps,
                'type': 'derivative'
            }
            
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': [f"❌ Error al calcular derivada: {str(e)}"],
                'type': 'error'
            }
    
    def calculate_integral(self, expression):
        """Calcula integrales con pasos detallados"""
        try:
            steps = []
            steps.append("∫ CÁLCULO DE INTEGRALES")
            steps.append("=" * 40)
            steps.append(f"🎯 Expresión a integrar: {expression}")
            
            # Procesar formato
            func, var = self._parse_integral_expression(expression)
            steps.append(f"📝 Función: f({var}) = {func}")
            steps.append(f"🔍 Variable de integración: {var}")
            
            # Explicar concepto
            steps.append("📚 CONCEPTO DE INTEGRAL:")
            steps.append("   💡 La integral calcula el área bajo la curva")
            steps.append("   📊 Geométricamente: suma de infinitos rectángulos")
            steps.append("   🔬 Físicamente: si f(x) es velocidad, integral es distancia")
            
            # Aplicar reglas paso a paso
            steps.append("∫ REGLAS DE INTEGRACIÓN:")
            integral_steps = self._explain_integration_rules_detailed(func)
            steps.extend(integral_steps)
            
            # Calcular resultado
            integral_result = integrate(func, var)
            steps.append(f"✅ RESULTADO: ∫f({var})d{var} = {integral_result} + C")
            steps.append("📝 NOTA: Siempre agregamos la constante C en integrales indefinidas")
            
            # Verificar por derivación
            steps.append("🔍 VERIFICACIÓN (derivando el resultado):")
            verification = diff(integral_result, var)
            steps.append(f"   d/d{var}[{integral_result}] = {verification}")
            if simplify(verification - func) == 0:
                steps.append("   ✅ Verificación exitosa: la derivada coincide con la función original")
            
            return {
                'result': f"∫ Integral: {integral_result} + C",
                'steps': steps,
                'type': 'integral'
            }
            
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': [f"❌ Error al calcular integral: {str(e)}"],
                'type': 'error'
            }
    
    def _explain_derivative_rules_detailed(self, func):
        """Explica las reglas de derivación con detalle paso a paso"""
        steps = []
        
        # Analizar la función y explicar reglas específicas
        func_str = str(func)
        
        if func.is_polynomial():
            steps.append("📐 REGLA DE LA POTENCIA:")
            steps.append("   📖 d/dx(xⁿ) = n·xⁿ⁻¹")
            steps.append("   📖 d/dx(c) = 0 (derivada de constante)")
            steps.append("   📖 d/dx(cf(x)) = c·f'(x) (factor constante)")
            
            # Mostrar aplicación específica
            terms = sp.Add.make_args(func)
            for term in terms:
                if term.is_number:
                    steps.append(f"   🔍 Término constante {term}: derivada = 0")
                elif term.has(sp.Symbol):
                    steps.append(f"   🔍 Término {term}: aplicamos regla de potencia")
        
        if 'sin' in func_str:
            steps.append("📐 REGLA TRIGONOMÉTRICA:")
            steps.append("   📖 d/dx(sin(x)) = cos(x)")
            steps.append("   💡 La derivada del seno es el coseno")
        
        if 'cos' in func_str:
            steps.append("📐 REGLA TRIGONOMÉTRICA:")
            steps.append("   📖 d/dx(cos(x)) = -sin(x)")
            steps.append("   💡 La derivada del coseno es menos seno")
        
        if 'exp' in func_str or 'e**' in func_str:
            steps.append("📐 REGLA EXPONENCIAL:")
            steps.append("   📖 d/dx(eˣ) = eˣ")
            steps.append("   💡 La función exponencial es su propia derivada")
        
        if 'log' in func_str:
            steps.append("📐 REGLA LOGARÍTMICA:")
            steps.append("   📖 d/dx(ln(x)) = 1/x")
            steps.append("   💡 La derivada del logaritmo natural")
        
        # Regla de la cadena si es necesario
        if func.has(sp.Function) or any(f in func_str for f in ['sin(', 'cos(', 'exp(', 'log(']):
            steps.append("🔗 REGLA DE LA CADENA:")
            steps.append("   📖 d/dx(f(g(x))) = f'(g(x))·g'(x)")
            steps.append("   💡 Para funciones compuestas")
        
        return steps
    
    def _explain_integration_rules_detailed(self, func):
        """Explica las reglas de integración con detalle"""
        steps = []
        func_str = str(func)
        
        if func.is_polynomial():
            steps.append("∫ REGLA DE LA POTENCIA:")
            steps.append("   📖 ∫xⁿ dx = xⁿ⁺¹/(n+1) + C")
            steps.append("   📖 ∫c dx = cx + C (integral de constante)")
            steps.append("   📖 ∫cf(x) dx = c∫f(x) dx (factor constante sale)")
            
            # Mostrar aplicación específica
            terms = sp.Add.make_args(func)
            for term in terms:
                if term.is_number:
                    steps.append(f"   🔍 Término constante {term}: integral = {term}x")
                elif term.has(sp.Symbol):
                    steps.append(f"   🔍 Término {term}: aplicamos regla de potencia")
        
        if 'sin' in func_str:
            steps.append("∫ REGLA TRIGONOMÉTRICA:")
            steps.append("   📖 ∫sin(x) dx = -cos(x) + C")
            steps.append("   💡 La integral del seno es menos coseno")
        
        if 'cos' in func_str:
            steps.append("∫ REGLA TRIGONOMÉTRICA:")
            steps.append("   📖 ∫cos(x) dx = sin(x) + C")
            steps.append("   💡 La integral del coseno es el seno")
        
        if 'exp' in func_str or 'e**' in func_str:
            steps.append("∫ REGLA EXPONENCIAL:")
            steps.append("   📖 ∫eˣ dx = eˣ + C")
            steps.append("   💡 La integral de la exponencial es ella misma")
        
        if func_str == '1/x':
            steps.append("∫ REGLA LOGARÍTMICA:")
            steps.append("   📖 ∫(1/x) dx = ln|x| + C")
            steps.append("   💡 La integral de 1/x es logaritmo natural")
        
        return steps
    
    def _verify_derivative_rules(self, original_func, derivative):
        """Verifica las reglas de derivación aplicadas"""
        steps = []
        
        # Verificar término por término si es suma
        if original_func.is_Add:
            steps.append("   📊 Verificamos término por término:")
            terms = sp.Add.make_args(original_func)
            der_terms = sp.Add.make_args(derivative)
            for i, term in enumerate(terms):
                if i < len(der_terms):
                    steps.append(f"   ✓ d/dx({term}) = {der_terms[i]}")
        
        return steps
    
    def _parse_derivative_expression(self, expression):
        """Parsea expresiones de derivada para extraer función y variable"""
        if 'd/dx(' in expression:
            start = expression.find('d/dx(') + 5
            end = expression.rfind(')')
            func_str = expression[start:end]
            return parse_expr(func_str), self.x
        elif 'derivative(' in expression:
            start = expression.find('derivative(') + 11
            end = expression.rfind(')')
            args = expression[start:end].split(',')
            if len(args) >= 2:
                return parse_expr(args[0].strip()), symbols(args[1].strip())
            else:
                return parse_expr(args[0].strip()), self.x
        else:
            return parse_expr(expression), self.x
    
    def _parse_integral_expression(self, expression):
        """Parsea expresiones de integral para extraer función y variable"""
        if 'integral(' in expression:
            start = expression.find('integral(') + 9
            end = expression.rfind(')')
            args = expression[start:end].split(',')
            if len(args) >= 2:
                return parse_expr(args[0].strip()), symbols(args[1].strip())
            else:
                return parse_expr(args[0].strip()), self.x
        elif 'integrate(' in expression:
            start = expression.find('integrate(') + 10
            end = expression.rfind(')')
            func_str = expression[start:end]
            return parse_expr(func_str), self.x
        else:
            return parse_expr(expression), self.x
    
    # ==================== ECUACIONES ====================
    def solve_equation(self, equation):
        """Resuelve ecuaciones con pasos matemáticos detallados"""
        try:
            steps = []
            steps.append("⚖️ RESOLUCIÓN DE ECUACIONES")
            steps.append("=" * 40)
            steps.append(f"🎯 Ecuación a resolver: {equation}")
            
            # Procesar multiplicación implícita
            processed_eq = self._handle_implicit_multiplication(equation)
            if processed_eq != equation:
                steps.append(f"📝 Multiplicación explícita: {processed_eq}")
            
            # Separar lados
            left_side, right_side = processed_eq.split('=')
            steps.append(f"🔍 Lado izquierdo: {left_side}")
            steps.append(f"🔍 Lado derecho: {right_side}")
            
            # Convertir a expresiones simbólicas
            transformations = standard_transformations + (implicit_multiplication_application,)
            left_expr = parse_expr(left_side, transformations=transformations)
            right_expr = parse_expr(right_side, transformations=transformations)
            
            eq = Eq(left_expr, right_expr)
            variables = list(eq.free_symbols)
            
            if not variables:
                # Verificación de igualdad numérica
                left_val = left_expr.evalf()
                right_val = right_expr.evalf()
                steps.append(f"🔢 Evaluación: {left_val} = {right_val}")
                
                result = "✅ La igualdad es verdadera" if left_val == right_val else "❌ La igualdad es falsa"
                return {'result': result, 'steps': steps, 'type': 'verification'}
            
            steps.append(f"🎯 Variable a encontrar: {variables[0]}")
            
            # Clasificar y resolver según el tipo
            var = variables[0]
            equation_type = self._classify_equation_type(left_expr, var)
            steps.append(f"📚 Tipo de ecuación: {equation_type}")
            
            # Resolver paso a paso según el tipo
            if equation_type == "LINEAL":
                solution_steps = self._solve_linear_detailed(left_expr, right_expr, var)
            elif equation_type == "CUADRÁTICA":
                solution_steps = self._solve_quadratic_detailed(left_expr, right_expr, var)
            else:
                solution_steps = self._solve_general_detailed(left_expr, right_expr, var)
            
            steps.extend(solution_steps)
            
            # Obtener solución
            sols = solve(eq, var)
            if sols:
                sol_value = sols[0]
                result_text = f"🎉 SOLUCIÓN: {var} = {sol_value}"
                if sol_value.is_rational and sol_value.q != 1:
                    result_text += f" = {float(sol_value)}"
                
                # Verificación
                steps.append("🔍 VERIFICACIÓN DE LA SOLUCIÓN:")
                verification = left_expr.subs(var, sol_value)
                steps.append(f"   Sustituyendo {var} = {sol_value} en el lado izquierdo:")
                steps.append(f"   {left_expr.subs(var, sol_value)} = {verification.evalf()}")
                steps.append(f"   Lado derecho: {right_expr.evalf()}")
                steps.append("   ✅ La solución es correcta" if verification.evalf() == right_expr.evalf() else "   ❌ Error en la solución")
                
                return {'result': result_text, 'steps': steps, 'type': 'equation'}
            else:
                return {'result': "❌ No hay soluciones", 'steps': steps, 'type': 'equation'}
                
        except Exception as e:
            return {'result': f"❌ Error: {str(e)}", 'steps': [f"❌ Error: {str(e)}"], 'type': 'error'}
    
    def _classify_equation_type(self, expr, var):
        """Clasifica el tipo de ecuación"""
        if expr.is_polynomial(var):
            degree = expr.as_poly(var).degree()
            if degree == 1:
                return "LINEAL"
            elif degree == 2:
                return "CUADRÁTICA"
            else:
                return f"POLINÓMICA GRADO {degree}"
        else:
            return "TRASCENDENTE"
    
    def _solve_linear_detailed(self, left_expr, right_expr, var):
        """Resuelve ecuaciones lineales con pasos matemáticos detallados"""
        steps = []
        steps.append("📐 MÉTODO DE RESOLUCIÓN LINEAL:")
        steps.append("   💡 Una ecuación lineal tiene la forma ax + b = c")
        
        # Obtener coeficientes
        poly = left_expr.as_poly(var)
        a = poly.nth(1) if poly.degree() >= 1 else 0
        b = poly.nth(0)
        c = right_expr
        
        steps.append(f"📊 Identificamos coeficientes: a = {a}, b = {b}, c = {c}")
        steps.append(f"📝 Forma estándar: {a}·{var} + ({b}) = {c}")
        
        steps.append("🔧 PASOS DE RESOLUCIÓN:")
        
        # Paso 1: Aislar término con variable
        if b != 0:
            new_right = c - b
            if b > 0:
                steps.append(f"1️⃣ Restamos {b} de ambos lados:")
            else:
                steps.append(f"1️⃣ Sumamos {abs(b)} a ambos lados:")
            steps.append(f"   {a}·{var} + ({b}) - ({b}) = {c} - ({b})")
            steps.append(f"   {a}·{var} = {new_right}")
        else:
            new_right = c
            steps.append(f"1️⃣ No hay término independiente que mover")
            steps.append(f"   {a}·{var} = {new_right}")
        
        # Paso 2: Despejar variable
        if a != 1:
            final_result = new_right / a
            steps.append(f"2️⃣ Dividimos ambos lados entre {a}:")
            steps.append(f"   {var} = {new_right} ÷ {a}")
            steps.append(f"   {var} = {final_result}")
        else:
            steps.append(f"2️⃣ El coeficiente es 1, por lo tanto:")
            steps.append(f"   {var} = {new_right}")
        
        return steps
    
    def _solve_quadratic_detailed(self, left_expr, right_expr, var):
        """Resuelve ecuaciones cuadráticas con pasos detallados"""
        steps = []
        steps.append("📐 MÉTODO DE RESOLUCIÓN CUADRÁTICA:")
        steps.append("   💡 Una ecuación cuadrática tiene la forma ax² + bx + c = 0")
        
        # Llevar a forma estándar
        full_expr = left_expr - right_expr
        poly = full_expr.as_poly(var)
        
        a = poly.nth(2) if poly.degree() >= 2 else 0
        b = poly.nth(1) if poly.degree() >= 1 else 0
        c = poly.nth(0)
        
        steps.append(f"📊 Forma estándar: {a}·{var}² + {b}·{var} + {c} = 0")
        steps.append(f"📝 Coeficientes: a = {a}, b = {b}, c = {c}")
        
        steps.append("🧮 FÓRMULA CUADRÁTICA:")
        steps.append("   📖 x = (-b ± √(b² - 4ac)) / (2a)")
        
        # Calcular discriminante
        discriminant = b**2 - 4*a*c
        steps.append(f"🔍 Calculamos discriminante (Δ):")
        steps.append(f"   Δ = b² - 4ac = ({b})² - 4({a})({c})")
        steps.append(f"   Δ = {b**2} - {4*a*c} = {discriminant}")
        
        # Analizar discriminante
        if discriminant > 0:
            steps.append("✅ Δ > 0: Dos soluciones reales distintas")
            sqrt_disc = sp.sqrt(discriminant)
            steps.append(f"🔢 √Δ = √{discriminant} = {sqrt_disc}")
            
            x1 = (-b + sqrt_disc) / (2*a)
            x2 = (-b - sqrt_disc) / (2*a)
            
            steps.append("📊 Aplicamos la fórmula:")
            steps.append(f"   x₁ = (-{b} + {sqrt_disc}) / (2·{a}) = {x1}")
            steps.append(f"   x₂ = (-{b} - {sqrt_disc}) / (2·{a}) = {x2}")
            
        elif discriminant == 0:
            steps.append("⚖️ Δ = 0: Una solución real doble")
            x = -b / (2*a)
            steps.append(f"📊 x = -b / (2a) = -({b}) / (2·{a}) = {x}")
            
        else:
            steps.append("❌ Δ < 0: No hay soluciones reales (soluciones complejas)")
        
        return steps
    
    def _solve_general_detailed(self, left_expr, right_expr, var):
        """Maneja ecuaciones generales"""
        steps = []
        steps.append("📐 ECUACIÓN GENERAL:")
        steps.append(f"   🎯 Despejamos {var} usando métodos algebraicos")
        steps.append(f"   📝 Ecuación: {left_expr} = {right_expr}")
        return steps
    
    # ==================== MATRICES Y ÁLGEBRA LINEAL ====================
    def process_matrix(self, matrix_str):
        """Procesa matrices con álgebra lineal detallada"""
        try:
            steps = []
            steps.append("🔢 MATRICES Y ÁLGEBRA LINEAL")
            steps.append("=" * 40)
            steps.append(f"🎯 Matriz a procesar: {matrix_str}")
            
            # Convertir a formato Matrix
            if 'Matrix(' not in matrix_str:
                matrix_str = f"Matrix({matrix_str})"
                steps.append(f"📝 Formato SymPy: {matrix_str}")
            
            matrix = eval(matrix_str, {"Matrix": Matrix, "sp": sp, "sqrt": sp.sqrt})
            steps.append(f"✅ Matriz creada: {matrix.rows}×{matrix.cols}")
            steps.append(f"📊 Elementos de la matriz:\n{matrix}")
            
            result_text = f"🔢 Matriz:\n{matrix}\n"
            
            # Propiedades básicas
            steps.append("📐 PROPIEDADES DE LA MATRIZ:")
            steps.append(f"   📏 Dimensiones: {matrix.rows} filas × {matrix.cols} columnas")
            steps.append(f"   🔍 Tipo: {'Cuadrada' if matrix.rows == matrix.cols else 'Rectangular'}")
            
            if matrix.rows == matrix.cols:
                steps.append("🧮 CÁLCULOS PARA MATRIZ CUADRADA:")
                
                # Determinante
                steps.append("1️⃣ DETERMINANTE:")
                if matrix.rows == 2:
                    steps.append("   📐 Para matriz 2×2: det(A) = ad - bc")
                    a, b = matrix[0, 0], matrix[0, 1]
                    c, d = matrix[1, 0], matrix[1, 1]
                    det = a*d - b*c
                    steps.append(f"   🔢 det = ({a})({d}) - ({b})({c}) = {a*d} - {b*c} = {det}")
                elif matrix.rows == 3:
                    steps.append("   📐 Para matriz 3×3: expansión por cofactores")
                    det = matrix.det()
                    steps.append(f"   🔢 det = {det}")
                else:
                    det = matrix.det()
                    steps.append(f"   🔢 det = {det} (calculado por expansión)")
                
                result_text += f"\n📊 Determinante: {det}"
                
                # Análisis del determinante
                steps.append("📊 ANÁLISIS DEL DETERMINANTE:")
                if det == 0:
                    steps.append("   ❌ det = 0: Matriz singular (no invertible)")
                    steps.append("   💡 Las filas/columnas son linealmente dependientes")
                else:
                    steps.append("   ✅ det ≠ 0: Matriz no singular (invertible)")
                    steps.append("   💡 Las filas/columnas son linealmente independientes")
                
                # Matriz inversa
                if det != 0:
                    steps.append("2️⃣ MATRIZ INVERSA:")
                    steps.append("   📐 A⁻¹ = (1/det(A)) × adj(A)")
                    steps.append("   💡 adj(A) es la matriz adjunta (transpuesta de cofactores)")
                    
                    inv = matrix.inv()
                    steps.append("   ✅ Matriz inversa calculada")
                    result_text += f"\n🔄 Matriz inversa:\n{inv}"
                    
                    # Verificación
                    steps.append("🔍 VERIFICACIÓN: A × A⁻¹ = I")
                    identity_check = matrix * inv
                    steps.append(f"   A × A⁻¹ = {identity_check}")
                else:
                    steps.append("2️⃣ MATRIZ INVERSA:")
                    steps.append("   ❌ No existe matriz inversa (det = 0)")
            
            # Rango
            steps.append("3️⃣ RANGO DE LA MATRIZ:")
            steps.append("   📐 El rango es el número máximo de filas/columnas linealmente independientes")
            rank = matrix.rank()
            steps.append(f"   🔢 rango(A) = {rank}")
            result_text += f"\n📏 Rango: {rank}"
            
            # Interpretación del rango
            steps.append("📊 INTERPRETACIÓN DEL RANGO:")
            if matrix.rows == matrix.cols:
                if rank == matrix.rows:
                    steps.append("   ✅ Rango completo: todas las filas/columnas son independientes")
                else:
                    steps.append(f"   ⚠️ Rango deficiente: solo {rank} de {matrix.rows} filas son independientes")
            
            return {
                'result': result_text,
                'steps': steps,
                'type': 'matrix'
            }
            
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': [f"❌ Error en matriz: {str(e)}"],
                'type': 'error'
            }
    
    # ==================== FRACCIONES EXACTAS ====================
    def process_fraction(self, expression):
        """Procesa fracciones con aritmética exacta"""
        try:
            steps = []
            steps.append("🔢 CÁLCULO CON FRACCIONES EXACTAS")
            steps.append("=" * 40)
            steps.append(f"🎯 Expresión con fracciones: {expression}")
            
            expr = parse_expr(expression)
            steps.append(f"📝 Expresión simbólica: {expr}")
            
            # Detectar operación con fracciones
            operation_type = self._detect_fraction_operation_type(expression)
            steps.append(f"📊 Tipo de operación: {operation_type}")
            
            # Explicar conceptos
            steps.append("📚 CONCEPTOS DE FRACCIONES:")
            steps.append("   💡 Una fracción representa una división a/b")
            steps.append("   📊 Numerador: parte que se toma")
            steps.append("   📊 Denominador: partes en que se divide el total")
            
            # Pasos específicos según operación
            if '+' in expression or '-' in expression:
                fraction_steps = self._explain_fraction_addition_subtraction(expression)
                steps.extend(fraction_steps)
            elif '*' in expression:
                fraction_steps = self._explain_fraction_multiplication(expression)
                steps.extend(fraction_steps)
            elif '/' in expression and expression.count('/') > 1:
                fraction_steps = self._explain_fraction_division(expression)
                steps.extend(fraction_steps)
            
            # Simplificación
            steps.append("🔧 SIMPLIFICACIÓN:")
            simplified = simplify(expr)
            
            if simplified != expr:
                steps.append(f"   📐 Aplicamos simplificación: {expr} → {simplified}")
                steps.append("   💡 Buscamos el máximo común divisor (MCD) del numerador y denominador")
            else:
                steps.append("   ℹ️ La fracción ya está en su forma más simple")
            
            # Resultado exacto
            if simplified.is_rational:
                fraction = sp.nsimplify(simplified)
                steps.append(f"✅ FRACCIÓN EXACTA: {fraction}")
                
                # Conversión a decimal
                decimal_val = float(fraction)
                steps.append(f"🔢 EQUIVALENTE DECIMAL: {fraction} = {decimal_val}")
                
                # Información adicional
                if hasattr(fraction, 'p') and hasattr(fraction, 'q'):
                    steps.append(f"📊 Numerador: {fraction.p}")
                    steps.append(f"📊 Denominador: {fraction.q}")
                
                return {
                    'result': f"🔢 Fracción exacta: {fraction} = {decimal_val}",
                    'steps': steps,
                    'type': 'fraction'
                }
            else:
                return {
                    'result': f"🔢 Resultado: {simplified}",
                    'steps': steps,
                    'type': 'fraction'
                }
                
        except Exception as e:
            return {
                'result': f"❌ Error: {str(e)}",
                'steps': [f"❌ Error en fracciones: {str(e)}"],
                'type': 'error'
            }
    
    def _detect_fraction_operation_type(self, expression):
        """Detecta el tipo de operación con fracciones"""
        if '+' in expression:
            return "SUMA DE FRACCIONES"
        elif '-' in expression:
            return "RESTA DE FRACCIONES"
        elif '*' in expression:
            return "MULTIPLICACIÓN DE FRACCIONES"
        elif expression.count('/') > 1:
            return "DIVISIÓN DE FRACCIONES"
        else:
            return "SIMPLIFICACIÓN DE FRACCIÓN"
    
    def _explain_fraction_addition_subtraction(self, expression):
        """Explica suma y resta de fracciones"""
        steps = []
        steps.append("➕ SUMA/RESTA DE FRACCIONES:")
        steps.append("   📐 Regla: a/b ± c/d = (ad ± bc)/(bd)")
        steps.append("   💡 Necesitamos un denominador común")
        steps.append("🔧 PASOS:")
        steps.append("   1️⃣ Encontrar el mínimo común múltiplo (MCM) de los denominadores")
        steps.append("   2️⃣ Convertir cada fracción al denominador común")
        steps.append("   3️⃣ Sumar/restar los numeradores")
        steps.append("   4️⃣ Simplificar el resultado")
        return steps
    
    def _explain_fraction_multiplication(self, expression):
        """Explica multiplicación de fracciones"""
        steps = []
        steps.append("✖️ MULTIPLICACIÓN DE FRACCIONES:")
        steps.append("   📐 Regla: (a/b) × (c/d) = (a×c)/(b×d)")
        steps.append("   💡 Multiplicamos numeradores entre sí y denominadores entre sí")
        steps.append("🔧 PASOS:")
        steps.append("   1️⃣ Multiplicar numeradores: a × c")
        steps.append("   2️⃣ Multiplicar denominadores: b × d")
        steps.append("   3️⃣ Simplificar si es posible")
        return steps
    
    def _explain_fraction_division(self, expression):
        """Explica división de fracciones"""
        steps = []
        steps.append("➗ DIVISIÓN DE FRACCIONES:")
        steps.append("   📐 Regla: (a/b) ÷ (c/d) = (a/b) × (d/c)")
        steps.append("   💡 Dividir es multiplicar por el recíproco")
        steps.append("🔧 PASOS:")
        steps.append("   1️⃣ Cambiar división por multiplicación")
        steps.append("   2️⃣ Invertir la segunda fracción (recíproco)")
        steps.append("   3️⃣ Multiplicar como fracciones normales")
        steps.append("   4️⃣ Simplificar el resultado")
        return steps
    
    # ==================== MÉTODOS AUXILIARES ====================
    def _clean_expression(self, expression):
        """Limpia la expresión"""
        expression = expression.strip()
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        expression = expression.replace('^', '**')
        return expression
    
    def _validate_expression(self, expression):
        """Valida que la expresión sea válida"""
        allowed_pattern = r'^[0-9+\-*/().,\s\w]*$'
        if not re.match(allowed_pattern, expression):
            return False
        return self._check_parentheses_balance(expression)
    
    def _check_parentheses_balance(self, expression):
        """Verifica balance de paréntesis"""
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
                if count < 0:
                    return False
        return count == 0
    
    def _replace_functions_and_constants(self, expression):
        """Reemplaza funciones matemáticas"""
        expression = expression.replace('pi', str(math.pi))
        expression = expression.replace('e', str(math.e))
        
        function_replacements = {
            'sqrt': 'math.sqrt', 'sin': 'math.sin', 'cos': 'math.cos',
            'tan': 'math.tan', 'log': 'math.log10', 'ln': 'math.log',
            'exp': 'math.exp', 'abs': 'abs'
        }
        
        for func_name, func_replacement in function_replacements.items():
            pattern = r'\b' + func_name + r'\b'
            expression = re.sub(pattern, func_replacement, expression)
        
        return expression
    
    def _safe_eval(self, expression):
        """Evalúa expresión de forma segura"""
        safe_dict = {
            "__builtins__": {},
            "math": math, "abs": abs, "round": round,
            "pow": pow, "max": max, "min": min
        }
        
        try:
            result = eval(expression, safe_dict)
            if isinstance(result, (int, float)):
                if math.isinf(result):
                    raise ValueError("Resultado infinito")
                elif math.isnan(result):
                    raise ValueError("Resultado no válido")
                return result
            else:
                raise ValueError("Resultado no numérico")
        except ZeroDivisionError:
            raise ZeroDivisionError("División por cero")
        except Exception as e:
            raise ValueError(f"Error: {str(e)}")
    
    def is_valid_expression(self, expression):
        """Verifica si es una expresión matemática válida"""
        if not expression or len(expression) < 1:
            return False
        
        math_functions = ['sin', 'cos', 'tan', 'sqrt', 'log', 'ln', 'pi', 'e', 
                         'derivative', 'integral', 'diff', 'Matrix', 'd/dx']
        variables = ['x', 'y', 'z', 't']
        
        has_numbers = any(c.isdigit() for c in expression)
        has_operators = any(c in '+-*/=' for c in expression)
        has_functions = any(func in expression.lower() for func in math_functions)
        has_variables = any(var in expression for var in variables)
        has_matrices = '[' in expression and ']' in expression
        
        return (has_numbers and (has_operators or has_functions)) or has_variables or has_matrices
    
    def get_operation_info(self, expression):
        """Obtiene información sobre la operación"""
        info = {
            'expression': expression,
            'type': 'unknown',
            'complexity': 'simple'
        }
        
        if self._is_equation(expression):
            info['type'] = 'equation'
        elif self._is_matrix_operation(expression):
            info['type'] = 'matrix'
        elif self._is_derivative(expression):
            info['type'] = 'derivative'
        elif self._is_integral(expression):
            info['type'] = 'integral'
        elif self._contains_variables(expression):
            info['type'] = 'symbolic'
        elif self._is_fraction(expression):
            info['type'] = 'fraction'
        else:
            info['type'] = 'basic_operations'
        
        return info