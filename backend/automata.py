class Automata:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales

    def es_deterministico(self):
        for estado, transiciones_estado in self.transiciones.items():
            for simbolo, destinos in transiciones_estado.items():
                if isinstance(destinos, list) and len(destinos) > 1:
                    return False
        return True

    def obtener_transiciones(self, estado, simbolo):
        if estado in self.transiciones and simbolo in self.transiciones[estado]:
            return self.transiciones[estado][simbolo]
        return None  # Claramente devuelve None cuando no hay transición

    def validar_cadena(self, cadena):
        if self.es_deterministico():
            return self._validar_cadena_deterministico(cadena)
        else:
            return self._validar_cadena_no_deterministico(cadena)

    def _validar_cadena_deterministico(self, cadena):
        estado_actual = self.estado_inicial
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False
            transicion = self.obtener_transiciones(estado_actual, simbolo)
            if not isinstance(transicion, str):  # Asegurar que sea una transición válida
                return False
            estado_actual = transicion
        return estado_actual in self.estados_finales

    def _validar_cadena_no_deterministico(self, cadena):
        def validar_recursivo(estado, cadena_restante):
            if not cadena_restante:
                return estado in self.estados_finales

            simbolo = cadena_restante[0]
            if simbolo not in self.alfabeto:
                return False

            transiciones = self.obtener_transiciones(estado, simbolo)
            if transiciones is None:
                return False

            if not isinstance(transiciones, list):
                transiciones = [transiciones]

            return any(validar_recursivo(siguiente_estado, cadena_restante[1:])
                       for siguiente_estado in transiciones)

        return validar_recursivo(self.estado_inicial, cadena)

    def convertir_a_deterministico(self):
        nuevos_estados = []  # Lista de conjuntos de estados (en determinístico)
        nuevas_transiciones = {}  # Transiciones del nuevo automata determinístico
        nuevos_estados_finales = set()  # Conjunto de estados finales
        estado_nombre_map = {}  # Mapeo de nombres de los nuevos estados
        nombre_actual = len(self.estados)  # Empezar la numeración desde el último estado original

        def obtener_nombre_estado(conjunto):
            conjunto_ordenado = frozenset(sorted(conjunto))
            if conjunto_ordenado not in estado_nombre_map:
                nonlocal nombre_actual
                nombre_actual += 1
                estado_nombre_map[conjunto_ordenado] = f"Q{nombre_actual}"
            return estado_nombre_map[conjunto_ordenado]

        # Estado inicial es el conjunto del estado inicial original
        conjunto_inicial = frozenset([self.estado_inicial])
        obtener_nombre_estado(conjunto_inicial)
        nuevos_estados.append(conjunto_inicial)

        # Procesar el conjunto inicial
        por_procesar = [conjunto_inicial]

        while por_procesar:
            estado_actual = por_procesar.pop(0)  # Procesar el primer estado en la lista
            nombre_estado_actual = obtener_nombre_estado(estado_actual)
            nuevas_transiciones[nombre_estado_actual] = {}

            for simbolo in self.alfabeto:
                nuevos_destinos = set()

                # Combinar las transiciones de todos los estados del conjunto actual
                for estado in estado_actual:
                    if simbolo in self.transiciones.get(estado, {}):
                        destinos = self.transiciones[estado][simbolo]
                        if isinstance(destinos, list):
                            nuevos_destinos.update(destinos)
                        else:
                            nuevos_destinos.add(destinos)

                if nuevos_destinos:
                    nuevo_estado = frozenset(nuevos_destinos)
                    nombre_nuevo_estado = obtener_nombre_estado(nuevo_estado)

                    # Asignar la transición al nuevo estado
                    nuevas_transiciones[nombre_estado_actual][simbolo] = nombre_nuevo_estado

                    if nuevo_estado not in nuevos_estados:
                        nuevos_estados.append(nuevo_estado)
                        por_procesar.append(nuevo_estado)

                    # Si el conjunto de nuevos estados contiene algún estado final, marcarlo como final
                    if nuevo_estado.intersection(self.estados_finales):
                        nuevos_estados_finales.add(nombre_nuevo_estado)

        # Obtener la lista de estados renombrados
        nuevos_estados_renombrados = list(estado_nombre_map.values())

        return Automata(
            estados=nuevos_estados_renombrados,
            alfabeto=self.alfabeto,
            transiciones=nuevas_transiciones,
            estado_inicial=obtener_nombre_estado(conjunto_inicial),
            estados_finales=list(nuevos_estados_finales)
        )
