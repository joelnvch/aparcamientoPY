from random import randint
import threading
import numpy

DIMENSION_MATRIZ = 4


class Cliente:
    def __init__(self, id):
        self.id = id
        self.destino = [randint(0, DIMENSION_MATRIZ - 1), randint(0, DIMENSION_MATRIZ - 1)]
        self.posicion = []
        self.pasajero = False


class Taxi:
    def __init__(self, id):
        self.id = id
        self.cliente = None
        self.posicion = []

    def decidir_mov(self, lista_pos, entorno):
        if self.cliente is None:
            raise Exception("Taxi error no deberia estar aqui")
        direccion_columna = self.cliente.destino[1] - self.posicion[1]
        direccion_fila = self.cliente.destino[0] - self.posicion[0]
        pos_resultado = []

        if (abs(direccion_fila) == 1 or abs(direccion_fila) == 0) and (
                abs(direccion_columna) == 1 or abs(direccion_columna) == 0):
            # aqui devolvemos la posicion destino siempre que este en el rango pero
            # puede ser que aunque este en el rango justo nos coincida que
            # esta ocupado justo en ese momento por otro vehiculo
            # -arreglar error vahiculoerror
            if entorno.matriz[self.cliente.destino[0]][self.cliente.destino[1]].vehiculo is None:
                pos_resultado = self.cliente.destino
            else:
                pos_resultado = self.posicion

        else:
            pos_resultado = lista_pos[0]
            dist_columna = self.cliente.destino[0] - pos_resultado[0]
            dist_fila = self.cliente.destino[1] - pos_resultado[1]
            dist_destino = numpy.linalg.norm([dist_fila, dist_columna])

            for posicion in lista_pos:
                dist_columna = self.cliente.destino[0] - posicion[0]
                dist_fila = self.cliente.destino[1] - posicion[1]
                dist_destino_aux = numpy.linalg.norm([dist_fila, dist_columna])
                if dist_destino_aux < dist_destino:
                    pos_resultado = posicion
                    dist_destino = dist_destino_aux

        if pos_resultado == self.cliente.destino:
            self.cliente.pasajero = False

        if not pos_resultado:
            raise Exception('decidir mov error.')

        return pos_resultado


class Autobus:
    def __init__(self, id):
        self.id = id
        self.clientes = []
        self.posicion = []
        self.parado = False

    def realizar_parada(self, entorno):
        lista_clientes_fuera = []
        for cliente in self.clientes:
            rand = randint(0, 2)
            # hacemos que sea menos probable que se baje un cliente
            if rand == 0:
                self.clientes.remove(cliente)
                cliente.pasajero = False
                entorno.matriz[cliente.posicion[0]][cliente.posicion[1]].clientes.append(cliente)
                lista_clientes_fuera.append(cliente)
        return lista_clientes_fuera

    def obtener_clientes(self):
        res = []
        for cliente in self.clientes:
            res.append(cliente.id)
        return res


class Casilla:
    def __init__(self, id):
        self.id = id
        self.estado = threading.Lock()
        self.vehiculo = None
        self.clientes = []


class Entorno:
    def __init__(self):
        self.matriz = numpy.full((DIMENSION_MATRIZ, DIMENSION_MATRIZ), None)
        for i in range(0, DIMENSION_MATRIZ):
            for j in range(0, DIMENSION_MATRIZ):
                self.matriz[i][j] = Casilla([i, j])

    def insertar_elemento(self, elemento, pos_nueva):
        casilla_dest = self.matriz[pos_nueva[0]][pos_nueva[1]]
        pos_antigua = elemento.posicion

        if pos_nueva == pos_antigua:
            pass
        elif isinstance(elemento, Cliente):
            # borramos el valor antiguo de la casilla que hemos dejado

            # WARNING: probablemente no necesario acaba_salir_autobus
            if pos_antigua:
                self.matriz[pos_antigua[0]][pos_antigua[1]].clientes.remove(elemento)

            if casilla_dest.vehiculo is None:
                casilla_dest.clientes.append(elemento)
                elemento.posicion = pos_nueva
            # si entra en vehiculo
            else:
                # no estoy contemplando que el vehiculo encontrado si es un taxi tengo alguien dentro
                # -arreglado falta pruebas
                vehiculo = casilla_dest.vehiculo
                elemento.posicion = pos_nueva

                # nuevo: contemplar que si cae en destino se queda en destino haya o no un coche
                if elemento.destino == pos_nueva:
                    casilla_dest.clientes.append(elemento)

                # error#2: hay un caso en el que entra por aqui pero no entra en los ifs
                # solo se hacen las tres lineas de atras
                # - arreglado falta pruebas ----
                elif isinstance(vehiculo, Taxi):
                    if vehiculo.cliente is None:
                        elemento.pasajero = True
                        vehiculo.cliente = elemento
                        return ["taxi", vehiculo.id]
                    else:  # si el taxi tiene un cliente
                        # ponerlo en la casilla
                        casilla_dest.clientes.append(elemento)

                elif isinstance(vehiculo, Autobus):
                    if vehiculo.parado:
                        vehiculo.clientes.append(elemento)
                        elemento.pasajero = True
                        return ["autobus", vehiculo.id]
                    else:
                        casilla_dest.clientes.append(elemento)

        # si es un vehiculo
        else:
            # tal y como esta diseñado si el valor es un vehiculo es porque es él mismo por lo tanto no hacemos nada
            if casilla_dest.vehiculo == elemento:
                return [""]
            # si el destino no es el mismo y hay un vehiculo dentro da error
            # esta planteado de forma que a este metodo solo le puedan llegar valores validos
            elif casilla_dest.vehiculo is not None:
                raise Exception("Vehiculo error en pos ", pos_nueva, "id del vehiculo ", elemento.id)

            # borramos el valor antiguo de la casilla que hemos dejado
            if pos_antigua:
                self.matriz[pos_antigua[0]][pos_antigua[1]].vehiculo = None

            if casilla_dest.vehiculo is None:
                # movemos vehiculo
                casilla_dest.vehiculo = elemento
                elemento.posicion = pos_nueva
                if isinstance(elemento, Autobus):
                    for cliente in elemento.clientes:
                        cliente.posicion = pos_nueva
                elif isinstance(elemento, Taxi):
                    if elemento.cliente is not None:
                        elemento.cliente.posicion = pos_nueva
                        if elemento.cliente.posicion == elemento.cliente.destino:
                            # el equivalente a salir del coche y dejarle en la casilla
                            id_cl = elemento.cliente.id
                            self.matriz[elemento.cliente.destino[0]][elemento.cliente.destino[1]].clientes.append(
                                elemento.cliente)
                            elemento.cliente = None
                            return ["paradaTaxi", id_cl]

        return [""]

    # priv
    def casillas_contiguas(self, pos):
        res = []
        for i in range(pos[0] - 1, pos[0] + 2):
            if 0 <= i <= DIMENSION_MATRIZ - 1:
                for j in range(pos[1] - 1, pos[1] + 2):
                    if 0 <= j <= DIMENSION_MATRIZ - 1:
                        res.append(self.matriz[i][j])
        # la posicion actual la tenemos en el argumento pos, el resto de posiciones en res
        res.remove(self.matriz[pos[0]][pos[1]])
        return res

    def lock_alrededor(self, pos):
        casilla_actual = self.matriz[pos[0]][pos[1]]
        posiciones_bloqueadas = []
        # no comienza hasta que no puede bloquear su posicion actual
        while casilla_actual.estado.locked():
            pass
        casilla_actual.estado.acquire()
        posiciones_bloqueadas.append(casilla_actual.id)

        for casilla in self.casillas_contiguas(pos):
            if not casilla.estado.locked():
                casilla.estado.acquire()
                posiciones_bloqueadas.append(casilla.id)
        # el primer elemento de esta lista será siempre la casilla actual
        return posiciones_bloqueadas

    def unlock_casillas(self, lista_pos):
        for pos in lista_pos:
            self.matriz[pos[0]][pos[1]].estado.release()

    def casillas_sin_vehiculos(self, lista_pos, boole=True):
        res = []
        for pos in lista_pos:
            if self.matriz[pos[0]][pos[1]].vehiculo is None:
                res.append(pos)
        # el primer elemento en la lista es la posicion actual y por lo tanto es una pos valida
        # este metodo solo lo llaman los vehiculos asi que no ocasionaría ninguna repeticion lo siguiente
        if boole:
            # es false en caso de que la lista introducida no provenga de lock_alrededor
            res.append(lista_pos[0])
        return res
