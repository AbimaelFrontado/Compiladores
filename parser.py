import csv

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
    tokens = input_str.split() + ['$']
    stack = ['$', 'E']
    node_stack = []
    root_node = Node('E')  # Nodo raíz inicial
    node_stack.append(root_node)
    
    productions = cargar_grammar_desde_csv('grammar_table.csv')
    
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
 
 

# Ejemplo de uso
entrada = "int + int"
ast_root = parse(entrada)
if ast_root:
    print("\nResultado: La cadena es válida.")
    generate_dot(ast_root)
else:
    print("\nResultado: La cadena NO es válida.")
