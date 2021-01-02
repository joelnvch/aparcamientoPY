import numpy

from clases import *


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
            if pos_antigua:
                self.matriz[pos_antigua[0]][pos_antigua[1]].clientes.remove(elemento)

            if casilla_dest.vehiculo is None:
                casilla_dest.clientes.append(elemento)
                elemento.posicion = pos_nueva
            # si entra en vehiculo
            else:
                vehiculo = casilla_dest.vehiculo
                elemento.posicion = pos_nueva

                if elemento.destino == pos_nueva:
                    casilla_dest.clientes.append(elemento)
                    return [""]
                elif isinstance(vehiculo, Taxi):
                    if vehiculo.cliente is None:
                        elemento.pasajero = True
                        vehiculo.cliente = elemento
                        return ["taxi", vehiculo.id, vehiculo.posicion, vehiculo.get_cliente()]
                    else:
                        casilla_dest.clientes.append(elemento)
                elif isinstance(vehiculo, Autobus):
                    if vehiculo.parado:
                        vehiculo.clientes.append(elemento)
                        elemento.pasajero = True
                        return ["autobus", vehiculo.id, vehiculo.posicion, vehiculo.parado]
                    else:
                        casilla_dest.clientes.append(elemento)

        # si es un vehiculo
        else:
            if casilla_dest.vehiculo == elemento:
                return [""]
            elif casilla_dest.vehiculo is not None:
                raise VehiculoException("Un vehiculo ha intentado entrar en una casilla con otro")

            if pos_antigua:
                self.matriz[pos_antigua[0]][pos_antigua[1]].vehiculo = None

            if casilla_dest.vehiculo is None:
                casilla_dest.vehiculo = elemento
                elemento.posicion = pos_nueva
                if isinstance(elemento, Autobus):
                    for cliente in elemento.clientes:
                        cliente.posicion = pos_nueva
                elif isinstance(elemento, Taxi):
                    if elemento.cliente is not None:
                        elemento.cliente.posicion = pos_nueva
                        if elemento.cliente.posicion == elemento.cliente.destino:
                            id_cl = elemento.cliente.id
                            self.matriz[elemento.cliente.destino[0]][elemento.cliente.destino[1]].clientes.append(
                                elemento.cliente)
                            elemento.cliente = None
                            return ["paradaTaxi", id_cl]
        return [""]

    def __casillas_contiguas(self, pos):
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
        casilla_actual.estado.acquire()  # no empezamos hasta que su posición no este bloqueada
        posiciones_bloqueadas.append(casilla_actual.id)
        for casilla in self.__casillas_contiguas(pos):
            if not casilla.estado.locked():
                casilla.estado.acquire()
                posiciones_bloqueadas.append(casilla.id)
        return posiciones_bloqueadas

    def unlock_casillas(self, lista_pos):
        for pos in lista_pos:
            self.matriz[pos[0]][pos[1]].estado.release()

    def casillas_sin_vehiculos(self, lista_pos):
        res = []
        for pos in lista_pos:
            if self.matriz[pos[0]][pos[1]].vehiculo is None:
                res.append(pos)
        res.append(lista_pos[0])  # el resultado que nos llegue tendrá en la pos[0] a si mismo
        return res
