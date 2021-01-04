import os
from random import randint
from time import sleep



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


def ciclo_autobus(autobus, juego):
    primera_iteracion = True
    cont = 0
    while True:
        cont = cont + 1

        if len(autobus.clientes) == juego.N_AUTOBUS_GANA:  # estado[4] contiene los clientes del autobus
            juego.print_lock.acquire()
            print("AUTOBUS GANA")
            os._exit(1)

        if primera_iteracion:
            primera_iteracion = False
            pos_posibles = [[0, 0], [0, juego.DIMENSION_MATRIZ - 1], [juego.DIMENSION_MATRIZ - 1, 0],
                            [juego.DIMENSION_MATRIZ - 1, juego.DIMENSION_MATRIZ - 1]]
            pos_disp = []
            while not pos_disp:
                pos_bloqueadas = juego.lock_posiciones(pos_posibles)
                pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas, False)
                if len(pos_disp) == 0:
                    juego.unlock_casillas(pos_bloqueadas)
                    sleep(0.2)
                else:
                    if len(pos_disp) == 1:
                        juego.insertar_elemento(autobus, pos_disp[0])
                    else:
                        juego.insertar_elemento(autobus, pos_disp[randint(0, len(pos_disp) - 1)])
                    juego.imprimir(["Colocacion autobus: ID= ", autobus.id, "  POS= ", autobus.posicion, " CLIENTES= ",
                                    autobus.obtener_clientes(), "cont=", cont])
                    juego.unlock_casillas(pos_bloqueadas)
        else:
            pos_bloqueadas = juego.lock_alrededor(autobus.posicion)
            pos_disp = juego.casillas_sin_vehiculos(pos_bloqueadas)
            if len(pos_disp) == 1:
                rand_index = 0
            else:
                rand_index = randint(0, len(pos_disp) - 1)
            juego.insertar_elemento(autobus, pos_disp[rand_index])
            if cont % 3 == 0:   # cada 3 mov una parada
                list_clientes = autobus.realizar_parada(juego)
                autobus.parado = True
                juego.print_lock.acquire()
                print("AUTOBUS se mueve y PARA: ID=", autobus.id, " POS= ", autobus.posicion, "PASAJEROS= ", autobus.obtener_clientes(), " cont", cont)
                for cliente in list_clientes:
                    print("PASAJERO FUERA: ClienteID= ", cliente.id, "  AutobusDejado= ", autobus.id, "  Posicion= ",
                          cliente.posicion,
                          "  pasajero?: ", cliente.pasajero)
                juego.print_lock.release()
                juego.unlock_casillas(pos_bloqueadas)
                sleep(1.5)
                autobus.parado = False
            else:
                juego.unlock_casillas(pos_bloqueadas)
                sleep(2)