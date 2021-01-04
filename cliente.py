from random import randint
from threading import Thread, Lock
from time import sleep


class Cliente:
    n_clientes = 0
    nclientes_lock = Lock()

    def __init__(self, id, entorno):
        self.id = id
        self.destino = [randint(0, entorno.DIMENSION_MATRIZ - 1), randint(0, entorno.DIMENSION_MATRIZ - 1)]
        self.posicion = []
        self.pasajero = False

    def ciclo_cliente(self, juego):
        primera_iteracion = True
        destino_alcanzado = False

        while not juego.elemento_ganador and not destino_alcanzado:
            if primera_iteracion:
                pos_disp = [randint(0, juego.DIMENSION_MATRIZ - 1), randint(0, juego.DIMENSION_MATRIZ - 1)]
                juego.matriz[pos_disp[0]][pos_disp[1]].estado.acquire()
                estado = juego.insertar_elemento(self, pos_disp)
                juego.imprimir(
                    ["Colocacion cliente: ID=", self.id, " POS=", self.posicion, " PASAJERO?=", self.pasajero])
            else:
                pos_disp = juego.lock_alrededor(self.posicion)
                rand_index = randint(0, len(pos_disp) - 1)
                estado = juego.insertar_elemento(self, pos_disp[rand_index])

            if estado[0] == "taxi":
                juego.imprimir(
                    ["CLIENTE MONTADO: ID=", self.id, " POS=", self.posicion, " TAXIID=", estado[1], " TAXIPOS=",
                     estado[2], " TAXIClienteID=", estado[3]])
            elif estado[0] == "autobus":
                juego.imprimir(["CLIENTE MONTADO: ID=", self.id, " POS=", self.posicion, " AUTOBUSID=", estado[1],
                                " AUTOBUSPOS= ", estado[2], " AUTOBUSPARADO= ", estado[3]])

            if primera_iteracion:
                juego.matriz[pos_disp[0]][pos_disp[1]].estado.release()
                primera_iteracion = False
            else:
                juego.unlock_casillas(pos_disp)

            while not juego.elemento_ganador and (self.pasajero or juego.matriz[self.posicion[0]][self.posicion[1]].estado.locked()):
                pass

            if not juego.elemento_ganador and self.posicion == self.destino:
                juego.imprimir(["EXITO Cliente: ID=", self.id, " DEST=", self.destino, " {Cliente llega destino}"])
                juego.matriz[self.destino[0]][self.destino[1]].clientes.remove(self)
                destino_alcanzado = True

                self.nclientes_lock.acquire()
                self.n_clientes = self.n_clientes + 1
                self.nclientes_lock.release()
                c = Cliente(self.n_clientes, juego)

                t = Thread(target=c.ciclo_cliente, args=(juego, ))
                t.start()
                t.join()

            sleep(4)
