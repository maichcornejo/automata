function generarTablaTransiciones() {
    const estados = document.getElementById("estados").value.split(',').map(e => e.trim());
    const alfabeto = document.getElementById("alfabeto").value.split(',').map(e => e.trim());
    const estado_inicial = document.getElementById("estado_inicial").value.trim();
    const estados_finales = document.getElementById("estados_finales").value.split(',').map(e => e.trim());

    let errores = [];

    // Validación: No permitir estados duplicados
    const estados_unicos = new Set(estados);
    if (estados_unicos.size !== estados.length) {
        errores.push("No se permiten estados duplicados.");
    }

    // Validación: No permitir símbolos duplicados en el alfabeto
    const alfabeto_unico = new Set(alfabeto);
    if (alfabeto_unico.size !== alfabeto.length) {
        errores.push("No se permiten símbolos duplicados en el alfabeto.");
    }

    // Validación: Estado inicial debe pertenecer a los estados ingresados
    if (!estados_unicos.has(estado_inicial)) {
        errores.push("El estado inicial debe pertenecer a los estados ingresados.");
    }

    // Validación: Estados aceptadores deben pertenecer a los estados ingresados
    estados_finales.forEach(estado => {
        if (!estados_unicos.has(estado)) {
            errores.push(`El estado aceptador '${estado}' no pertenece a los estados ingresados.`);
        }
    });

    // Si hay errores, mostrar el mensaje de error y no generar la tabla de transiciones
    if (errores.length > 0) {
        alert("Errores:\n" + errores.join("\n"));
        return; // Detener aquí si hay errores
    }

    // Si no hay errores, generar la tabla de transiciones
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

    // Enviar los datos al backend si no hay errores
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
    .then(response => response.json())
    .then(data => {
        document.getElementById("resultados").innerHTML = data.tabla;
        document.getElementById("mensaje_deterministico").style.display = "block";
        document.getElementById("mensaje").innerText = data.mensaje;

        // Mostrar el gráfico del autómata no determinístico
        const grafico = document.createElement("img");
        grafico.src = '/static/automata_graph.png?' + new Date().getTime(); // Forzar la recarga del gráfico
        document.getElementById("resultados").appendChild(grafico);

        if (!data.deterministico) {
            document.getElementById("deterministic_button").style.display = "block";  // Mostrar el botón para convertir
        } else {
            document.getElementById("deterministic_button").style.display = "none";   // Ocultar el botón si es determinístico
        }
    })
    .catch(error => {
        console.error("Error al procesar el JSON:", error);
        alert("Ocurrió un error al procesar la respuesta del servidor.");
    });
}

function convertirADeterministico() {
    fetch('/convert_to_deterministic', {
        method: 'POST'
    })
    .then(response => response.text())
    .then(data => {
        document.getElementById("resultados").innerHTML = data;
        
        // Ocultar el mensaje y el botón después de la conversión
        document.getElementById("mensaje_deterministico").style.display = "none";
        document.getElementById("deterministic_button").style.display = "none";
    })
    .catch(error => {
        console.error("Error al convertir a determinístico:", error);
        alert("Ocurrió un error al convertir el autómata a determinístico.");
    });
}
