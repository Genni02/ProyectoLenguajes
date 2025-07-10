import sympy as sp
from typing import Union, Dict, Any

def safe_sympify(expression: str, variables: Dict[str, Any] = None) -> Union[sp.Expr, None]:
    """
    Intenta convertir una expresión en un objeto sympy de manera segura.
    
    Args:
        expression: La expresión matemática a convertir
        variables: Diccionario de variables definidas
        
    Returns:
        Un objeto sympy.Expr o None si hay error
    """
    try:
        # Reemplazar símbolos especiales
        expr = expression.replace("π", "pi").replace("√", "sqrt")
        
        # Evaluar con sympy
        if variables:
            return sp.sympify(expr, locals=variables)
        return sp.sympify(expr)
    except (sp.SympifyError, TypeError, AttributeError):
        return None

def format_result(result: Any) -> str:
    """
    Formatea el resultado para mostrarlo de manera legible.
    
    Args:
        result: El resultado a formatear
        
    Returns:
        Una representación en cadena del resultado
    """
    if isinstance(result, (sp.Expr, sp.Float, sp.Integer, sp.Rational)):
        return sp.pretty(result)
    return str(result)

def validate_expression(expression: str) -> bool:
    """
    Valida que una expresión matemática sea sintácticamente correcta.
    
    Args:
        expression: La expresión a validar
        
    Returns:
        True si es válida, False en caso contrario
    """
    try:
        sp.sympify(expression)
        return True
    except sp.SympifyError:
        return False