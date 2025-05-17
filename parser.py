import csv
import re

# Definiciones léxicas (tokens y sus patrones)
token_specification = [
    # Palabras clave
    ('Imprimir',  r'Imprimir'),
    ('Sino',      r'Sino'),
    ('Si',        r'Si'), 
    ('Para',      r'Para'),
    ('Mientras',  r'Mientras'),
    ('Break',     r'Break'),
    ('Func',      r'Func'),
    ('Retornar',  r'Retornar'),
    ('en',        r'en'),
    
    # Tipos de datos
    ('Entero',    r'Entero'),
    ('Decimal',   r'Decimal'),
    ('Texto',     r'Texto'),
    
    # Identificadores y valores
    ('Numero',    r'\d+(\.\d+)?'),
    ('Identificador', r'[a-zA-Z_]\w*'),
    ('Literal',   r'"[^"\n]*"'),
    
    # Operadores
    ('OperadorAritmetico', r'[\+\-\*/=]'),
    ('OperadorRelacional', r'(<=|>=|==|!=|<|>)'),
    ('OperadorLogico',     r'\b(y|o)\b'),
    
    # Símbolos y puntuación
    ('LParen',    r'\('),
    ('RParen',    r'\)'),
    ('LBrace',    r'\{'),
    ('RBrace',    r'\}'),
    ('Comma',     r','),
    
    # Espacios y comentarios
    ('SKIP',      r'[ \t]+'),
    ('NEWLINE',   r'\n'),
    ('MISMATCH',  r'.'),  # Para detectar errores léxicos
]

token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)

def lexer(code):
    tokens = []
    for mo in re.finditer(token_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'Numero':
            tokens.append(('Numero' ))
        elif kind == 'Imprimir':
            tokens.append(('Imprimir'))      
        elif kind == 'Sino':
            tokens.append(('Sino'))   
        elif kind == 'Si':
            tokens.append(('Si'))   
        elif kind == 'Para':
            tokens.append(('Para'))  
        elif kind == 'Mientras':
            tokens.append(('Mientras'))   
        elif kind == 'Break':
            tokens.append(('Break'))   
        elif kind == 'Func':
            tokens.append(('Func'))   
        elif kind == 'Retornar':
            tokens.append(('retornar'))   
        elif kind == 'En':
            tokens.append(('En'))  
        elif kind == 'Entero':
            tokens.append(('Entero'))   
        elif kind == 'Decimal':
            tokens.append(('Decimal'))   
        elif kind == 'Texto':
            tokens.append(('Texto'))   
        elif kind == 'Identificador':
            tokens.append(('Identificador')) 
        elif kind == 'Literal':
            tokens.append(('Literal'))
        elif kind in ('OperadorAritmetico', 'OperadorRelacional', 'OperadorLogico', 'LParen', 'RParen', 'LBrace', 'RBrace', 'Comma'):
            tokens.append((value ))  # Tratamos operadores y signos como su propio tipo
        elif kind == 'SKIP' or kind == 'NEWLINE':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Caracter inesperado: {value}')
    return tokens
class Node:
    _counter = 1  # Variable de clase para llevar la cuenta
    
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children is not None else []
        self.id = Node._counter
        Node._counter += 1
    
    def __str__(self):
        return f"{self.value}"
    
    def add_child(self, child_node):
        self.children.append(child_node)
    
    def to_dot(self):
        dot_str = f'  node_{self.id} [label="{self.value}"];\n'
        for child in self.children:
            dot_str += child.to_dot()
            dot_str += f'  node_{self.id} -> node_{child.id};\n'
        return dot_str
    
def cargar_grammar_desde_csv(nombre_archivo):
    tabla = {}
    with open(nombre_archivo, newline='') as csvfile:
        lector = csv.reader(csvfile)
        encabezados = next(lector)[1:]  # Saltamos la primera celda vacía

        for fila in lector:
            no_terminal = fila[0]
            producciones = fila[1:]
            tabla[no_terminal] = {}

            for terminal, produccion in zip(encabezados, producciones):
                if produccion == '':
                    tabla[no_terminal][terminal] = None
                else:
                    produccion = produccion.strip()
                    if produccion == 'epsilon':
                        tabla[no_terminal][terminal] = ['epsilon']
                    else:
                        tabla[no_terminal][terminal] = produccion.split()
    return tabla

def parse(input_str):
    tokens = lexer(input_str) + ['$']
    stack = ['$', 'Programa']
    node_stack = []
    root_node = Node('Programa')  # Nodo raíz inicial
    node_stack.append(root_node)
    
    productions = cargar_grammar_desde_csv('tabla_ll1.csv')
    
    print("Tokens:", tokens)
    i = 0

    while True:
        print(f"Pila: {stack}, Índice de Entrada: {i}, Token Actual: {tokens[i]}")

        if not stack:
            print("Error: Pila vacía antes de terminar el análisis.")
            return None

        x = stack.pop()
        current_node = node_stack.pop() if node_stack else None
        
        # Manejo especial para el símbolo $
        if x == '$' and tokens[i] == '$':
            print("Análisis exitoso!")
            return root_node

        actual = tokens[i] 

        if x == "epsilon":
            print(f"  Acción: Procesar epsilon (continuar)")
            epsilon_node = Node('ε')
            if current_node:
                current_node.add_child(epsilon_node)
            continue
        elif x == actual:
            print(f"  Acción: Coincidencia de terminal '{x}'")
            if current_node:
                current_node.value = actual
            i += 1
        elif x in productions:
            production_rule = productions[x].get(actual)
            print(f"  Acción: Expandir no-terminal '{x}' con entrada '{actual}'")

            if production_rule:
                print(f"    Usando regla: {x} -> {' '.join(production_rule)}")
                # Guardamos los nodos hijos temporalmente
                temp_children = []
                for symbol in reversed(production_rule):
                    if symbol != "epsilon":
                        stack.append(symbol)
                        new_node = Node(symbol)
                        temp_children.append(new_node)
                
                # Los hijos deben estar en orden normal (no invertido)
                temp_children.reverse()
                if current_node:
                    current_node.children = temp_children
                    # Empujamos los hijos a la pila para procesarlos después
                    node_stack.extend(reversed(temp_children))
            else:
                print(f"Error de Sintaxis: No hay regla para el no-terminal '{x}' con el token de entrada '{actual}'")
                return None
        else:
            print(f"Error de Sintaxis: Se esperaba el terminal '{x}' pero se encontró '{actual}'")
            return None

def generate_dot(root_node, filename='arbol.dot'):
    if root_node is None:
        print("No se puede generar DOT: árbol sintáctico es None")
        return
    
    dot_content = f"digraph arbol {{\n{root_node.to_dot()}}}"
    with open(filename, 'w') as f:
        f.write(dot_content)
    print(f"Código DOT generado en: {filename}")
 
def leer_entradas_desde_txt(nombre_archivo):
    try:
        with open(nombre_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().strip()
            return contenido if contenido else None
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{nombre_archivo}'")
        return None

entrada = leer_entradas_desde_txt('Ejemplos.txt')

if not entrada :
    print(" El archivo 'Ejemplos.txt' está vacío o no contiene entradas válidas.")
else: 
        
    ast_root = parse(entrada)
    if ast_root:
        print("  Resultado: La cadena es válida.")
        generate_dot(ast_root,  'arbol.dot')
    else:
        print(" Resultado: La cadena NO es válida.")

      








