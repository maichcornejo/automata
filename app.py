from flask import Flask, render_template, request, jsonify
from backend.automata import Automata
import graphviz

app = Flask(__name__)

# Global variable to store the automata
automata_global = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_automata')
def create_automata():
    return render_template('automata.html')

@app.route('/submit_automata', methods=['POST'])
def submit_automata():
    global automata_global

    try:
        # Recibe los datos desde el frontend
        data = request.get_json()
        estados = data['estados']
        alfabeto = data['alfabeto']
        transiciones = data['transiciones']
        estado_inicial = data['estado_inicial']
        estados_finales = data['estados_finales']

        errores = []

        # Validación: Verificar que todos los destinos de las transiciones existan y que no se repitan
        for estado, transiciones_estado in transiciones.items():
            for simbolo, destino in transiciones_estado.items():
                # Verificar si destino es una lista (en caso de no determinismo)
                if isinstance(destino, list):
                    # Comprobar si hay duplicados en la lista de destinos
                    if len(destino) != len(set(destino)):
                        errores.append(f"El estado '{estado}' con el símbolo '{simbolo}' tiene estados destino duplicados: {', '.join(destino)}.")
                    # Comprobar si los destinos existen en la lista de estados
                    for d in destino:
                        if d and d not in estados:  
                            errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{d}'.")
                else:
                    if destino and destino not in estados:  
                        errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{destino}'.")

        if errores:
            return jsonify({'error': "\n".join(errores)}), 400

        # Crea una instancia de Automata (no determinístico)
        automata_global = Automata(estados, alfabeto, transiciones, estado_inicial, estados_finales)
        deterministico = automata_global.es_deterministico()
        tabla_transiciones = generar_tabla_transiciones(automata_global)
        graficar_automata(automata_global, deterministic=False)

        # Enviar respuesta JSON con el mensaje de si es determinístico
        mensaje = "El autómata es determinístico." if deterministico else "El autómata NO es determinístico."
        return jsonify({
            'tabla': tabla_transiciones,
            'mensaje': mensaje,
            'deterministico': deterministico
        })
    except Exception as e:
        # Capturar cualquier error y devolver un mensaje
        print(f"Error en submit_automata: {e}")
        return jsonify({'error': f"Error al procesar el autómata: {e}"}), 500


@app.route('/convert_to_deterministic', methods=['POST'])
def convert_to_deterministic():
    global automata_global
    automata_deterministico = automata_global.convertir_a_deterministico()
    tabla_transiciones = generar_tabla_transiciones(automata_deterministico)
    graficar_automata(automata_deterministico, deterministic=True)

    return jsonify({
        'tabla': tabla_transiciones,
        'mensaje': "El autómata ha sido convertido a determinístico.",
        'deterministico': True
    })


def generar_tabla_transiciones(automata):
    tabla_html = "<table border='1'><tr><th>Estado</th>"
    for simbolo in automata.alfabeto:
        tabla_html += f"<th>{simbolo}</th>"
    tabla_html += "</tr>"

    for estado in automata.estados:
        estado_str = estado
        tabla_html += f"<tr><td>{estado_str}</td>"
        for simbolo in automata.alfabeto:
            destino = automata.obtener_transiciones(estado, simbolo)
            destino_str = ','.join(destino) if isinstance(destino, list) else destino if destino else '-'
            tabla_html += f"<td>{destino_str}</td>"
        tabla_html += "</tr>"

    tabla_html += "</table>"
    return tabla_html


def graficar_automata(automata, deterministic=False):
    dot = graphviz.Digraph(comment="Autómata")
    dot.attr(size="6,6!", rankdir='LR', center='true')

    # Añadir los nodos
    for estado in automata.estados:
        estado_str = estado
        if estado in automata.estados_finales:
            dot.node(estado_str, shape='doublecircle')
        else:
            dot.node(estado_str)

    # Añadir el estado inicial
    estado_inicial_str = automata.estado_inicial
    dot.node('', shape='none')
    dot.edge('', estado_inicial_str)

    # Añadir las transiciones, solo si hay un destino válido
    for estado, transiciones_estado in automata.transiciones.items():
        estado_str = estado
        for simbolo, destino in transiciones_estado.items():
            # Verificar si el destino es válido (ni vacío, ni nulo, ni "-")
            if isinstance(destino, list):
                for d in destino:
                    if d and d != "-": 
                        dot.edge(estado_str, d, label=simbolo)  # Dibuja una transición por cada destino
            elif isinstance(destino, str) and destino.strip():  
                dot.edge(estado_str, destino, label=simbolo)

    # Guardar el gráfico como PNG
    output_file = 'automata_graph_deterministic' if deterministic else 'automata_graph'
    dot.render(f'static/{output_file}', format='png', cleanup=True)


@app.route('/validar_cadena', methods=['POST'])
def validar_cadena():
    global automata_global
    try:
        # Obtener la cadena enviada desde el frontend
        data = request.get_json()
        cadena = data['cadena']

        # Validar la cadena con el autómata actual
        if automata_global:
            es_valida = automata_global.validar_cadena(cadena)
            resultado = "La cadena es aceptada." if es_valida else "La cadena no es aceptada."
        else:
            resultado = "El autómata no está definido."

        # Enviar el resultado de la validación al frontend
        return jsonify({ 'resultado': resultado })
    except Exception as e:
        print(f"Error al validar la cadena: {e}")
        return jsonify({ 'error': f"Error al validar la cadena: {e}" }), 500
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')