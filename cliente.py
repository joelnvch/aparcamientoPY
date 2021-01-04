from random import randint
from time import sleep


class Cliente:
    def __init__(self, id, entorno):
        self.id = id
        self.destino = [randint(0, entorno.DIMENSION_MATRIZ - 1), randint(0, entorno.DIMENSION_MATRIZ - 1)]
        self.posicion = []
        self.pasajero = False


def ciclo_cliente(cliente, juego):
    primera_iteracion = True
    while True:
        if primera_iteracion:
            pos_disp = [randint(0, juego.DIMENSION_MATRIZ - 1), randint(0, juego.DIMENSION_MATRIZ - 1)]
            juego.matriz[pos_disp[0]][pos_disp[1]].estado.acquire()
            estado = juego.insertar_elemento(cliente, pos_disp)
            juego.imprimir(
                ["Colocacion cliente: ID=", cliente.id, " POS=", cliente.posicion, " PASAJERO?=", cliente.pasajero])
        else:
            pos_disp = juego.lock_alrededor(cliente.posicion)
            rand_index = randint(0, len(pos_disp) - 1)
            estado = juego.insertar_elemento(cliente, pos_disp[rand_index])

        if estado[0] == "taxi":
            juego.imprimir(
                ["CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " TAXIID=", estado[1], " TAXIPOS=",
                 estado[2], " TAXIClienteID=", estado[3]])
        elif estado[0] == "autobus":
            juego.imprimir(["CLIENTE MONTADO: ID=", cliente.id, " POS=", cliente.posicion, " AUTOBUSID=", estado[1],
                            " AUTOBUSPOS= ", estado[2], " AUTOBUSPARADO= ", estado[3]])

        if primera_iteracion:
            juego.matriz[pos_disp[0]][pos_disp[1]].estado.release()
            primera_iteracion = False
        else:
            juego.unlock_casillas(pos_disp)

        while cliente.pasajero or juego.matriz[cliente.posicion[0]][cliente.posicion[1]].estado.locked():
            pass

        if cliente.posicion == cliente.destino:
            juego.imprimir(["EXITO Cliente: ID=", cliente.id, " DEST=", cliente.destino, " {Cliente llega destino}"])
            juego.matriz[cliente.destino[0]][cliente.destino[1]].clientes.remove(cliente)

            juego.nclientes_lock.acquire()
            juego.n_clientes = juego.n_clientes + 1
            juego.nclientes_lock.release()
            c = Cliente(juego.n_clientes, juego)
            ciclo_cliente(c, juego)

        sleep(4)
