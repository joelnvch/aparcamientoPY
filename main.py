from clases import *
from random import randint
from time import sleep
from threading import *
from entorno import Entorno
import sys

N_AUTOBUS_GANA = 4      # clientes necesarios para que
N_TAXI_GANA = 5         #      gane uno u otro

entorno = Entorno()
n_clientes = 0
print_lock = Lock()
nclientes_lock = Lock()

autobus_gana = False
taxi_gana = False


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
                imprimir(["Colocacion cliente: ID=", cliente.id, " POS=", cliente.posicion, " PASAJERO?=", cliente.pasajero])
            else:
                pos_disp = entorno.lock_alrededor(cliente.posicion)
                rand_index = randint(0, len(pos_disp) - 1)
                estado = entorno.insertar_elemento(cliente, pos_disp[rand_index])

            if estado[0] == "taxi":
                imprimir(["CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " TAXIID=", estado[1], " TAXIPOS=", estado[2], " TAXIClienteID=", estado[3]])
            elif estado[0] == "autobus":
                imprimir(["CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " AUTOBUSID=", estado[1], " AUTOBUSPOS= ", estado[2], " AUTOBUSPARADO= ", estado[3]])

            if primera_iteracion:
                entorno.matriz[pos_disp[0]][pos_disp[1]].estado.release()
                primera_iteracion = False
            else:
                entorno.unlock_casillas(pos_disp)

            while cliente.pasajero or entorno.matriz[cliente.posicion[0]][cliente.posicion[1]].estado.locked() :
                pass

            if cliente.posicion == cliente.destino:
                imprimir(["EXITO Cliente: ID=", cliente.id, " DEST=", cliente.destino, " {Cliente llega destino}"])
                entorno.matriz[cliente.destino[0]][cliente.destino[1]].clientes.remove(cliente)
                cliente_inic_termina = True
                break

            sleep(4)


def ciclo_autobus(autobus):
    global entorno
    primera_iteracion = True
    cont = 0

    while True:
        cont = cont + 1

        if len(autobus.clientes) == N_AUTOBUS_GANA:
            global autobus_gana
            autobus_gana = True

        if primera_iteracion:
            primera_iteracion = False

            pos_posibles = None
            while pos_posibles is None:
                try:
                    pos_posibles = [[0, 0], [0, DIMENSION_MATRIZ - 1], [DIMENSION_MATRIZ - 1, 0], [DIMENSION_MATRIZ - 1, DIMENSION_MATRIZ - 1]]
                    pos_bloqueadas = pos_posibles[randint(0, 3)]
                    while entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].vehiculo is not None:
                        pass
                    entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].estado.acquire()
                    entorno.insertar_elemento(autobus, pos_bloqueadas)
                except VehiculoException:
                    entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].estado.release()
                    pos_posibles = None

            imprimir(["Colocacion autobus: ID= ", autobus.id, "  POS= ", autobus.posicion, " CLIENTES= ",
                      autobus.obtener_clientes(), "cont=", cont])
            entorno.matriz[pos_bloqueadas[0]][pos_bloqueadas[1]].estado.release()
        else:
            pos_bloqueadas = entorno.lock_alrededor(autobus.posicion)
            pos_disp = entorno.casillas_sin_vehiculos(pos_bloqueadas)
            if len(pos_disp) == 1:
                rand_index = 0
            else:
                rand_index = randint(0, len(pos_disp) - 1)
            entorno.insertar_elemento(autobus, pos_disp[rand_index])

            if cont % 3 == 0:   # cada 3 mov una parada
                list_clientes = autobus.realizar_parada(entorno)
                autobus.parado = True

                print_lock.acquire()
                print("AUTOBUS se mueve y PARA: ID=", autobus.id, " POS= ", autobus.posicion, "PASAJEROS= ", autobus.obtener_clientes(), " cont", cont)
                for cliente in list_clientes:
                    print("PASAJERO FUERA: ClienteID= ", cliente.id, "  AutobusDejado= ", autobus.id, "  Posicion= ",
                          cliente.posicion,
                          "  pasajero?: ", cliente.pasajero)
                print_lock.release()

                entorno.unlock_casillas(pos_bloqueadas)

                sleep(1.5)
                autobus.parado = False
            else:
                entorno.unlock_casillas(pos_bloqueadas)
                sleep(2)


def ciclo_taxi(taxi):
    global entorno
    primera_iteracion = True
    n_clientes_transportados = 0

    while True:
        if n_clientes_transportados == N_TAXI_GANA:
            global taxi_gana
            taxi_gana = True

        # Ponerlo en la matriz
        if primera_iteracion:
            primera_iteracion = False

            pos = None
            while pos is None:
                try:
                    pos = [randint(0, DIMENSION_MATRIZ - 1), randint(0, DIMENSION_MATRIZ - 1)]
                    while entorno.matriz[pos[0]][pos[1]].vehiculo is not None:
                        pass
                    entorno.matriz[pos[0]][pos[1]].estado.acquire()
                    entorno.insertar_elemento(taxi, pos)
                except VehiculoException:
                    entorno.matriz[pos[0]][pos[1]].estado.release()
                    pos = None

            imprimir(["Colocacion Taxi: ID= ", taxi.id, "  POS= ", taxi.posicion, "  CLIENTEisNone?= ",
                      taxi.cliente is None])
            entorno.matriz[pos[0]][pos[1]].estado.release()

        else:
            pos_bloqueadas = entorno.lock_alrededor(taxi.posicion)
            pos_disp = entorno.casillas_sin_vehiculos(pos_bloqueadas)

            if taxi.cliente is None:
                if len(pos_disp) == 1:
                    rand_index = 0
                else:
                    rand_index = randint(0, len(pos_disp) - 1)
                code = entorno.insertar_elemento(taxi, pos_disp[rand_index])
            else:
                pos = taxi.decidir_mov(pos_disp, entorno)
                code = entorno.insertar_elemento(taxi, pos)

            print_lock.acquire()
            if code[0] == "paradaTaxi":
                print("TAXI se mueve y PARA: ID= ", taxi.id, " POS=", taxi.posicion, " {Cliente ", code[1], " se baja}")
                n_clientes_transportados = n_clientes_transportados + 1
            print_lock.release()

            entorno.unlock_casillas(pos_bloqueadas)

        sleep(1)


if __name__ == "__main__":
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
        t.daemon = True
        t.start()

    while True:
        if autobus_gana:
            print_lock.acquire()
            print("AUTOBUS GANA")
            sys.exit()
        elif taxi_gana:
            print_lock.acquire()
            print("TAXI GANA")
            sys.exit()
