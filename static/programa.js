function resetearFormulario() {
    // Reiniciar el formulario
    document.getElementById("automataForm").reset();
    
    // Ocultar secciones de transiciones, resultados y validación
    document.getElementById("transiciones_container").style.display = "none";
    document.getElementById("resultados").innerHTML = "";
    document.getElementById("mensaje_deterministico").style.display = "none";
    document.getElementById("deterministic_button").style.display = "none";
    document.getElementById("validacion_section").style.display = "none";
}

function generarTablaTransiciones() {
    // Borrar resultados previos antes de generar nueva tabla
    document.getElementById("resultados").innerHTML = "";
    document.getElementById("mensaje_deterministico").style.display = "none";
    document.getElementById("deterministic_button").style.display = "none";
    document.getElementById("validacion_section").style.display = "none";
    
    const estados = document.getElementById("estados").value.split(',').map(e => e.trim());
    const alfabeto = document.getElementById("alfabeto").value.split(',').map(e => e.trim());
    const estado_inicial = document.getElementById("estado_inicial").value.trim();
    const estados_finales = document.getElementById("estados_finales").value.split(',').map(e => e.trim());

    let errores = [];

    // Validaciones (mismas que antes)
    const estados_unicos = new Set(estados);
    if (estados_unicos.size !== estados.length) {
        errores.push("No se permiten estados duplicados.");
    }

    const alfabeto_unico = new Set(alfabeto);
    if (alfabeto_unico.size !== alfabeto.length) {
        errores.push("No se permiten símbolos duplicados en el alfabeto.");
    }

    if (!estados_unicos.has(estado_inicial)) {
        errores.push("El estado inicial debe pertenecer a los estados ingresados.");
    }

    estados_finales.forEach(estado => {
        if (!estados_unicos.has(estado)) {
            errores.push(`El estado aceptador '${estado}' no pertenece a los estados ingresados.`);
        }
    });

    if (errores.length > 0) {
        alert("Errores:\n" + errores.join("\n"));
        return;
    }

    let tablaHtml = "<tr><th>Estado</th>";
    alfabeto.forEach(simbolo => {
        tablaHtml += `<th>Transición (${simbolo})</th>`;
    });
    tablaHtml += "</tr>";

    estados.forEach(estado => {
        tablaHtml += `<tr><td>${estado}</td>`;
        alfabeto.forEach(simbolo => {
            tablaHtml += `<td><input type='text' name='${estado},${simbolo}'></td>`;
        });
        tablaHtml += "</tr>";
    });

    document.getElementById("tablaTransiciones").innerHTML = tablaHtml;
    document.getElementById("transiciones_container").style.display = "block";
}

function enviarAutomata() {
    const form = document.getElementById("automataForm");
    const formData = new FormData(form);
    const estados = formData.get("estados").split(',').map(e => e.trim());
    const alfabeto = formData.get("alfabeto").split(',').map(e => e.trim());
    const estado_inicial = formData.get("estado_inicial").trim();
    const estados_finales = formData.get("estados_finales").split(',').map(e => e.trim());

    const transiciones = {};

    // Recoger las transiciones ingresadas en la tabla
    document.querySelectorAll("table input").forEach(input => {
        const [estado, simbolo] = input.name.split(',');
        const valor = input.value.trim();

        if (!transiciones[estado]) {
            transiciones[estado] = {};
        }
        transiciones[estado][simbolo] = valor.split(',').map(v => v.trim());
    });

    // Enviar los datos al backend
    fetch('/submit_automata', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            estados: estados,
            alfabeto: alfabeto,
            estado_inicial: estado_inicial,
            estados_finales: estados_finales,
            transiciones: transiciones
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error);
            });
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("resultados").innerHTML = data.tabla;

        // Mostrar el gráfico del autómata
        const grafico = document.createElement("img");
        grafico.src = '/static/automata_graph.png?' + new Date().getTime(); // Forzar la recarga del gráfico
        document.getElementById("resultados").appendChild(grafico);

        // Mostrar si es determinístico o no
        const esDeterministico = data.deterministico;
        document.getElementById("mensaje_deterministico").style.display = "block";
        document.getElementById("mensaje").innerText = esDeterministico 
            ? "El autómata es determinístico." 
            : "El autómata NO es determinístico.";

        // Mostrar u ocultar el botón de conversión y la sección de validación según si es determinístico o no
        document.getElementById("deterministic_button").style.display = esDeterministico ? "none" : "block";
        document.getElementById("validacion_section").style.display = esDeterministico ? "block" : "none";
    })
    .catch(error => {
        alert("Error: " + error.message);
    });
}

function convertirADeterministico() {
    fetch('/convert_to_deterministic', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("resultados").innerHTML = data.tabla;

        // Actualizar el gráfico para el autómata determinístico
        const grafico = document.createElement("img");
        grafico.src = '/static/automata_graph.png?' + new Date().getTime(); 
        document.getElementById("resultados").appendChild(grafico);

        // Ocultar el botón de conversión y el mensaje de determinismo
        document.getElementById("mensaje_deterministico").style.display = "none";
        document.getElementById("deterministic_button").style.display = "none";

        // Mostrar la opción para validar cadena ahora que es determinístico
        document.getElementById("validacion_section").style.display = "block";
    })
    .catch(error => {
        alert("Error al convertir a determinístico: " + error.message);
    });
}

function validarCadena() {
    const cadena = document.getElementById("cadena").value.trim();
    // Enviar la cadena al backend
    fetch('/validar_cadena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cadena: cadena })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("validacion_resultado").innerHTML = data.resultado;
    })
    .catch(error => {
        console.error("Error al validar la cadena:", error);
        alert("Ocurrió un error al validar la cadena.");
    });
}
