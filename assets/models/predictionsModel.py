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

def projection_Balance_General(cantidadPeriodosPredecir, dataSet, resultadosNetos):
    # Verifica si el índice es temporal
    if not isinstance(dataSet.index, pd.DatetimeIndex):
        raise ValueError("El índice del DataFrame debe ser un DatetimeIndex.")
    
    # Rubros a predecir
    rubrosToPredict = [
        "Propiedad, Planta y Equipo", 
        "Activos Intangibles y Valor Llave", 
        "Cuentas por Cobrar No Corrientes",
        "Activos Financieros a Largo Plazo", 
        "Activos Diferidos", 
        "Otros Activos No Corrientes",

        "Inventarios", 
        "Cuentas por Cobrar", 
        "Pagos Anticipados",

        "Activos Financieros de Corto Plazo", 
        "Efectivo o Equivalentes", 
        "Otros Activos Corrientes",

        "Capital Suscrito", 
        "Resultados Acumulados", 
        "Otro Patrimonio",

        "Créditos y Préstamos No Corrientes", 
        "Cuentas por Pagar No Corrientes",
        "Otros Pasivos No Corrientes", 
        "Créditos y Préstamos Corrientes", 
        "Cuentas por Pagar",
        "Otros Pasivos Corrientes"
    ]

    
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

    dfPredicciones["Utilidad del Periodo"] = resultadosNetos

    dfPredicciones["Activos No Corrientes"] = (
    dfPredicciones["Propiedad, Planta y Equipo"] +
    dfPredicciones["Activos Intangibles y Valor Llave"] +
    dfPredicciones["Cuentas por Cobrar No Corrientes"] +
    dfPredicciones["Activos Financieros a Largo Plazo"] +
    dfPredicciones["Activos Diferidos"] +
    dfPredicciones["Otros Activos No Corrientes"]
    )

    dfPredicciones["Activos Corrientes"] = (
        dfPredicciones["Inventarios"] +
        dfPredicciones["Cuentas por Cobrar"] +
        dfPredicciones["Pagos Anticipados"] +
        dfPredicciones["Activos Financieros de Corto Plazo"] +
        dfPredicciones["Efectivo o Equivalentes"] +
        dfPredicciones["Otros Activos Corrientes"]
    )

    dfPredicciones["Activos Totales"] = (
        dfPredicciones["Activos Corrientes"] + 
        dfPredicciones["Activos No Corrientes"]
    )

    dfPredicciones["Total de Patrimonio"] = (
        dfPredicciones["Capital Suscrito"] +
        dfPredicciones["Resultados Acumulados"] +
        dfPredicciones["Utilidad del Periodo"] +
        dfPredicciones["Otro Patrimonio"]
    )

    dfPredicciones["Pasivos No Corrientes"] = (
        dfPredicciones["Créditos y Préstamos No Corrientes"] +
        dfPredicciones["Cuentas por Pagar No Corrientes"] +
        dfPredicciones["Otros Pasivos No Corrientes"]
    )

    dfPredicciones["Pasivos Corrientes"] = (
        dfPredicciones["Créditos y Préstamos Corrientes"] +
        dfPredicciones["Cuentas por Pagar"] +
        dfPredicciones["Otros Pasivos Corrientes"]
    )

    dfPredicciones["Pasivos Totales"] = (
        dfPredicciones["Pasivos Corrientes"] +
        dfPredicciones["Pasivos No Corrientes"]
    )

    dfPredicciones["Total de Patrimonio y Pasivos"] = (
        dfPredicciones["Pasivos Totales"] +
        dfPredicciones["Total de Patrimonio"]
    )

    # Concatenar datos originales con predicciones
    dataSet = pd.concat([dataSet, dfPredicciones], axis=0)
    return dataSet

def projection_Flujo_Efectivo(cantidadPeriodosPredecir, dataSet):
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