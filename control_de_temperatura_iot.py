from datetime import datetime

class ServidorSingleton:
    _unicaInstancia = None

    def __init__(self):
        self.datos = []

    @classmethod
    def obtenerInstancia(cls):
        if not cls._unicaInstancia:
            cls._unicaInstancia = cls()
        return cls._unicaInstancia

    def obtener_datos(self):
        return self.datos

    def notificar(self, datos):
        self.datos.append(datos)
