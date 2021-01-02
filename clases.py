from random import randint
import threading
import numpy

DIMENSION_MATRIZ = 4


class VehiculoException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


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
        direccion_columna = self.cliente.destino[1] - self.posicion[1]
        direccion_fila = self.cliente.destino[0] - self.posicion[0]

        if (abs(direccion_fila) == 1 or abs(direccion_fila) == 0) and (
                abs(direccion_columna) == 1 or abs(direccion_columna) == 0):
            if entorno.matriz[self.cliente.destino[0]][self.cliente.destino[1]].vehiculo is None:
                pos_resultado = self.cliente.destino
                self.cliente.pasajero = False
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
