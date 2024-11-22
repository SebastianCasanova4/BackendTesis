# datos y modelos
import pandas as pd
from sklearn import metrics
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error

def projection(cantidadPeriodosPredecir, dataSet):
    # Verifica si el índice es temporal
    if not isinstance(dataSet.index, pd.DatetimeIndex):
        raise ValueError("El índice del DataFrame debe ser un DatetimeIndex.")
    
    # Extraemos los features del dataset
    rubros = dataSet.columns[:]
    
    # Definimos la cantidad de periodos que vamos a usar para probar el modelo
    numPeriodosPruebas = 1
    modelos = []
    train = dataSet[:-numPeriodosPruebas]
    test = dataSet[-numPeriodosPruebas:]
    
    # Crear un DataFrame para las predicciones
    dfPredicciones = pd.DataFrame()
    
    for feature in rubros:
        # Verificar si hay valores nulos
        if dataSet[feature].isnull().sum() > 0:
            print("El rubro ", feature, " tiene valores nulos, no se puede proyectar")
            continue
        else:
            modelos.append(auto_arima(train[feature], seasonal=True, m=1))

    for indice, modelo in enumerate(modelos):
        prediccionActual = modelo.predict(n_periods=cantidadPeriodosPredecir)
        prediccionActual = pd.Series(prediccionActual, name=rubros[indice])
        dfPredicciones = pd.concat([dfPredicciones, prediccionActual], axis=1)
    
    # Generar nuevas fechas para las predicciones
    ultimaFecha = dataSet.index[-1]
    frecuencia = pd.infer_freq(dataSet.index)  # Detectar frecuencia automáticamente
    if frecuencia is None:
        raise ValueError("No se pudo inferir la frecuencia del índice.")
    
    nuevasFechas = pd.date_range(start=ultimaFecha, periods=cantidadPeriodosPredecir + 1, freq=frecuencia)[1:]
    dfPredicciones.index = nuevasFechas  # Asignar nuevas fechas como índice
    
    # Concatenar predicciones al DataFrame original
    dataSet = pd.concat([dataSet, dfPredicciones], axis=0)
    return dataSet

        
        
    
   
    
   
    
    
    