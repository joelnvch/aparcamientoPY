from clases import *
from random import randint
from time import sleep
import numpy as np
from threading import *

entorno = Entorno()
n_clientes = 0
print_lock = Lock()
nclientes_lock = Lock()
threads = []


def imprimir(string):
    print_lock.acquire()
    for palabra in string:
        print(palabra, end="")
    print()
    print_lock.release()


def ciclo_cliente(cliente_inic):
    global entorno, n_clientes
    cliente = cliente_inic
    cliente_inic_termina = False

    while True:
        primera_iteracion = True
        if cliente_inic_termina:
            nclientes_lock.acquire()
            n_clientes = n_clientes + 1
            cliente = Cliente(n_clientes)
            nclientes_lock.release()

        while True:
            if primera_iteracion:
                pos_disp = [randint(0, DIMENSION_MATRIZ - 1), randint(0, DIMENSION_MATRIZ - 1)]
                entorno.matriz[pos_disp[0]][pos_disp[1]].estado.acquire()
                estado = entorno.insertar_elemento(cliente, pos_disp)
                entorno.matriz[pos_disp[0]][pos_disp[1]].estado.release()
            else:
                pos_disp = entorno.lock_alrededor(cliente.posicion)
                rand_index = randint(0, len(pos_disp) - 1)
                estado = entorno.insertar_elemento(cliente, pos_disp[rand_index])
                entorno.unlock_casillas(pos_disp)

            print_lock.acquire()
            if primera_iteracion:
                print("Colocacion cliente: ID=", cliente.id, " POS=", cliente.posicion, " PASAJERO?=", cliente.pasajero,
                      " OBJETO=", cliente)
            else:
                print("Cliente Movimiento: ID=", cliente.id, " POS= ", cliente.posicion, " PASAJERO?=", cliente.pasajero)
            primera_iteracion = False

            if estado[0] == "taxi":
                print("CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " TAXIID=", estado[1])
            elif estado[0] == "autobus":
                print("CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " AUTOBUSID=", estado[1])
            elif cliente.posicion == cliente.destino:
                print("EXITO Cliente: ID=", cliente.id, " DEST=", cliente.destino, " {Cliente llega destino}")
                print_lock.release()
                # en este caso se llega caminando al destino por lo que la casilla destino siempre contiene al cliente antes de que acabe
                entorno.matriz[cliente.destino[0]][cliente.destino[1]].clientes.remove(cliente)
                cliente_inic_termina = True
                break

            print_lock.release()

            # cuadno cliente montado en vehiculo
            while cliente.pasajero or entorno.matriz[cliente.posicion[0]][cliente.posicion[1]].estado.locked():
                pass

            if cliente.posicion == cliente.destino:
                imprimir(["EXITO Cliente: ID=", cliente.id, " DEST=", cliente.destino])
                # en este caso la casilla destino puede contener o no el cliente ya que el taxi no deja al cliente en la casilla
                # solo actualiza su posicion en el objeto, un autobus deja al cliente en la casilla en todo caso
                entorno.matriz[cliente.destino[0]][cliente.destino[1]].clientes.remove(cliente)
                cliente_inic_termina = True
                break

            sleep(4)


def ciclo_autobus(autobus):
    global entorno
    primera_iteracion = True
    cont = 0

    while True:
        if primera_iteracion:
            primera_iteracion = False
            pos_posibles = entorno.casillas_sin_vehiculos([[0, 0], [0, DIMENSION_MATRIZ - 1],
                                                           [DIMENSION_MATRIZ - 1, 0],
                                                           [DIMENSION_MATRIZ - 1, DIMENSION_MATRIZ - 1]], False)
            pos_bloqueadas = pos_posibles[randint(0, len(pos_posibles) - 1)]
            while entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].vehiculo is not None:
                pass
            entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].estado.acquire()
            entorno.insertar_elemento(autobus, pos_bloqueadas)
            entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].estado.release()
            imprimir(["Colocacion autobus: ID= ", autobus.id, "  POS= ", autobus.posicion, " CLIENTES= ",
                      autobus.obtener_clientes()])
        else:
            pos_bloqueadas = entorno.lock_alrededor(autobus.posicion)
            pos_disp = entorno.casillas_sin_vehiculos(pos_bloqueadas)
            rand_index = randint(0, len(pos_disp) - 1)
            entorno.insertar_elemento(autobus, pos_disp[rand_index])

            cont = cont + 1
            # cada 3 movimientos habrá una parada
            if cont % 3 == 0:
                list_clientes = autobus.realizar_parada(entorno)
                entorno.unlock_casillas(pos_bloqueadas)
                print_lock.acquire()
                print("Autobus movimiento: ID= ", autobus.id, "  POS= ", autobus.posicion, "  CLIENTES: ",
                      autobus.obtener_clientes())
                print("AUTOBUS PARADA: ID=", autobus.id, " POS=", autobus.posicion)
                for cliente in list_clientes:
                    print("PASAJERO FUERA: ClienteID= ", cliente.id, "  AutobusDejado= ", autobus.id, "  Posicion= ",
                          cliente.posicion,
                          "  pasajero?: ", cliente.pasajero)
                print_lock.release()
            else:
                entorno.unlock_casillas(pos_bloqueadas)
                imprimir(["Autobus movimiento: ID= ", autobus.id, "  POS= ", autobus.posicion, "  CLIENTES: ",
                          autobus.obtener_clientes()])
        sleep(2)


def ciclo_taxi(taxi):
    global entorno
    primera_iteracion = True

    while True:
        # Ponerlo en la matriz
        if primera_iteracion:
            primera_iteracion = False
            pos = [randint(0, DIMENSION_MATRIZ - 1), randint(0, DIMENSION_MATRIZ - 1)]
            while entorno.matriz[pos[0]][pos[1]].vehiculo is not None:
                pass
            entorno.matriz[pos[0]][pos[1]].estado.acquire()
            entorno.insertar_elemento(taxi, pos)
            entorno.matriz[pos[0]][pos[1]].estado.release()
            imprimir(["Colocacion Taxi: ID= ", taxi.id, "  POS= ", taxi.posicion, "  CLIENTEisNone?= ", taxi.cliente is None])
        else:
            pos_bloqueadas = entorno.lock_alrededor(taxi.posicion)
            pos_disp = entorno.casillas_sin_vehiculos(pos_bloqueadas)

            if taxi.cliente is None:
                if len(pos_disp) == 1:
                    rand_index = 0
                if len(pos_disp) <= 0:
                    raise Exception("problema con casillas_sin_vehiculos o lock_alrededor")
                else:
                    rand_index = randint(0, len(pos_disp) - 1)
                code = entorno.insertar_elemento(taxi, pos_disp[rand_index])
            else:
                pos = taxi.decidir_mov(pos_disp, entorno)
                code = entorno.insertar_elemento(taxi, pos)

            entorno.unlock_casillas(pos_bloqueadas)

            print_lock.acquire()
            if code[0] == "paradaTaxi":
                print("Taxi movimiento: ID= ", taxi.id, " POS=", taxi.posicion, " CLIENTEisNone= [", taxi.cliente is None, "}")
                print("TAXI PARADA: ID= ", taxi.id, " POS=", taxi.posicion, " {Cliente ", code[1], " se baja}")
            else:
                print("Taxi movimiento: ID= ", taxi.id, " POS=", taxi.posicion, " CLIENTEisNone= [", taxi.cliente is None, "}")
            print_lock.release()
        sleep(1)


if __name__ == "__main__":
    # El número de clientes disponibles, de autobuses y de taxistas debe ser configurable al comenzar el juego.
    n_clientes = int(input("Introducir número de clientes: \n"))
    n_autobuses = int(input("Introducir número de autobuses: \n"))
    n_taxistas = int(input("Introducir número de taxistas: \n"))
    print()

    elementos_set = set()
    for i in range(1, n_clientes + 1):
        elementos_set.add(Cliente(i))
    for i in range(1, n_autobuses + 1):
        elementos_set.add(Autobus(i))
    for i in range(1, n_taxistas + 1):
        elementos_set.add(Taxi(i))

    for elemento in elementos_set:
        targ = None

        if isinstance(elemento, Cliente):
            targ = ciclo_cliente
        elif isinstance(elemento, Autobus):
            targ = ciclo_autobus
        elif isinstance(elemento, Taxi):
            targ = ciclo_taxi

        t = Thread(target=targ, args=(elemento,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
