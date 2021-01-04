from autobus import Autobus
from threading import *
from cliente import Cliente
from juego import Juego

from taxi import Taxi

if __name__ == "__main__":
    n_clientes = int(input("Introducir número de clientes: \n"))
    n_autobuses = int(input("Introducir número de autobuses: \n"))
    n_taxistas = int(input("Introducir número de taxistas: \n"))
    print()

    juego = Juego()

    elementos_set = set()
    for i in range(1, n_clientes + 1):
        elementos_set.add(Cliente(i, juego))
    for i in range(1, n_autobuses + 1):
        elementos_set.add(Autobus(i))
    for i in range(1, n_taxistas + 1):
        elementos_set.add(Taxi(i))

    for elemento in elementos_set:
        targ = None
        if isinstance(elemento, Cliente):
            targ = Cliente.ciclo_cliente
        elif isinstance(elemento, Autobus):
            targ = Autobus.ciclo_autobus
        elif isinstance(elemento, Taxi):
            targ = Taxi.ciclo_taxi

        t = Thread(target=targ, args=(elemento, juego))
        t.start()


