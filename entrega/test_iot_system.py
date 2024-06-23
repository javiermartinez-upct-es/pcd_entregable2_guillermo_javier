import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from control_de_temperatura_iot import ServidorSingleton, DatosTemperatura, Observador, ManejadorCalculoEstadisticos, ManejadorComprobarUmbral, ManejadorComprobarAumento, EstrategiaMediaDesviacion, EstrategiaCuantiles, EstrategiaMinMax

def singleton():
    instancia = ServidorSingleton.obtenerInstancia()
    # Reseteamos la instancia para cada test
    instancia._unicaInstancia = None
    instancia = ServidorSingleton.obtenerInstancia()
    return instancia

def test_singleton_unica_instancia(singleton):
    otra_instancia = ServidorSingleton.obtenerInstancia()
    assert singleton is otra_instancia

def test_singleton_añadir_observador(singleton):
    observador_mock = Mock()
    singleton.añadir_observador(observador_mock)
    assert observador_mock in singleton.observadores


def test_manejador_calculo_estadisticos(singleton):
    estrategia = EstrategiaMediaDesviacion()
    manejador = ManejadorCalculoEstadisticos(estrategia)
    dato_temperatura1 = DatosTemperatura(datetime.now() - timedelta(seconds=30), 20.0)
    dato_temperatura2 = DatosTemperatura(datetime.now(), 25.0)
    singleton.notificar(dato_temperatura1)
    singleton.notificar(dato_temperatura2)
    manejador.manejar_datos()
    # Verificamos que los cálculos son correctos
    assert estrategia.calcular([20.0, 25.0]) == {'Media': 22.5, 'Desviación típica': 2.5}

def test_manejador_comprobar_umbral(singleton):
    umbral = 24.0
    manejador = ManejadorComprobarUmbral(umbral)
    dato_temperatura = DatosTemperatura(datetime.now(), 25.0)
    singleton.notificar(dato_temperatura)
    with pytest.raises(AssertionError):
        manejador.manejar_datos()
    assert singleton.obtener_datos()[-1].temperatura > umbral

def test_manejador_comprobar_aumento(singleton):
    manejador = ManejadorComprobarAumento()
    dato_temperatura1 = DatosTemperatura(datetime.now() - timedelta(seconds=20), 15.0)
    dato_temperatura2 = DatosTemperatura(datetime.now(), 26.0)
    singleton.notificar(dato_temperatura1)
    singleton.notificar(dato_temperatura2)
    with pytest.raises(AssertionError):
        manejador.manejar_datos()
    assert (singleton.obtener_datos()[-1].temperatura - singleton.obtener_datos()[-2].temperatura) > 10

def test_estrategia_media_desviacion():
    estrategia = EstrategiaMediaDesviacion()
    temperaturas = [20.0, 25.0, 30.0]
    resultado = estrategia.calcular(temperaturas)
    assert resultado == {'Media': 25.0, 'Desviación típica': 4.08248290463863}

def test_estrategia_cuantiles():
    estrategia = EstrategiaCuantiles()
    temperaturas = [20.0, 25.0, 30.0]
    resultado = estrategia.calcular(temperaturas)
    assert resultado == {'Percentil 25%': 22.5, 'Percentil 50% (media)': 25.0, 'Percentil 75%': 27.5}

def test_estrategia_min_max():
    estrategia = EstrategiaMinMax()
    temperaturas = [20.0, 25.0, 30.0]
    resultado = estrategia.calcular(temperaturas)
    assert resultado == {'Mínimo': 20.0, 'Máximo': 30.0}
