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

    def convertir_a_deterministico(self):
        nuevos_estados = []
        nuevas_transiciones = {}
        nuevos_estados_finales = set()
        
        estado_nombre_map = {frozenset([estado]): estado for estado in self.estados}
        nombre_actual = 1

        conjunto_inicial = frozenset([self.estado_inicial])
        if conjunto_inicial not in estado_nombre_map:
            estado_nombre_map[conjunto_inicial] = f"Q{nombre_actual}"
            nombre_actual += 1
        nuevos_estados.append(conjunto_inicial)
        nuevas_transiciones[conjunto_inicial] = {}

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

                if nuevos_destinos:
                    nuevo_estado = frozenset(nuevos_destinos)
                    if nuevo_estado not in estado_nombre_map:
                        estado_nombre_map[nuevo_estado] = f"Q{nombre_actual}"
                        nombre_actual += 1

                    nuevas_transiciones[estado_actual][simbolo] = nuevo_estado

                    if nuevo_estado not in nuevos_estados:
                        nuevos_estados.append(nuevo_estado)
                        por_procesar.append(nuevo_estado)

                    if nuevo_estado.intersection(set(self.estados_finales)):
                        nuevos_estados_finales.add(nuevo_estado)

        # Eliminar estados de error y bucles de error compuestos
        estados_a_eliminar = set()
        for estado in nuevos_estados:
            if estado not in nuevos_estados_finales:
                transiciones = nuevas_transiciones.get(estado, {})
                if all(destino == estado for destino in transiciones.values()):
                    estados_a_eliminar.add(estado)
                elif all(destino in estados_a_eliminar or destino == estado for destino in transiciones.values()):
                    estados_a_eliminar.add(estado)

        # Eliminar estados sin transiciones salientes
        for estado in nuevos_estados:
            if not nuevas_transiciones.get(estado, {}):
                estados_a_eliminar.add(estado)

        # Eliminar los estados marcados
        for estado in estados_a_eliminar:
            if estado in nuevos_estados:
                nuevos_estados.remove(estado)
            if estado in nuevas_transiciones:
                nuevas_transiciones.pop(estado)
            for _, transiciones in nuevas_transiciones.items():
                for simbolo in list(transiciones.keys()):
                    if transiciones[simbolo] == estado:
                        transiciones.pop(simbolo)

        # Renombrar transiciones
        nuevas_transiciones_renombradas = {}
        for estado, trans in nuevas_transiciones.items():
            estado_nuevo = estado_nombre_map[estado]
            nuevas_transiciones_renombradas[estado_nuevo] = {}
            for simbolo, destino in trans.items():
                nuevas_transiciones_renombradas[estado_nuevo][simbolo] = estado_nombre_map[destino]

        nuevos_estados_renombrados = list(nuevas_transiciones_renombradas.keys())
        nuevos_estados_finales_renombrados = [estado_nombre_map[estado] for estado in nuevos_estados_finales if estado not in estados_a_eliminar]

        return Automata(
            estados=nuevos_estados_renombrados,
            alfabeto=self.alfabeto,
            transiciones=nuevas_transiciones_renombradas,
            estado_inicial=estado_nombre_map[conjunto_inicial],
            estados_finales=nuevos_estados_finales_renombrados
        )
    
    def validar_cadena(self, cadena):
        if not self.es_deterministico():
            automata_deterministico = self.convertir_a_deterministico()
            return automata_deterministico.validar_cadena(cadena)

        estado_actual = self.estado_inicial
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False  
            
            siguiente_estado = self.obtener_transiciones(estado_actual, simbolo)
            if siguiente_estado is None:
                return False   
            
            estado_actual = siguiente_estado

        return estado_actual in self.estados_finales