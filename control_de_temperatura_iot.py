from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json
import numpy as np
from kafka import KafkaConsumer
import time

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
        self.datos.append(datos)  # Primero almacenamos los datos de temperatura
        for observador in self.observadores:  # Luego notificamos a los observadores
            observador.actualizar()

class DatosTemperatura:
    def __init__(self, timestamp, temperatura):
        self.timestamp = timestamp
        self.temperatura = temperatura

class Observador:  # Implementación del patrón Observer y Manejador (Chain of responsability)
    def __init__(self, sucesor=None):
        self.sucesor = sucesor

    def manejar_datos(self):
        if self.sucesor:
            self.sucesor.manejar_datos()

    def actualizar(self):
        self.manejar_datos()
    # Cuando se actualiza un dato se maneja, ya que cada nuevo valor de temperatura recibido debe de implicar la realización de una serie de pasos encadenados
    
class ManejadorCalculoEstadisticos(Observador):
    def __init__(self, estrategia, sucesor=None):
        super().__init__(sucesor)
        self.estrategia = estrategia

    def manejar_datos(self):
        ahora = datetime.now()
        hace_60_segundos = ahora - timedelta(seconds=60)
        datos_recientes = list(filter(lambda x: x.timestamp >= hace_60_segundos, ServidorSingleton.obtenerInstancia().obtener_datos()))
        temperaturas = list(map(lambda x: x.temperatura, datos_recientes))
        
        if temperaturas:
            estadisticos = self.estrategia.calcular(temperaturas)
            print(f"Estadísticas calculadas: {estadisticos}")
        
        super().manejar_datos()

class ManejadorComprobarUmbral(Observador):
    def __init__(self, umbral, sucesor=None):
        super().__init__(sucesor)
        self.umbral = umbral

    def manejar_datos(self):
        temperatura = ServidorSingleton.obtenerInstancia().obtener_datos()[-1].temperatura  # Extraemos la última medida de temperatura para comprobar el umbral
        if temperatura > self.umbral:
            print(f"La temperatura {temperatura} supera el umbral de {self.umbral}")
        
        super().manejar_datos()

class ManejadorComprobarAumento(Observador):
    def manejar_datos(self):
        ahora = datetime.now()
        hace_30_segundos = ahora - timedelta(seconds=30)
        datos_recientes = list(filter(lambda x: x.timestamp >= hace_30_segundos, ServidorSingleton.obtenerInstancia().obtener_datos()))
        temperaturas = list(map(lambda x: x.temperatura, datos_recientes))
        
        if len(temperaturas) > 1 and (temperaturas[-1] - temperaturas[0]) > 10:
            print(f"La temperatura ha aumentado más de 10 grados en los últimos 30 segundos")
        
        super().manejar_datos()

class EstrategiaEstadisticos(ABC):
    @abstractmethod
    def calcular(self, temperaturas):
        pass

class EstrategiaMediaDesviacion(EstrategiaEstadisticos):
    def calcular(self, temperaturas):
        media = np.mean(temperaturas)
        desviacion = np.std(temperaturas)
        return {
            "Media": media,
            "Desviación típica": desviacion
        }

class EstrategiaCuantiles(EstrategiaEstadisticos):
    def calcular(self, temperaturas):
        cuantiles = np.percentile(temperaturas, [25, 50, 75])
        return {
            "Percentil 25%": cuantiles[0],
            "Percentil 50% (media)": cuantiles[1],
            "Percentil 75%": cuantiles[2]
        }

class EstrategiaMinMax(EstrategiaEstadisticos):
    def calcular(self, temperaturas):
        min = np.min(temperaturas)
        max = np.max(temperaturas)
        return {
            "Mínimo": min,
            "Máximo": max
        }

class Consumidor:
    def __init__(self, topico):
        self.topico = topico
        self.consumidor = KafkaConsumer(
            self.topico,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='iot-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.servidor = ServidorSingleton.obtenerInstancia()
        self.servidor.añadir_observador(ManejadorComprobarAumento())

    def empezar_a_consumir(self):
        for mensaje in self.consumidor:
            datos = mensaje.value
            timestamp = datetime.fromisoformat(datos["timestamp"])
            temperatura = datos["temperatura"]
            dato = DatosTemperatura(timestamp, temperatura)
            self.servidor.notificar(dato)
            print(f"Recibido: {datos}")

'''if __name__ == '__main__':
    import sys
    topico = sys.argv[1]
    consumidor = Consumidor(topico)
    consumidor.empezar_a_consumir()'''

# Ejemplo de uso
server = ServidorSingleton.obtenerInstancia()
server.añadir_observador(ManejadorCalculoEstadisticos(EstrategiaMediaDesviacion()))
server.añadir_observador(ManejadorComprobarUmbral(25))
server.añadir_observador(ManejadorComprobarAumento())

# Simular la recepción de datos
from time import sleep

for i in range(10):
    timestamp = datetime.now()
    temperatura = np.random.uniform(20, 30)
    dato = DatosTemperatura(timestamp, temperatura)
    server.notificar(dato)
    sleep(5) # Esperar 5 segundos antes de recibir el siguiente dato

# Ejemplo de uso
server = ServidorSingleton.obtenerInstancia()
server.añadir_observador(ManejadorComprobarAumento())

# Simular la recepción de datos con un rápido aumento de temperatura
def simular_datos_rapidos():
    incrementos = [20, 25, 35, 40]  # Valores de temperatura para simular un rápido aumento
    for incremento in incrementos:
        timestamp = datetime.now()
        temperatura = incremento
        dato = DatosTemperatura(timestamp, temperatura)
        server.notificar(dato)
        time.sleep(5)  # Esperar 5 segundos antes de recibir el siguiente dato

# Ejecutar la simulación
simular_datos_rapidos()
