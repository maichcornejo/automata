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
        # Recibir los datos enviados desde el frontend
        data = request.get_json()

        estados = data['estados']
        alfabeto = data['alfabeto']
        transiciones = data['transiciones']
        estado_inicial = data['estado_inicial']
        estados_finales = data['estados_finales']

        errores = []

        # Validación: Verificar que todos los destinos de las transiciones existan, si no son nulos o vacíos
        for estado, transiciones_estado in transiciones.items():
            for simbolo, destino in transiciones_estado.items():
                if isinstance(destino, list):
                    for d in destino:
                        if d and d not in estados:  # Verificar que no sea nulo o vacío, y que exista
                            errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{d}'.")
                else:
                    if destino and destino not in estados:  # Verificar que no sea nulo o vacío, y que exista
                        errores.append(f"La transición desde el estado '{estado}' con el símbolo '{simbolo}' apunta a un estado inexistente: '{destino}'.")

        # Si hay errores, devolverlos
        if errores:
            return jsonify({'error': "\n".join(errores)}), 400

        # Crear una instancia de Automata (no determinístico)
        automata_global = Automata(estados, alfabeto, transiciones, estado_inicial, estados_finales)

        # Verificar si es determinístico
        deterministico = automata_global.es_deterministico()

        # Generar la tabla de transiciones
        tabla_transiciones = generar_tabla_transiciones(automata_global)

        # Graficar el autómata no determinístico
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

    # Convertir el autómata a determinístico
    automata_deterministico = automata_global.convertir_a_deterministico()

    # Generar la tabla de transiciones determinística
    tabla_transiciones = generar_tabla_transiciones(automata_deterministico)

    # Graficar el autómata determinístico
    graficar_automata(automata_deterministico, deterministic=True)

    # Devolver la tabla de transiciones y los gráficos (no determinístico y determinístico)
    return f"""
    <h3>Tabla de Transiciones Final (Determinístico)</h3>
    {tabla_transiciones}
    <div style="display: flex; justify-content: center; align-items: center; gap: 20px;">
        <div>
            <h3>Autómata No Determinístico</h3>
            <img src='/static/automata_graph.png' alt='Gráfico del autómata no determinístico'>
        </div>
        <div>
            <h3>Autómata Determinístico</h3>
            <img src='/static/automata_graph_deterministic.png' alt='Gráfico del autómata determinístico'>
        </div>
    </div>
    """

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

    # Añadir las transiciones
    for estado, transiciones_estado in automata.transiciones.items():
        estado_str = estado
        for simbolo, destino in transiciones_estado.items():
            if destino and destino != "-" and destino != "":
                destino_str = ','.join(destino) if isinstance(destino, list) else destino
                dot.edge(estado_str, destino_str, label=simbolo)

    # Guardar el gráfico como PNG
    output_file = 'automata_graph_deterministic' if deterministic else 'automata_graph'
    dot.render(f'static/{output_file}', format='png', cleanup=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
