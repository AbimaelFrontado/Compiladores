import csv
from collections import defaultdict

EPSILON = 'epsilon'
ENDMARKER = '$'

class LL1Grammar:
    def __init__(self, productions):
        self.productions = productions
        self.non_terminals = set(productions.keys())
        self.terminals = self._find_terminals()
        self.first = defaultdict(set)
        self.follow = defaultdict(set)
        self.table = defaultdict(dict)

    def _find_terminals(self):
        return {
            symbol
            for prods in self.productions.values()
            for prod in prods
            for symbol in prod
            if symbol not in self.productions and symbol != EPSILON
        }

    def compute_first(self):
        # FIRST de terminales es el terminal mismo
        for terminal in self.terminals:
            self.first[terminal].add(terminal)
        self.first[EPSILON].add(EPSILON) # FIRST de epsilon es epsilon

        changed = True
        while changed:
            changed = False
            for nt, prods in self.productions.items():
                for prod in prods:
                    new_first = self._get_prod_first(prod)
                    if not new_first.issubset(self.first[nt]):
                        self.first[nt].update(new_first)
                        changed = True

    def _get_prod_first(self, prod):
        result = set()
        for symbol in prod:
            result.update(self.first[symbol])
            if EPSILON not in self.first[symbol]:
                return result
        result.add(EPSILON)
        return result

    def compute_follow(self):
        # Agregar $ al FOLLOW del símbolo inicial
        start_symbol = next(iter(self.productions))
        self.follow[start_symbol].add(ENDMARKER)

        # Agregar FOLLOW vacío a todos los terminales
        for terminal in self.terminals:
            self.follow[terminal] = set()

        changed = True
        while changed:
            changed = False
            for nt, prods in self.productions.items():
                for prod in prods:
                    trailer = self.follow[nt].copy()
                    for symbol in reversed(prod):
                        if symbol in self.non_terminals:
                            if not trailer.issubset(self.follow[symbol]):
                                self.follow[symbol].update(trailer)
                                changed = True
                            if EPSILON in self.first[symbol]:
                                trailer.update(self.first[symbol] - {EPSILON})
                            else:
                                trailer = self.first[symbol]
                        else:
                            trailer = {symbol}

    def build_parsing_table(self):
        for nt, prods in self.productions.items():
            for prod in prods:
                first_set = self._get_prod_first(prod)

                # Para cada terminal en FIRST(prod), agregar la producción
                for terminal in first_set - {EPSILON}:
                    if terminal in self.table[nt]:
                        print(f"Conflicto en tabla[{nt}][{terminal}]: ya tiene {self.table[nt][terminal]}, intentando agregar {prod}")
                    self.table[nt][terminal] = prod

                # Si epsilon está en FIRST, agregar producción para todos los terminales en FOLLOW(nt)
                if EPSILON in first_set:
                    for terminal in self.follow[nt]:
                        if terminal in self.table[nt]:
                            # Solo permitimos conflicto si es la misma producción
                            if self.table[nt][terminal] != prod:
                                print(f"Conflicto en tabla[{nt}][{terminal}]: ya tiene {self.table[nt][terminal]}, intentando agregar {prod}")
                        else:
                            self.table[nt][terminal] = prod

    def export_table_to_csv(self, filename="tabla_ll1.csv"):
        headers = sorted(list(self.terminals) + [EPSILON, ENDMARKER])
        non_terminals = sorted(self.non_terminals)

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([""] + headers)
            for nt in non_terminals:
                row = [nt]
                for terminal in headers:
                    if terminal in self.table[nt]:
                        production = self.table[nt][terminal]
                        formatted = ' '.join(symbol for symbol in production)
                        row.append(formatted)
                    else:
                        row.append("")
                writer.writerow(row)

    def print_first_follow(self):
        print("Conjuntos FIRST:")
        for symbol in sorted(self.first):
            content = ', '.join(self.first[symbol])
            print(f"FIRST({symbol}) = {{{content}}}")

        print("\nConjuntos FOLLOW:")
        for symbol in sorted(self.follow):
            content = ', '.join(self.follow[symbol])
            print(f"FOLLOW({symbol}) = {{{content}}}")


# ==== EJEMPLO DE USO ====
if __name__ == "__main__":
    grammar = {
         "Programa": [["Sentencia", "Programa"], ["Funcion", "Programa"], [EPSILON]],
        "Sentencia": [ ["Imprimir", "(", "Expresion", ")"], ["Si", "(", "Condicion", ")", "{", "ListaSentencias", "}", "SinoOpcional"], ["Asignacion"], ["Para", "(", "Iterador", "en", "Numero", "RangoOpcional", ")", "{", "ListaSentencias", "}"], ["Mientras", "(", "Condicion", ")", "{", "ListaSentencias", "}"], ["Break"] ],
        "Funcion": [["Func", "Tipo", "Identificador", "(", "ListaParametrosOpcional", ")", "{", "ListaSentencias", "RetornoOpcional", "}"]], 
        "ListaParametrosOpcional": [["ListaParametros"], [EPSILON]],
        "ListaParametros": [["Asignacion", "ListaParametros'"]],
        "ListaParametros'": [[",", "Asignacion", "ListaParametros'"], [EPSILON]], 
        "Parametros": [["Asignacion"], [EPSILON]], 
        "RangoOpcional": [["Incremento", "Numero"], [EPSILON]], 
        "RetornoOpcional": [["Retornar", "ValorRetorno"], [EPSILON]],
        "ValorRetorno": [[EPSILON], ["Identificador"], ["Expresion"]], 
        "SinoOpcional": [["Sino", "Sentencia"], [EPSILON]], 
        "ListaSentencias": [["Sentencia", "ListaSentencias"], [EPSILON]], 
        "Asignacion": [["Tipo", "Identificador", "AsignacionOpcional"]],
        "AsignacionOpcional": [[EPSILON], ["OperadorAritmetico", "Identificador"]], 
        "Tipo": [["Entero"], ["Decimal"], ["Texto"]],
        "Identificador": [["Id"], ["Numero"], ["Literal"]], 
        "OperadorAritmetico": [["+"], ["-"], ["/"], ["*"], ["="]],
        "OperadorRelacional": [["<="], [">="], ["=="], ["!="]],
        "OperadorLogico": [["y", "Condicion"], ["o", "Condicion"], [EPSILON]], 
        "Condicion": [["Expresion", "OperadorRelacional", "Expresion", "OperadorLogico"]], 
        "Expresion": [["Termino", "Expresion'"]],
        "Expresion'": [["OperadorAritmetico", "Termino", "Expresion'"], [EPSILON]], 
        "Termino": [["Identificador", "OperacionSecundaria"], ["(", "Expresion", ")"]],
        "OperacionSecundaria": [["OperadorAritmetico", "Termino"], [EPSILON]],
    }

    parser = LL1Grammar(grammar)
    parser.compute_first()
    parser.compute_follow()
    parser.build_parsing_table()
    parser.print_first_follow()
    parser.export_table_to_csv()
    print("\nTabla sintáctica exportada a 'tabla_ll1.csv'")
