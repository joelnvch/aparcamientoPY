import os
from random import randint
from time import sleep

import numpy


class Taxi:
    def __init__(self, id):
        self.id = id
        self.cliente = None
        self.posicion = []

    def get_cliente(self):
        if self.cliente is None:
            return "-"
        else:
            return self.cliente.id

    def decidir_mov(self, lista_pos, juego):
        direccion_columna = self.cliente.destino[1] - self.posicion[1]
        direccion_fila = self.cliente.destino[0] - self.posicion[0]

        if (abs(direccion_fila) == 1 or abs(direccion_fila) == 0) and (
                abs(direccion_columna) == 1 or abs(direccion_columna) == 0):
            if juego.matriz[self.cliente.destino[0]][self.cliente.destino[1]].vehiculo is None:
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

    def ciclo_taxi(self, juego):
        primera_iteracion = True
        n_clientes_transportados = 0

        while not juego.elemento_ganador:
            if n_clientes_transportados == juego.N_TAXI_GANA:
                juego.elemento_ganador = "TAXI"
                break

            # Ponerlo en la matriz
            if primera_iteracion:
                primera_iteracion = False
                pos_posibles = [[randint(0, juego.DIMENSION_MATRIZ - 1), randint(0, juego.DIMENSION_MATRIZ - 1)],
                                [randint(0, juego.DIMENSION_MATRIZ - 1), randint(0, juego.DIMENSION_MATRIZ - 1)],
                                [randint(0, juego.DIMENSION_MATRIZ - 1), randint(0, juego.DIMENSION_MATRIZ - 1)]]
                pos_disp = []
                while not pos_disp:
                    pos_bloqueadas = juego.lock_posiciones(pos_posibles)
                    pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas, False)
                    if len(pos_disp) == 0:
                        juego.unlock_casillas(pos_bloqueadas)
                        sleep(0.2)
                    else:
                        if len(pos_disp) == 1:
                            juego.insertar_elemento(self, pos_disp[0])
                        else:
                            juego.insertar_elemento(self, pos_disp[randint(0, len(pos_disp) - 1)])
                        juego.imprimir(["Colocacion Taxi: ID= ", self.id, "  POS= ", self.posicion, "  CLIENTE= ",
                                        self.get_cliente()])
                        juego.unlock_casillas(pos_bloqueadas)
            else:
                pos_bloqueadas = juego.lock_alrededor(self.posicion)
                pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas)
                if self.cliente is None:
                    if len(pos_disp) == 1:
                        rand_index = 0
                    else:
                        rand_index = randint(0, len(pos_disp) - 1)
                    code = juego.insertar_elemento(self, pos_disp[rand_index])
                else:
                    pos = self.decidir_mov(pos_disp, juego)
                    code = juego.insertar_elemento(self, pos)

                juego.print_lock.acquire()
                if code[0] == "paradaTaxi":
                    print("TAXI se mueve y PARA: ID= ", self.id, " POS=", self.posicion, " {Cliente ", code[1],
                          " se baja}")
                    n_clientes_transportados = n_clientes_transportados + 1
                juego.print_lock.release()

                juego.unlock_casillas(pos_bloqueadas)
            sleep(1)
