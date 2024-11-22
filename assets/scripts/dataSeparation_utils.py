import pandas as pd
def dataSeparation(filename):
    file = pd.read_excel(f"./uploads/{filename}", header=5)
    NOMBRE_EMPRESA = file.columns[0]
    #Extraemos el tipo de estado financiero, corresponde a la periodicidad este rubro.
    TIPO_ESTADO_FINANCIERO = file.iloc[1,1]
    #Extraemos la fecha final del periodo para poder obtener las fechas facilmente.
    fechasFinalPeriodo = file.iloc[2,1:].tolist()
    #Limpiamos los formatos con cadenas de texto para que queden sin espacios.
    file.iloc[:,0] = file.iloc[:,0].str.strip()
    #Extraemos los indices de los diferentes estados financieros que tenemos en nuestro documento para separarlos.
    indiceEstadoResultados = file[file.iloc[:, 0] == 'Estado de Resultados'].index[0]
    indiceBalanceGeneral = file[file.iloc[:, 0] == 'Balance General'].index[0]
    indiceEstadosFlujoEfectivo = file[file.iloc[:, 0] == 'Estado de Flujo de Efectivo'].index[0]
    #Para este dfEstadoResultados set es necesario borrar todas las filas al final que sean nulas.
    indiceResiduos = file.iloc[indiceEstadosFlujoEfectivo:,0].isna().idxmax()
    #Separamos el dataSet de estado de Resultados
    dfEstadoResultados = file.iloc[indiceEstadoResultados: indiceBalanceGeneral - 1,:]
    #Separamos el dataSet de Balance General
    dfBalanceGeneral = file.iloc[indiceBalanceGeneral: indiceEstadosFlujoEfectivo - 1,:]
    #Separamos el dataSet de Estado de Flujo de Efectivo
    dfFlujoEfectivo = file.iloc[indiceEstadosFlujoEfectivo: indiceResiduos ,:]
    # Se transpone el dfEstadoResultados set para que quede en formato de columnas correcto.
    dfEstadoResultados = dfEstadoResultados.T
    dfBalanceGeneral = dfBalanceGeneral.T
    dfFlujoEfectivo = dfFlujoEfectivo.T
    #Ajustamos los nombres de las columnas para los dataSets para que no sean numericos sino los rubros_estadoResultados.
    dfEstadoResultados.columns = dfEstadoResultados.iloc[0]
    dfBalanceGeneral.columns = dfBalanceGeneral.iloc[0]
    dfFlujoEfectivo.columns = dfFlujoEfectivo.iloc[0]
    # Elimimanomos la fila que contenia los rubros_estadoResultados
    dfEstadoResultados = dfEstadoResultados.drop(dfEstadoResultados.index[0])
    dfBalanceGeneral = dfBalanceGeneral.drop(dfBalanceGeneral.index[0])
    dfFlujoEfectivo = dfFlujoEfectivo.drop(dfFlujoEfectivo.index[0])
    # convertir las fechas a datetime
    fechas= pd.to_datetime(fechasFinalPeriodo)
    # Convertir las fechas a un DatetimeIndex
    fechasPeriodicas = pd.DatetimeIndex(fechas)
    # Establecer la frecuencia trimestral con fin en diciembre (Q-DEC)
    fechasPeriodicas = pd.DatetimeIndex(fechasPeriodicas).to_period('Q-DEC')
    #Establecemos las fechas como indice
    dfEstadoResultados.set_index(fechas, inplace=True)
    dfEstadoResultados= dfEstadoResultados.drop(dfEstadoResultados.columns[0], axis=1)
    #Ordenamos el dataSet por fecha de manera ascendente
    dfEstadoResultados.sort_index(inplace=True)
    #Establecemos las fechas como indice
    dfBalanceGeneral.set_index(fechas, inplace=True)
    dfBalanceGeneral= dfBalanceGeneral.drop(dfBalanceGeneral.columns[0], axis=1)
    #Ordenamos el dataSet por fecha de manera ascendente
    dfBalanceGeneral.sort_index(inplace=True)
    #Establecemos las fechas como indice
    dfFlujoEfectivo.set_index(fechas, inplace=True)
    dfFlujoEfectivo= dfFlujoEfectivo.drop(dfFlujoEfectivo.columns[0], axis=1)
    #Ordenamos el dataSet por fecha de manera ascendente
    dfFlujoEfectivo.sort_index(inplace=True)
    #Remplazar los nulos por 0
    dfEstadoResultados.fillna(0, inplace=True)
    dfBalanceGeneral.fillna(0, inplace=True)
    dfFlujoEfectivo.fillna(0, inplace=True)

    rubros_estadoResultados = ["Ingresos netos por ventas", "Costo de mercancías vendidas", "Utilidad bruta", "Gastos de venta y distribución", "Gastos administrativos", "Gastos de depreciación, amortización y deterioro", "Otros resultados operativos netos", "Ganancia operativa (EBIT)", "Resultado financiero", "Otros resultados no operativos netos", "Monto de Pérdidas o Ganancias Extraordinarias", "Ganancias antes de impuestos", "Impuesto a la renta", "Ganancia (Pérdida) Neta"]

    for rubro in rubros_estadoResultados:
        if rubro not in dfEstadoResultados:
            dfEstadoResultados[rubro] = 0


    ventas = dfEstadoResultados["Ingresos netos por ventas"]
    costo_ventas = dfEstadoResultados["Costo de mercancías vendidas"]
    utilidadBruta = dfEstadoResultados["Utilidad bruta"]
    gastosVentaDistribucion = dfEstadoResultados["Gastos de venta y distribución"]
    gastosAdministrativos = dfEstadoResultados["Gastos administrativos"]
    depreciacionAmortizacion = dfEstadoResultados["Gastos de depreciación, amortización y deterioro"]
    otrosResultadosOperativos = dfEstadoResultados["Otros resultados operativos netos"]
    EBIT = dfEstadoResultados["Ganancia operativa (EBIT)"]
    resultadoFinanciero = dfEstadoResultados["Resultado financiero"]
    resultadosNoOperativos = dfEstadoResultados["Otros resultados no operativos netos"]
    perdidasGananciasExtraordinarias = dfEstadoResultados["Monto de Pérdidas o Ganancias Extraordinarias"]
    utilidadAntesDeImpuestos = dfEstadoResultados["Ganancias antes de impuestos"]
    impuesto = dfEstadoResultados["Impuesto a la renta"]
    utilidadNeta = dfEstadoResultados["Ganancia (Pérdida) Neta"]
    dfEstadoResultadosFinal = pd.DataFrame([ventas,costo_ventas,utilidadBruta,gastosVentaDistribucion,gastosAdministrativos,depreciacionAmortizacion,otrosResultadosOperativos,EBIT,resultadoFinanciero,resultadosNoOperativos,perdidasGananciasExtraordinarias,utilidadAntesDeImpuestos,impuesto,utilidadNeta],index=["Ventas","Costo de ventas","Utilidad Bruta","Gastos de venta y distribución","Gastos administrativos","Gastos de depreciación, amortización y deterioro","Otros resultados operativos netos","Ganancia operativa (EBIT)","Resultado financiero","Otros resultados no operativos netos","Monto de Pérdidas o Ganancias Extraordinarias","Ganancias antes de impuestos","Impuesto a la renta","Ganancia (Pérdida) Neta"]).T



    

    return dfEstadoResultadosFinal, dfBalanceGeneral, dfFlujoEfectivo, NOMBRE_EMPRESA, TIPO_ESTADO_FINANCIERO, fechasPeriodicas
