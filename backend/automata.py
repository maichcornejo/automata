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
        return None

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
            if not isinstance(transicion, str):
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
        nuevos_estados = []
        nuevas_transiciones = {}
        nuevos_estados_finales = set()
        estado_componentes = {}

        conjunto_inicial = frozenset([self.estado_inicial])
        nuevos_estados.append(conjunto_inicial)
        por_procesar = [conjunto_inicial]

        while por_procesar:
            estado_actual = por_procesar.pop(0)
            estado_actual_str = '{' + ','.join(sorted(estado_actual)) + '}'  
            nuevas_transiciones[estado_actual_str] = {}

            for simbolo in self.alfabeto:
                nuevos_destinos = set()

                for estado in estado_actual:
                    if simbolo in self.transiciones.get(estado, {}):
                        destinos = self.transiciones[estado][simbolo]
                        if isinstance(destinos, list):
                            nuevos_destinos.update(destinos)
                        else:
                            nuevos_destinos.add(destinos)

                if nuevos_destinos:
                    nuevo_estado = frozenset(nuevos_destinos)
                    nuevo_estado_str = '{' + ','.join(sorted(nuevo_estado)) + '}'  # Mostrar conjunto de estados

                    nuevas_transiciones[estado_actual_str][simbolo] = nuevo_estado_str

                    if nuevo_estado not in nuevos_estados:
                        nuevos_estados.append(nuevo_estado)
                        por_procesar.append(nuevo_estado)

                    if nuevo_estado.intersection(self.estados_finales):
                        nuevos_estados_finales.add(nuevo_estado_str)

        nuevos_estados_str = ['{' + ','.join(sorted(estado)) + '}' for estado in nuevos_estados]
        estado_inicial_str = '{' + self.estado_inicial + '}'

        return Automata(
            estados=nuevos_estados_str,
            alfabeto=self.alfabeto,
            transiciones=nuevas_transiciones,
            estado_inicial=estado_inicial_str,
            estados_finales=list(nuevos_estados_finales)
        ), {estado: list(componentes) for estado, componentes in zip(nuevos_estados_str, nuevos_estados)}
