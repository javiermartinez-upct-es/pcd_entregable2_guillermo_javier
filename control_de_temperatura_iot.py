from datetime import datetime

class ServidorSingleton:
    _unicaInstancia = None

    def __init__(self):
        self.observadores = []
        self.datos = []

    @classmethod
    def obtenerInstancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia

    def obtener_datos(self):
        return self.datos

    def añadir_observador(self, observador):
        self.observadores.append(observador)

    def notificar(self, datos):
        self.datos.append(datos)
        for observador in self.observadores:
            observador.actualizar()


class Observador:
    def actualizar(self):
        pass