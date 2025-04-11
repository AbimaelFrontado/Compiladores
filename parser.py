import csv
import sys

class BottomUpParser:
    def __init__(self, csv_file):
        # Cargar la tabla de análisis desde CSV
        self.table = {}
        self.states = set()
        self.symbols = []
        
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Leer encabezados
            self.symbols = headers[1:]  # Todos los símbolos (terminales y no terminales)
            
            for row in reader:
                state = int(row[0])
                self.states.add(state)
                self.table[state] = {}
                
                for i, symbol in enumerate(self.symbols):
                    value = row[i+1].strip() if i+1 < len(row) else ''
                    self.table[state][symbol] = value if value else None
    
    def parse(self, tokens, line=1, col=1):
        tokens = list(tokens) + ['$']  # Añadir símbolo de fin
        pointer = 0
        current_col = col
        self.stack = ['$', 0]  # Reiniciar pila
        
        while True:
            current_state = self.stack[-1]
            current_token = tokens[pointer]
            
            # Obtener acción de la tabla
            action = self.get_action(current_state, current_token)
            
            # Manejar error
            if action is None:
                expected = self.get_expected_symbols(current_state)
                return {
                    'status': 'error',
                    'message': f"Error sintáctico en línea {line}, columna {current_col}",
                    'details': f"Token inesperado: '{current_token}'. Se esperaba: {expected}"
                }
            
            # Desplazamiento
            if action.startswith('s'):
                state = int(action[1:])
                self.stack.append(current_token)
                self.stack.append(state)
                pointer += 1
                current_col += len(current_token) if current_token != 'int' else 3
                
            # Reducción
            elif action.startswith('r'):
                prod_num = int(action[1:])
                lhs, rhs_len = self.get_production(prod_num)
                
                # Desapilar
                if rhs_len > 0:
                    self.stack = self.stack[:-2*rhs_len]
                
                # Obtener nuevo estado
                new_state = self.stack[-1]
                goto = self.get_goto(new_state, lhs)
                
                if goto is None:
                    return {
                        'status': 'error',
                        'message': f"Error de sintaxis después de reducir {lhs} → {' '.join(['...']*rhs_len)}",
                        'details': f"No se encontró transición para {lhs} en estado {new_state}"
                    }
                
                # Apilar
                self.stack.append(lhs)
                self.stack.append(goto)
                
            # Aceptación
            elif action == 'acc':
                return {
                    'status': 'success',
                    'message': "La entrada pertenece al lenguaje (gramática)"
                }
            
            else:
                return {
                    'status': 'error',
                    'message': "Acción desconocida en la tabla de análisis",
                    'details': f"Acción: {action}, Estado: {current_state}, Token: {current_token}"
                }
    
    def get_action(self, state, symbol):
        try:
            action = self.table[state].get(symbol, None)
            return action if action != '' else None
        except KeyError:
            return None
    
    def get_goto(self, state, symbol):
        try:
            goto = self.table[state].get(symbol, None)
            return int(goto) if goto and goto.isdigit() else None
        except KeyError:
            return None
    
    def get_expected_symbols(self, state):
        expected = []
        for symbol, action in self.table[state].items():
            if action and action != '':
                expected.append(symbol)
        return expected or ["ningún símbolo (error en tabla)"]
        
    def get_production(self, num):
        productions = {
            1: ('E', 1),  # E → T X
            2: ('X', 3),  # X → + E
            3: ('X', 0),  # X → ε
            4: ('T', 3),  # T → ( E )
            5: ('T', 2),  # T → int Y
            6: ('Y', 3),  # Y → * T
            7: ('Y', 0),  # Y → ε
        }
        return productions.get(num, (None, None))

def main():
    if len(sys.argv) < 3:
        print("Uso: python parser.py <archivo_csv> <tokens> [línea] [columna]")
        print("Ejemplo: python parser.py grammar_table.csv 'int * int' 1 1")
        return
    
    csv_file = sys.argv[1]
    input_tokens = sys.argv[2].split()
    line = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    col = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    
    try:
        parser = BottomUpParser(csv_file)
        result = parser.parse(input_tokens, line, col)
        
        print("\nResultado del análisis:")
        print(result['message'])
        if result['status'] == 'error':
            print(result['details'])
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {csv_file}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    main()
