"""Small arithmetic language; never evaluates Python code."""
import ast
import math
import operator

OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod}


def calculate(expression):
    if not isinstance(expression, str) or not 0 < len(expression) <= 256:
        raise ValueError('Expression must contain 1..256 characters')
    tree = ast.parse(expression, mode='eval')
    if sum(1 for _ in ast.walk(tree)) > 100:
        raise ValueError('Expression is too complex')

    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            value = node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand) * (-1 if isinstance(node.op, ast.USub) else 1)
        elif isinstance(node, ast.BinOp) and type(node.op) in OPS:
            value = OPS[type(node.op)](visit(node.left), visit(node.right))
        else:
            raise ValueError('Only numbers, parentheses and + - * / // % are allowed')
        if abs(value) > 1e15 or not math.isfinite(value):
            raise ValueError('Result out of range')
        return value
    return visit(tree.body)


def response(expression):
    try:
        return {'ok': True, 'result': calculate(expression)}
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError, RecursionError) as error:
        return {'ok': False, 'error': str(error)}
