function resetearFormulario() {
    document.getElementById("automataForm").reset();

    // Ocultar secciones de transiciones, resultados y validación
    document.getElementById("transiciones_container").style.display = "none";
    document.getElementById("resultados").innerHTML = "";
    document.getElementById("mensaje_deterministico").style.display = "none";
    document.getElementById("deterministic_button").style.display = "none";
    document.getElementById("eliminar_error_button").style.display = "none";
    document.getElementById("validacion_section").style.display = "none";
}

function generarTablaTransiciones() {
    document.getElementById("resultados").innerHTML = "";
    document.getElementById("mensaje_deterministico").style.display = "none";
    document.getElementById("deterministic_button").style.display = "none";
    document.getElementById("eliminar_error_button").style.display = "none";
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
        errores.push("El estado inicial debe ser único.");
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
            tablaHtml += `<td><input type='text' name='${estado},${simbolo}' placeholder='-'></td>`;
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

    document.querySelectorAll("table input").forEach(input => {
        const [estado, simbolo] = input.name.split(',');
        const valor = input.value.trim();

        if (!transiciones[estado]) {
            transiciones[estado] = {};
        }

        if (valor === '' || valor === '-') {
            transiciones[estado][simbolo] = []; // Representar transiciones inexistentes como listas vacías
        } else {
            // Mantener transiciones como lista si son múltiples, o como cadena si es única
            const destinos = valor.split(',').map(v => v.trim()).filter(v => v !== '');
            transiciones[estado][simbolo] = destinos.length > 1 ? destinos : destinos;
        }
    });

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
                    throw new Error(data.error || 'Error en la solicitud');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.tabla && data.png_path) {
                // Mostrar la tabla de transiciones y grafico
                document.getElementById("resultados").innerHTML = data.tabla;
                const grafico = document.createElement("img");
                grafico.src = data.png_path + '?' + new Date().getTime();  
                document.getElementById("resultados").appendChild(grafico);
            } else {
                console.error("Tabla o ruta del PNG no recibida.");
            }

            // Mostrar el mensaje de si es determinístico o no
            const esDeterministico = data.deterministico;
            document.getElementById("mensaje_deterministico").style.display = "block";
            document.getElementById("mensaje").innerText = esDeterministico
                ? "El autómata es determinístico."
                : "El autómata NO es determinístico.";

            // Mostrar/ocultar el botón de conversión
            document.getElementById("deterministic_button").style.display = esDeterministico ? "none" : "block";

            // Mostrar el botón para eliminar estados de error si no es determinístico
            if (!esDeterministico) {
                document.getElementById("eliminar_error_button").style.display = "block";
            } else {
                document.getElementById("eliminar_error_button").style.display = "none";
            }

            // Mostrar la sección de validación solo si es determinístico
            document.getElementById("validacion_section").style.display = esDeterministico ? "block" : "none";
        })
        .catch(error => {
            alert("Error: " + error.message);
        });
}

function convertirADeterministico() {
    fetch('/contertir_en_deterministico', {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error en la solicitud');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.tabla && data.png_path) {
                // Mostrar tabla y grafico
                document.getElementById("resultados").innerHTML = data.tabla;
                const grafico = document.createElement("img");
                grafico.src = data.png_path + '?' + new Date().getTime();  
                document.getElementById("resultados").appendChild(grafico);
            } else {
                console.error("Tabla o ruta del PNG no recibida.");
            }

            // Mostrar el mensaje de conversión
            document.getElementById("mensaje_deterministico").style.display = "block";
            document.getElementById("mensaje").innerText = data.mensaje;
            document.getElementById("deterministic_button").style.display = "none";
            document.getElementById("eliminar_error_button").style.display = "none";
            document.getElementById("validacion_section").style.display = "block";
        })
        .catch(error => {
            console.error("Error al convertir a determinístico:", error);
            alert("Error al convertir a determinístico: " + error.message);
        });
}

function eliminarEstadosError() {
    fetch('/eliminar_estados_error', {
        method: 'POST'
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error en la solicitud');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.tabla && data.png_path) {
                //Tabla de transiciones y grafico actualizados
                document.getElementById("resultados").innerHTML = data.tabla;
                const grafico = document.createElement("img");
                grafico.src = data.png_path + '?' + new Date().getTime();  
                document.getElementById("resultados").appendChild(grafico);
            }

            document.getElementById("mensaje_deterministico").style.display = "block";
            document.getElementById("mensaje").innerText = data.mensaje || "Estados de error eliminados correctamente.";

            document.getElementById("eliminar_error_button").style.display = "none";

            const esDeterministico = data.deterministico;
            document.getElementById("deterministic_button").style.display = esDeterministico ? "none" : "block";
            document.getElementById("validacion_section").style.display = esDeterministico ? "block" : "none";
        })
        .catch(error => {
            console.error("Error al eliminar estados de error:", error);
            alert("Error al eliminar estados de error: " + error.message);
        });
}

function validarCadena() {
    const cadena = document.getElementById("cadena").value.trim();

    fetch('/validar_cadena', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cadena: cadena })
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Error en la solicitud');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.resultado) {
                document.getElementById("validacion_resultado").innerText = data.resultado;
            } else {
                document.getElementById("validacion_resultado").innerText = "No se obtuvo respuesta de la validación.";
            }
        })
        .catch(error => {
            console.error("Error al validar la cadena:", error);
            document.getElementById("validacion_resultado").innerText = "Error al validar la cadena: " + error.message;
        });
}
