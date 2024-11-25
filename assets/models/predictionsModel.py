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

 
   ########################### Proyectores Individuales ############################
   ## Función que se encarga de entrenar los modelos para cada rubro a proyectar.
def entrenar_modelos(pRubros_proyectar, pDataSet, pTipo_estado_financiero):
    rubros_proyectados = []
    for rubro in pRubros_proyectar:
            # Verificar si hay valores nulos ya que SARIMA Y ARIMA no pueden trabajar con nulos.
        if pDataSet[rubro].isnull().sum() > 0:
            print("El rubro ", rubro, " tiene valores nulos por lo que no se puede proyectar correctamente.")
            pDataSet[rubro] = pDataSet[rubro].fillna(0)
            rubros_proyectados.append(auto_arima(pDataSet[rubro], seasonal=True, m=pTipo_estado_financiero))
        else:
            rubros_proyectados.append(auto_arima(pDataSet[rubro], seasonal=True, m=pTipo_estado_financiero))
    return rubros_proyectados




## Funcion que calcula el promedio del porcentaje que corresponde a las ventas y su costo por venta. 
def promedio_porcentual_costo_ventas(pDataSet):
    # Lista con el porcentaje de costo de ventas sobre la venta para cada año.
    porcentajes_costos_ventas = []
    # Recorremos todas las filas del DataSet calculando el procentaje de costo de venta con respecto a la venta.
    for year in pDataSet.index:
        porcentaje = pDataSet.loc[year, "Costo de ventas"] / pDataSet.loc[year, "Ventas"]
        porcentajes_costos_ventas.append(porcentaje)   
        
    # Calculamos el promedio de los porcentajes.
    promedio = np.mean(porcentajes_costos_ventas)
    return promedio



# Funcion que se encarga de sacar la temporalidad de los periodos para obtener el parametro que se usa en los modelos de proyeccion
def obtener_temporalidad(pTipo_estado_financiero):
    if(pTipo_estado_financiero == "Anual, Indiv."):
        return 1
    elif(pTipo_estado_financiero == "Semestral, Indiv."):
        return 2
    elif(pTipo_estado_financiero == "Trimestralmente, Indiv."):
        return 4
    elif(pTipo_estado_financiero == "Cuatrimestral, Indiv."):
        return 3
    elif(pTipo_estado_financiero == "Mensual, Indiv."):
        return 12
    return 1

##Proyección de datos especifica para el Estado de Resultados
## @param pTIPO_ESTADO_FINANCIERO = corresponde al valor de la periodicidad de los estados financiero, 1 para años, 2 para semestres, 3 para cuatrimestres, 4 para trimiestres. 12 para mensual.
def projection_estado_resultados(pCantidad_periodos_proyectar, pDfEstadoResultados, pTipo_estado_financiero = 1):
    
    
    temporalidad = obtener_temporalidad(pTipo_estado_financiero)
    
    # Lista de rubros que proyectaremos usando los modelos.
    rubros_proyectar = ["Ventas", "Gastos de venta y distribución", "Gastos administrativos", "Otros resultados operativos netos", "Resultado financiero", "Otros resultados no operativos netos", "Monto de Pérdidas o Ganancias Extraordinarias"]
   
    # Debido a que cada rubro se proyecta independientemente, se debe crear un modelo para cada rubro.
    modelos = []
    # Creamos una estructura donde almacenaremos las respectivas predicciones.
    df_predicciones = pd.DataFrame()
    
    #Entrenamos los modelos.
    modelos = entrenar_modelos(rubros_proyectar, pDfEstadoResultados, temporalidad)
    
    # Proyectar los rubros
    # Promedio del porcentaje de costo de ventas sobre las ventas.
    promedio_costo_ventas = promedio_porcentual_costo_ventas(pDfEstadoResultados)
    # Impuesto a la renta
    impuesto = pDfEstadoResultados["Impuesto a la renta"].iloc[-1] / pDfEstadoResultados["Ganancias antes de impuestos"].iloc[-1]
    
    # Proyectamos todos los indices que requieren de modelos.
    for indice, modelo in enumerate(modelos):
        prediccion_actual = modelo.predict(n_periods=pCantidad_periodos_proyectar)
        prediccion_actual = pd.Series(prediccion_actual, name = rubros_proyectar[indice])
        df_predicciones = pd.concat([df_predicciones, prediccion_actual], axis=1)
        
    # Calculamos los rubros que dependen de los proyectados.
    # Costo de ventas.
    costo_ventas_proyectado = pd.Series(df_predicciones["Ventas"] * promedio_costo_ventas, name="Costo de ventas")
    df_predicciones = pd.concat([df_predicciones, costo_ventas_proyectado], axis=1)
    
    # Utilidad Bruta
    utilidad_bruta_proyectada = pd.Series(df_predicciones["Ventas"] + df_predicciones["Costo de ventas"], name="Utilidad Bruta")
    df_predicciones = pd.concat([df_predicciones, utilidad_bruta_proyectada], axis=1)
    
    #Ganancia operativa (EBIT)
    EBIT_proyectado = pd.Series(df_predicciones["Utilidad Bruta"] + df_predicciones["Gastos de venta y distribución"] + df_predicciones["Gastos administrativos"] + df_predicciones["Otros resultados operativos netos"], name="Ganancia operativa (EBIT)")
    df_predicciones = pd.concat([df_predicciones, EBIT_proyectado], axis=1)
    
    # Ganancias antes de impuestos
    ganancias_antes_impuestos_proyectado = pd.Series(df_predicciones["Ganancia operativa (EBIT)"] + df_predicciones["Resultado financiero"] + df_predicciones["Otros resultados no operativos netos"] + df_predicciones["Monto de Pérdidas o Ganancias Extraordinarias"], name="Ganancias antes de impuestos")
    df_predicciones = pd.concat([df_predicciones, ganancias_antes_impuestos_proyectado], axis=1)
    
    #Impuesto a la renta
    impuesto_renta = pd.Series(df_predicciones["Ganancias antes de impuestos"] * impuesto, name="Impuesto a la renta")
    df_predicciones = pd.concat([df_predicciones, impuesto_renta], axis=1)
    
    #Ganancias (Pérdida) Neta
    resultado_neto = pd.Series(df_predicciones["Ganancias antes de impuestos"] + df_predicciones["Impuesto a la renta"], name="Ganancia (Pérdida) Neta")
    df_predicciones = pd.concat([df_predicciones, resultado_neto], axis=1)
    
    #Añadimos los rubros proyectados a nuestro dataset original.
    
    # Generar nuevas fechas para las predicciones.
    ultimaFecha = pDfEstadoResultados.index[-1]
    # Detectamos la frecuencia de los periodos automáticamente
    frecuencia = pd.infer_freq(pDfEstadoResultados.index) 
    if frecuencia is None:
        raise ValueError("No se pudo inferir la frecuencia del índice.")
    
    # Asignar nuevas fechas como índice
    nuevasFechas = pd.date_range(start=ultimaFecha, periods=pCantidad_periodos_proyectar + 1, freq=frecuencia)[1:]
    df_predicciones.index = nuevasFechas  
    
    # Concatenar predicciones al DataFrame original
    pDfEstadoResultados = pd.concat([pDfEstadoResultados, df_predicciones], axis=1)
    return pDfEstadoResultados

   
   

        
    
   
    
   
    
    
    