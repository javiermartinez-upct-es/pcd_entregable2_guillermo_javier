from datetime import datetime, timedelta

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

class DatosTemperatura:
    def __init__(self, timestamp, temperatura):
        self.timestamp = timestamp
        self.temperatura = temperatura

class Observador:
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    def manejar_datos(self):
        if self.sucesor:
            self.sucesor.manejar_datos()

    def actualizar(self):
        self.manejar_datos()

class ManejadorCalculoEstadisticos(Observador):
    def __init__(self, sucesor=None):
        super().__init__(sucesor)

    def manejar_datos(self):
        ahora = datetime.now()
        hace_60_segundos = ahora - timedelta(seconds=60)
        datos_recientes = list(filter(lambda x: x.timestamp >= hace_60_segundos, ServidorSingleton.obtenerInstancia().obtener_datos()))
        temperaturas = list(map(lambda x: x.temperatura, datos_recientes))

        if temperaturas:
            media = sum(temperaturas) / len(temperaturas)
            print(f"Media de las temperaturas: {media}")

        super().manejar_datos()