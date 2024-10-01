from flask import Flask, render_template, request, jsonify
from backend.automata import Automata
import graphviz
import os

app = Flask(__name__)

# Variable global para almacenar el autómata
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

        # Verifica que todos los destinos de las transiciones existan y que no se repitan
        for estado, transiciones_estado in transiciones.items():
            for simbolo, destino in transiciones_estado.items():
                if isinstance(destino, list):
                    if len(destino) != len(set(destino)):
                        errores.append(f"El estado '{estado}' con el símbolo '{simbolo}' tiene estados destino duplicados: {', '.join(destino)}.")
                    for d in destino:
                        if d and d not in estados:
                            errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{d}'.")
                else:
                    if destino and destino not in estados:
                        errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{destino}'.")

        if errores:
            return jsonify({'error': "\n".join(errores)}), 400

        # Instancia el automata no det.
        automata_global = Automata(estados, alfabeto, transiciones, estado_inicial, estados_finales)
        deterministico = automata_global.es_deterministico()

        # Tabla de transiciones y grafico del automata
        tabla_transiciones = generar_tabla_transiciones(automata_global)
        graficar_automata(automata_global, deterministic=deterministico)

        png_filename = 'automata_graph_deterministico.png' if deterministico else 'automata_graph.png'
        png_path = f'/static/{png_filename}'

        # Devolver la respuesta con la tabla y el gráfico
        return jsonify({
            'tabla': tabla_transiciones,
            'png_path': png_path, 
            'mensaje': "El autómata es determinístico." if deterministico else "El autómata NO es determinístico.",
            'deterministico': deterministico
        })

    except Exception as e:
        print(f"Error en submit_automata: {e}")
        return jsonify({'error': f"Error al procesar el autómata: {e}"}), 500


@app.route('/contertir_en_deterministico', methods=['POST'])
def contertir_en_deterministico():
    global automata_global
    try:
        if not automata_global:
            return jsonify({'error': "El autómata no está definido."}), 400

        automata_deterministico, _ = automata_global.convertir_a_deterministico()
        tabla_transiciones = generar_tabla_transiciones(automata_deterministico)
        graficar_automata(automata_deterministico, deterministic=True)
        png_filename = 'automata_graph_deterministico.png'
        png_path = f'/static/{png_filename}'

        return jsonify({
            'tabla': tabla_transiciones,
            'png_path': png_path, 
            'mensaje': "El autómata ha sido convertido a determinístico.",
            'deterministico': True
        })
    except Exception as e:
        print(f"Error en contertir_en_deterministico: {e}")
        return jsonify({'error': f"Error al convertir a determinístico: {e}"}), 500


@app.route('/eliminar_estados_error', methods=['POST'])
def eliminar_estados_error():
    global automata_global
    try:
        if not automata_global:
            return jsonify({'error': "El autómata no está definido."}), 400

        estados_eliminados = automata_global.eliminar_estados_de_error()
        if not estados_eliminados:
            return jsonify({'mensaje': "No se encontraron estados de error para eliminar."})

        # Generar la tabla de transiciones y el grafico actualizados
        tabla_transiciones = generar_tabla_transiciones(automata_global)
        graficar_automata(automata_global, deterministic=automata_global.es_deterministico())

        deterministico = automata_global.es_deterministico()
        png_filename = 'automata_graph_deterministico.png' if deterministico else 'automata_graph.png'
        png_path = f'/static/{png_filename}'

        # Devolver la respuesta con la tabla y el gráfico
        return jsonify({
            'tabla': tabla_transiciones,
            'png_path': png_path,  
            'mensaje': f"Se han eliminado los siguientes estados de error: {', '.join(estados_eliminados)}.",
            'deterministico': deterministico
        })

    except Exception as e:
        print(f"Error en eliminar_estados_error: {e}")
        return jsonify({'error': f"Error al eliminar estados de error: {e}"}), 500


def generar_tabla_transiciones(automata):
    tabla_html = "<table border='1'><tr><th>Estado</th>"
    for simbolo in automata.alfabeto:
        tabla_html += f"<th>{simbolo}</th>"
    tabla_html += "</tr>"

    for estado in automata.estados:
        estado_str = estado
        tabla_html += f"<tr><td>{estado_str}</td>"
        for simbolo in automata.alfabeto:
            destinos = automata.obtener_transiciones(estado, simbolo)
            if not destinos:
                destino_str = '-'  # Representa transiciones inexistentes
            elif isinstance(destinos, list):
                destino_str = ', '.join(destinos) if destinos else '-'
            else:
                destino_str = destinos if destinos else '-'
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

    # Añadir las transiciones
    for estado, transiciones_estado in automata.transiciones.items():
        estado_str = estado
        for simbolo, destinos in transiciones_estado.items():
            if not destinos:
                continue  # No añade transiciones inexistentes
            if isinstance(destinos, list):
                for d in destinos:
                    if d and d != "-":
                        dot.edge(estado_str, d, label=simbolo)
            elif isinstance(destinos, str) and destinos.strip():
                dot.edge(estado_str, destinos, label=simbolo)

    if not os.path.exists('static'):
        os.makedirs('static')

    output_file = 'automata_graph_deterministico' if deterministic else 'automata_graph'
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
        return jsonify({'resultado': resultado})
    except Exception as e:
        print(f"Error al validar la cadena: {e}")
        return jsonify({'error': f"Error al validar la cadena: {e}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
