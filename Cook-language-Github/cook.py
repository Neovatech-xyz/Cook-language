import sys
import re

# ==========================================
# 1. Lexer (字句解析)
# ==========================================
class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.tokenize()
        
    def tokenize(self):
        token_specification = [
            ('START',     r'\bstart\b'),
            ('END',       r'\bend\b'),
            ('CONSOLE',   r'console\.write'),
            ('FAST_IF',   r'\bfast check if\b'),
            ('ELSE_IF',   r'\bsecond check else if\b'),
            ('ELSE',      r'\bthird check else\b'),
            ('REPEAT',    r'\brepeat this block code\b'),
            ('CREATE_VAR',r'\bcreate variable name equal\b'),
            ('CREATE_CONST', r'\bcreate constant name equal\b'),
            ('CREATE_FUNC', r'\bcreate function name equal\b'),
            ('ARGS_EQUAL',r'\barguments name equal\b'),
            ('USE_LIB',   r'\buse library name equal\b'),
            ('IN',        r'\bin\b'),
            ('NOT',       r'\bnot\b'),
            ('INC',       r'\+\+'),
            ('DEC',       r'--'),
            ('POWER',     r'\bpower\b|\*\*'),
            ('PLUS',      r'\bplus\b|\+'),
            ('MINUS',     r'\bminus\b|-'),
            ('TIMES',     r'\btimes\b|\*'),
            ('COMMENT',   r'//.*'),
            ('DIV',       r'\bdivided by\b|/'),
            ('MOD',       r'\bmod\b|%'),
            ('EQUAL_SYM', r'=='),
            ('ASSIGN',    r'='),
            ('EQUAL_WORD',r'\bequal\b'),
            ('GT',        r'>'),
            ('LT',        r'<'),
            ('COLON',     r':'),
            ('COMMA',     r','),
            ('LPAREN',    r'\('),
            ('RPAREN',    r'\)'),
            ('STRING',    r'"[^"]*"'),
            ('NUMBER',    r'\d+(\.\d+)?'),
            ('ID',        r'[A-Za-z_]\w*'),
            ('NEWLINE',   r'\n'),
            ('SKIP',      r'[ \t]+'),
            ('MISMATCH',  r'.'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        for mo in re.finditer(tok_regex, self.code):
            kind = mo.lastgroup
            value = mo.group()
            if kind in ['COMMENT', 'SKIP', 'NEWLINE']:
                continue
            elif kind == 'MISMATCH':
                if value in ['\r', '\n']:
                    continue
                raise RuntimeError(f'Unexpected character {repr(value)}')
            else:
                self.tokens.append((kind, value))
        self.tokens.append(('EOF', ''))

# ==========================================
# 2. Parser (構文解析)
# ==========================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_kind=None):
        tok = self.tokens[self.pos]
        if expected_kind and tok[0] != expected_kind:
            raise SyntaxError(f"Expected {expected_kind}, got {tok[0]} ('{tok[1]}')")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek()[0] != 'EOF':
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        kind = self.peek()[0]
        if kind == 'USE_LIB':
            self.consume()
            lib_name = self.consume('ID')[1]
            return ('USE_LIB', lib_name)
        elif kind == 'CREATE_VAR' or kind == 'CREATE_CONST':
            is_const = (kind == 'CREATE_CONST')
            self.consume()
            name = self.consume('ID')[1]
            self.consume('IN')
            expr = self.parse_expression()
            return ('CONST_DECL' if is_const else 'VAR_DECL', name, expr)
        elif kind == 'CREATE_FUNC':
            self.consume()
            name = self.consume('ID')[1]
            args = []
            if self.peek()[0] == 'ARGS_EQUAL':
                self.consume()
                while self.peek()[0] == 'ID':
                    args.append(self.consume('ID')[1])
                    if self.peek()[0] == 'COMMA':
                        self.consume('COMMA')
                    else:
                        break
            self.consume('COLON')
            block = self.parse_block()
            return ('FUNC_DECL', name, args, block)
        elif kind == 'CONSOLE':
            self.consume()
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return ('PRINT', expr)
        elif kind == 'FAST_IF':
            self.consume()
            has_not = False
            if self.peek()[0] == 'NOT':
                self.consume()
                has_not = True
            cond = self.parse_expression()
            self.consume('COLON')
            true_block = self.parse_block()
            
            elifs = []
            while self.peek()[0] == 'ELSE_IF':
                self.consume()
                elcond = self.parse_expression()
                self.consume('COLON')
                elblock = self.parse_block()
                elifs.append((elcond, elblock))
                
            false_block = None
            if self.peek()[0] == 'ELSE':
                self.consume()
                self.consume('COLON')
                false_block = self.parse_block()
                
            return ('IF', has_not, cond, true_block, elifs, false_block)
        elif kind == 'REPEAT':
            self.consume()
            cond = self.parse_expression()
            self.consume('COLON')
            block = self.parse_block()
            return ('WHILE', cond, block)
        elif kind == 'ID':
            # Assignment or function call
            name = self.consume('ID')[1]
            if self.peek()[0] == 'LPAREN':
                self.consume('LPAREN')
                args = []
                while self.peek()[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    if self.peek()[0] == 'COMMA':
                        self.consume('COMMA')
                self.consume('RPAREN')
                return ('CALL', name, args)
            elif self.peek()[0] == 'INC':
                self.consume()
                return ('ASSIGN', name, ('BINOP', '+', ('VAR', name), ('NUM', 1)))
            elif self.peek()[0] == 'DEC':
                self.consume()
                return ('ASSIGN', name, ('BINOP', '-', ('VAR', name), ('NUM', 1)))
            elif self.peek()[0] in ('IN', 'ASSIGN', 'EQUAL_WORD'):
                self.consume()
                expr = self.parse_expression()
                return ('ASSIGN', name, expr)
            else:
                raise SyntaxError(f"Unexpected token after ID: {self.peek()}")
        elif kind == 'START':
            return ('BLOCK', self.parse_block())
        else:
            raise SyntaxError(f"Unknown statement starting with {self.peek()}")

    def parse_block(self):
        self.consume('START')
        stmts = []
        while self.peek()[0] != 'END' and self.peek()[0] != 'EOF':
            stmts.append(self.parse_statement())
        self.consume('END')
        return stmts

    def parse_expression(self):
        left = self.parse_term()
        while self.peek()[0] in ('GT', 'LT', 'EQUAL_SYM', 'PLUS', 'MINUS', 'TIMES', 'DIV', 'MOD', 'POWER'):
            op = self.consume()[1]
            if op == 'plus': op = '+'
            elif op == 'minus': op = '-'
            elif op == 'times': op = '*'
            elif op == 'divided by': op = '/'
            elif op == 'mod': op = '%'
            elif op == 'power': op = '**'
            right = self.parse_term()
            left = ('BINOP', op, left, right)
        return left

    def parse_term(self):
        kind, val = self.peek()
        if kind == 'MINUS':
            self.consume()
            return ('BINOP', '-', ('NUM', 0), self.parse_term())
        elif kind == 'PLUS':
            self.consume()
            return self.parse_term()
        elif kind == 'NUMBER':
            self.consume()
            if '.' in val:
                return ('NUM', float(val))
            return ('NUM', int(val))
        elif kind == 'STRING':
            self.consume()
            return ('STR', val[1:-1])
        elif kind == 'ID':
            name = self.consume()[1]
            if self.peek()[0] == 'LPAREN':
                self.consume()
                args = []
                while self.peek()[0] != 'RPAREN':
                    args.append(self.parse_expression())
                    if self.peek()[0] == 'COMMA':
                        self.consume()
                self.consume('RPAREN')
                return ('CALL_EXPR', name, args)
            return ('VAR', name)
        else:
            raise SyntaxError(f"Unexpected token in expression: {val}")

# ==========================================
# 3. Evaluator (評価器・インタプリタ)
# ==========================================
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.constants = set()
        self.parent = parent
    def set(self, name, value, is_const=False):
        if name in self.constants:
            raise Exception(f"Cannot redeclare constant '{name}'")
        self.vars[name] = value
        if is_const:
            self.constants.add(name)
    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise Exception(f"Undefined variable '{name}'")
    def assign(self, name, value):
        if name in self.constants:
            raise Exception(f"Cannot assign to constant '{name}'")
        if name in self.vars:
            self.vars[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise Exception(f"Undefined variable '{name}'")

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}

    def evaluate(self, node, env):
        if type(node) is not tuple:
            return None
        kind = node[0]

        if kind == 'NUM':
            return node[1]
        elif kind == 'STR':
            return node[1]
        elif kind == 'VAR':
            return env.get(node[1])
        elif kind == 'BINOP':
            op = node[1]
            left = self.evaluate(node[2], env)
            right = self.evaluate(node[3], env)
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '%': return left % right
            if op == '**': return left ** right
            if op == '>': return left > right
            if op == '<': return left < right
            if op == '==': return left == right
        elif kind == 'USE_LIB':
            lib_name = node[1]
            if lib_name == 'math':
                import math
                env.set('sqrt', math.sqrt, is_const=True)
                env.set('pi', math.pi, is_const=True)
                env.set('floor', math.floor, is_const=True)
                env.set('ceil', math.ceil, is_const=True)
                env.set('abs', abs, is_const=True)
                env.set('round', round, is_const=True)
                env.set('sin', math.sin, is_const=True)
                env.set('cos', math.cos, is_const=True)
                env.set('tan', math.tan, is_const=True)
        elif kind == 'VAR_DECL':
            name = node[1]
            val = self.evaluate(node[2], env)
            env.set(name, val, is_const=False)
        elif kind == 'CONST_DECL':
            name = node[1]
            val = self.evaluate(node[2], env)
            env.set(name, val, is_const=True)
        elif kind == 'FUNC_DECL':
            name = node[1]
            args = node[2]
            body = node[3]
            self.functions[name] = (args, body)
        elif kind == 'ASSIGN':
            name = node[1]
            val = self.evaluate(node[2], env)
            env.assign(name, val)
        elif kind == 'PRINT':
            val = self.evaluate(node[1], env)
            print(val)
        elif kind == 'IF':
            has_not = node[1]
            cond_val = self.evaluate(node[2], env)
            if has_not: cond_val = not cond_val
            
            if cond_val:
                self.execute_block(node[3], Environment(env))
            else:
                executed = False
                for elcond, elblock in node[4]:
                    if self.evaluate(elcond, env):
                        self.execute_block(elblock, Environment(env))
                        executed = True
                        break
                if not executed and node[5]:
                    self.execute_block(node[5], Environment(env))
        elif kind == 'WHILE':
            while self.evaluate(node[1], env):
                self.execute_block(node[2], Environment(env))
        elif kind == 'CALL_EXPR' or kind == 'CALL':
            name = node[1]
            args_eval = [self.evaluate(a, env) for a in node[2]]
            
            try:
                val = env.get(name)
                if callable(val):
                    return val(*args_eval)
            except Exception:
                pass
                
            if name not in self.functions:
                raise Exception(f"Undefined function '{name}'")
            func_args, func_body = self.functions[name]
            local_env = Environment(self.global_env)
            for i, arg_name in enumerate(func_args):
                local_env.set(arg_name, args_eval[i] if i < len(args_eval) else None)
            self.execute_block(func_body, local_env)
            return None

    def execute_block(self, stmts, env):
        for stmt in stmts:
            self.evaluate(stmt, env)

    def run(self, code):
        lexer = Lexer(code)
        parser = Parser(lexer.tokens)
        ast = parser.parse()
        for node in ast:
            self.evaluate(node, self.global_env)

# ==========================================
# 4. Entry Point (実行)
# ==========================================
if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Expected: run cook file name equal main.cook
        # Extract the file name (any argument ending in .cook)
        filename = None
        for arg in sys.argv[1:]:
            if arg.endswith('.cook'):
                filename = arg
                break
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()
            interp = Interpreter()
            interp.run(code)
        else:
            print("Error: Please provide a .cook file.")
            print("Usage: python cook.py run cook file name equal main.cook")
    else:
        print("Cook Language Interpreter")
        print("Usage: python cook.py run cook file name equal main.cook")
