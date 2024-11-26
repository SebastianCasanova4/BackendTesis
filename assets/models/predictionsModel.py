# datos y modelos
import numpy as np
import pandas as pd
from pmdarima import auto_arima

def projection_Estado_Resultados(cantidadPeriodosPredecir, dataSet, impuesto=0.3):
    # Verifica si el índice es temporal
    if not isinstance(dataSet.index, pd.DatetimeIndex):
        raise ValueError("El índice del DataFrame debe ser un DatetimeIndex.")
    
    # Rubros a predecir
    rubrosToPredict = [
        "Ventas", "Gastos de operación", "Gastos de venta y distribución",
        "Gastos administrativos", "Gastos de depreciación, amortización y deterioro", 
        "Otros resultados operativos netos", "Resultado financiero", 
        "Monto de Pérdidas o Ganancias Extraordinarias", "Impuesto a la renta",
        "Otros resultados no operativos netos"
    ]
    
    # Promedio del costo de ventas sobre las ventas
    promedioCostoVentas = promedio_porcentual_costo_ventas(dataSet)

    # Crear un DataFrame para las predicciones
    dfPredicciones = pd.DataFrame()

    # Generar modelos y predecir solo para rubros seleccionados
    for rubro in rubrosToPredict:
        if rubro in dataSet.columns and dataSet[rubro].notnull().all():
            modelo = auto_arima(dataSet[rubro], seasonal=True, m=1)
            prediccionActual = modelo.predict(n_periods=cantidadPeriodosPredecir)
            prediccionActual = pd.Series(prediccionActual, name=rubro)
            dfPredicciones = pd.concat([dfPredicciones, prediccionActual], axis=1)
        else:
            print(f"El rubro {rubro} tiene valores nulos o no existe en el dataset, no se puede proyectar")

    # Generar nuevas fechas para las predicciones
    ultimaFecha = dataSet.index[-1]
    frecuencia = pd.infer_freq(dataSet.index)  # Detectar frecuencia automáticamente
    if frecuencia is None:
        raise ValueError("No se pudo inferir la frecuencia del índice.")
    nuevasFechas = pd.date_range(start=ultimaFecha, periods=cantidadPeriodosPredecir + 1, freq=frecuencia)[1:]
    dfPredicciones.index = nuevasFechas  # Asignar nuevas fechas como índice

    # Calcular rubros dependientes
    dfPredicciones["Costo de ventas"] = dfPredicciones["Ventas"] * promedioCostoVentas
    dfPredicciones["Utilidad Bruta"] = dfPredicciones["Ventas"] + dfPredicciones["Costo de ventas"]
    dfPredicciones["Ganancia operativa (EBIT)"] = (
        dfPredicciones["Utilidad Bruta"] 
        + dfPredicciones["Gastos de venta y distribución"] 
        + dfPredicciones["Gastos administrativos"] 
        + dfPredicciones["Otros resultados operativos netos"]
    )
    dfPredicciones["Ganancias antes de impuestos"] = (
        dfPredicciones["Ganancia operativa (EBIT)"] 
        + dfPredicciones["Resultado financiero"] 
        + dfPredicciones["Otros resultados no operativos netos"] 
        + dfPredicciones["Monto de Pérdidas o Ganancias Extraordinarias"]
    )
    dfPredicciones["Impuesto a la renta"] = dfPredicciones["Ganancias antes de impuestos"] * impuesto
    dfPredicciones["Ganancia (Pérdida) Neta"] = (
        dfPredicciones["Ganancias antes de impuestos"] + dfPredicciones["Impuesto a la renta"]
    )
    
    # Concatenar datos originales con predicciones
    dataSet = pd.concat([dataSet, dfPredicciones], axis=0)
    return dataSet

# Funcion que calcula el promedio del porcentaje que corresponde a las ventas y su costo por venta. 
def promedio_porcentual_costo_ventas(pDataSet):
    porcentajes_costos_ventas = []
    for year in pDataSet.index:
        porcentaje = pDataSet.loc[year, "Costo de ventas"] / pDataSet.loc[year, "Ventas"]
        porcentajes_costos_ventas.append(porcentaje)   
    promedio = np.mean(porcentajes_costos_ventas)
    return promedio
