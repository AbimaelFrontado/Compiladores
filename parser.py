import csv


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
    stack = ['$','E']
   
    productions = cargar_grammar_desde_csv('grammar_table.csv')


   
    print("Tokens:", tokens)




    i = 0




    while True:
        print(f"Pila: {stack}, Índice de Entrada: {i}, Token Actual: {tokens[i]}")




        if not stack:
             print("Error: Pila vacía antes de terminar el análisis.")
             return False




        x = stack.pop()
        actual = tokens[i]




        if x == "epsilon" :


            print(f"  Acción: Procesar epsilon (continuar)")
            continue
        elif x == actual :


            print(f"  Acción: Coincidencia de terminal '{x}'")
            i+=1
            if x == '$':
                print("Análisis exitoso!")
                return True
           
        elif x in productions :


            production_rule = productions[x].get(actual)
            print(f"  Acción: Expandir no-terminal '{x}' con entrada '{actual}'")




            if production_rule:
                print(f"    Usando regla: {x} -> {' '.join(production_rule)}")




                for symbol in reversed(production_rule):
                    if symbol != "epsilon":
                        stack.append(symbol)


            else:


                print(f"Error de Sintaxis: No hay regla para el no-terminal '{x}' con el token de entrada '{actual}'")
                return False
           
        else:


            print(f"Error de Sintaxis: Se esperaba el terminal '{x}' pero se encontró '{actual}'")
            return False
       


entrada = "int + int"
if parse(entrada):
    print("Resultado: La cadena es válida.")
else:
    print("Resultado: La cadena NO es válida.")
