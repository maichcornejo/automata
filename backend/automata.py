class Automata:
    def __init__(self, estados, alfabeto, transiciones, estado_inicial, estados_finales):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transiciones = transiciones
        self.estado_inicial = estado_inicial
        self.estados_finales = estados_finales

    def es_deterministico(self):
        """
        Verifica si el autómata es determinístico.
        Un autómata es determinístico si, para cada estado y símbolo del alfabeto, existe una y solo una transición definida.
        """
        for estado, transiciones_estado in self.transiciones.items():
            for simbolo, destinos in transiciones_estado.items():
                if isinstance(destinos, list) and len(destinos) > 1:
                    return False
        return True

    def obtener_transiciones(self, estado, simbolo):
        """
        Devuelve las transiciones para un estado dado y un símbolo.
        Si no existen transiciones, devuelve None.
        """
        if estado in self.transiciones and simbolo in self.transiciones[estado]:
            return self.transiciones[estado][simbolo]
        return None

    def convertir_a_deterministico(self):
        """
        Convierte el autómata no determinístico a uno determinístico utilizando el algoritmo de subconjuntos.
        Evita la creación de estados adicionales si no hay transiciones válidas.
        Asigna nuevos nombres a los estados determinísticos continuando desde los originales.
        """
        nuevos_estados = []
        nuevas_transiciones = {}
        nuevos_estados_finales = set()
        
        # Mapa para los nombres de los nuevos estados determinísticos
        estado_nombre_map = {frozenset([estado]): estado for estado in self.estados}
        nombre_actual = 1  # Empezar con una numeración para los nuevos estados, independientemente de los nombres originales

        # El nuevo estado inicial es el conjunto del estado inicial
        conjunto_inicial = frozenset([self.estado_inicial])
        if conjunto_inicial not in estado_nombre_map:
            estado_nombre_map[conjunto_inicial] = f"Q{nombre_actual}"  # Generar nuevos nombres como 'Q1', 'Q2', etc.
            nombre_actual += 1
        nuevos_estados.append(conjunto_inicial)
        nuevas_transiciones[conjunto_inicial] = {}

        # Conjunto de estados no procesados
        por_procesar = [conjunto_inicial]

        while por_procesar:
            estado_actual = por_procesar.pop()
            nuevas_transiciones[estado_actual] = {}

            for simbolo in self.alfabeto:
                nuevos_destinos = set()

                for estado in estado_actual:
                    if simbolo in self.transiciones.get(estado, {}):
                        destinos = self.transiciones[estado][simbolo]
                        if isinstance(destinos, list):
                            nuevos_destinos.update(destinos)
                        else:
                            nuevos_destinos.add(destinos)

                # Solo agregar el nuevo estado si existen destinos válidos
                if nuevos_destinos:
                    nuevo_estado = frozenset(nuevos_destinos)
                    if nuevo_estado not in estado_nombre_map:
                        estado_nombre_map[nuevo_estado] = f"Q{nombre_actual}"  # Generar nuevo nombre de estado
                        nombre_actual += 1

                    nuevas_transiciones[estado_actual][simbolo] = nuevo_estado

                    if nuevo_estado not in nuevos_estados:
                        nuevos_estados.append(nuevo_estado)
                        por_procesar.append(nuevo_estado)

                    # Verificar si el nuevo estado contiene un estado final
                    if nuevo_estado.intersection(set(self.estados_finales)):
                        nuevos_estados_finales.add(nuevo_estado)

        # Renombrar transiciones, evitando agregar estados vacíos
        nuevas_transiciones_renombradas = {}
        for estado, trans in nuevas_transiciones.items():
            estado_nuevo = estado_nombre_map[estado]
            nuevas_transiciones_renombradas[estado_nuevo] = {}
            for simbolo in self.alfabeto:
                destino = trans.get(simbolo)
                if destino:
                    nuevas_transiciones_renombradas[estado_nuevo][simbolo] = estado_nombre_map[destino]

        nuevos_estados_renombrados = list(nuevas_transiciones_renombradas.keys())
        nuevos_estados_finales_renombrados = [estado_nombre_map[estado] for estado in nuevos_estados_finales]

        # Devolver el nuevo autómata determinístico con estados renombrados
        return Automata(
            estados=nuevos_estados_renombrados,
            alfabeto=self.alfabeto,
            transiciones=nuevas_transiciones_renombradas,
            estado_inicial=estado_nombre_map[conjunto_inicial],
            estados_finales=nuevos_estados_finales_renombrados
        )
