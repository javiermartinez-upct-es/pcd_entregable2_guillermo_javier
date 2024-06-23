from kafka import KafkaProducer
import time
import json
import random
from datetime import datetime

class GeneradorDatosTemperatura:
    @staticmethod
    def generar_dato():
        temperatura = random.uniform(15, 30)  # Generar una temperatura aleatoria entre 15 y 30 grados
        timestamp = datetime.now().isoformat()
        return {
            "timestamp": timestamp,
            "temperatura": temperatura
        }

class Productor:
    def __init__(self, topico, frecuencia):
        self.topico = topico
        self.frecuencia = frecuencia if isinstance(frecuencia, int) else int(frecuencia)
        self.productor = KafkaProducer(
            bootstrap_servers='localhost:9092',
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def empezar_a_producir(self):
        while True:
            dato = GeneradorDatosTemperatura.generar_dato()
            self.productor.send(self.topico, value=dato)
            print(f'Enviado: {dato}')
            time.sleep(self.frecuencia)

if __name__ == '__main__':
    import sys
    topico = sys.argv[1]
    frecuencia = int(sys.argv[2])
    productor = Productor(topico, frecuencia)
    productor.empezar_a_producir()
