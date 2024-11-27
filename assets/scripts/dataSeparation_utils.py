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

    rubrosBalanceGeneral = [
        "Activos Totales", "Activos no corrientes",
        "Propiedad planta y equipo","Activos intangibles y valor llave", "Comerciales y otras cuentas a cobrar no corrientes",
        "Activos financieros a largo plazo", "Activos diferidos", "Otros activos no corrientes",
        "Activos Corrientes", 
        "Inventarios", "Comerciales y otras cuentas a cobrar", "Pagos anticipados, ingresos devengados y otros activos circulantes diferidos",
        "Activos financieros de corto plazo", "Efectivo o Equivalentes", "Otros Activos Corrientes",
        "Activos del grupo de disposición clasificados como mantenidos para la venta",

        "Total de patrimonio y pasivos", "Total de patrimonio",
        "Capital Suscrito", "Resultados acumulados", "Ganancia o Pérdida del Periodo", "Otro patrimonio",

        "Pasivos Totales", "Pasivos no corrientes",
        "Créditos y préstamos no corrientes", "Otras cuentas por pagar no corrientes",
        "Otros pasivos no corrientes", 
        
        "Pasivos Corrientes"
        "Créditos y préstamos corrientes", "Comerciales y otras cuentas a pagar",
        "Otros pasivos corrientes"
    ]

    for rubro in rubrosBalanceGeneral:
        if rubro not in dfBalanceGeneral:
            dfBalanceGeneral[rubro] = 0
    
    activosTotales = dfBalanceGeneral["Activos Totales"]#T
    activosNoCorrientes = dfBalanceGeneral["Activos no corrientes"]
    propiedadPlantaEquipo = dfBalanceGeneral["Propiedad, planta y equipo"]#& por y
    activosIntangibles = dfBalanceGeneral["Activos intangibles y valor llave"]
    cuentasCobrarNoCorrientes = dfBalanceGeneral["Comerciales y otras cuentas a cobrar no corrientes"]
    activosFinancierosLargoPlazo = dfBalanceGeneral["Activos financieros a largo plazo"]
    activosDiferidos = dfBalanceGeneral["Activos diferidos"]
    otrosActivosNoCorrientes = dfBalanceGeneral["Activos no corrientes"] - propiedadPlantaEquipo - activosIntangibles - cuentasCobrarNoCorrientes - activosFinancierosLargoPlazo - activosDiferidos
    activosCorrientes = dfBalanceGeneral["Activos Corrientes"]#C
    inventarios = dfBalanceGeneral["Inventarios"]
    cuentasCobrar = dfBalanceGeneral["Comerciales y otras cuentas a cobrar"]
    pagosAnticipados = dfBalanceGeneral["Pagos anticipados, ingresos devengados y otros activos circulantes diferidos"]
    activosFinancierosCortoPlazo = dfBalanceGeneral["Activos financieros de corto plazo"]
    efectivoEquivalentes = dfBalanceGeneral["Efectivo o Equivalentes"]
    otrosActivosCorrientes = dfBalanceGeneral["Activos Corrientes"] - inventarios - cuentasCobrar - pagosAnticipados - activosFinancierosCortoPlazo - efectivoEquivalentes

    totalPatrimonioPasivos = dfBalanceGeneral["Total de patrimonio y pasivos"]#de
    totalPatrimonio = dfBalanceGeneral["Total de patrimonio"]
    capitalSuscrito = dfBalanceGeneral["Capital Suscrito"]#S
    resultadosAcumulados = dfBalanceGeneral["Resultados acumulados"]#o
    utilidadPeriodo = dfBalanceGeneral["Ganancia o Pérdida del Periodo"]#Ganancia o Pérdida del Periodo
    otroPatrimonio = dfBalanceGeneral["Total de patrimonio"] - capitalSuscrito - resultadosAcumulados - utilidadPeriodo
    pasivosTotales = dfBalanceGeneral["Pasivos Totales"]#T
    pasivosNoCorrientes = dfBalanceGeneral["Pasivos no corrientes"]
    creditosPrestamosNoCorrientes = dfBalanceGeneral["Créditos y préstamos no corrientes"]
    cuentasPagarNoCorrientes = dfBalanceGeneral["Otras cuentas por pagar no corrientes"]
    otrosPasivosNoCorrientes = dfBalanceGeneral["Pasivos no corrientes"] - creditosPrestamosNoCorrientes - cuentasPagarNoCorrientes
    pasivosCorrientes = dfBalanceGeneral["Pasivos Corrientes"]#C
    creditosPrestamosCorrientes = dfBalanceGeneral["Créditos y préstamos corrientes"]
    cuentasPagar = dfBalanceGeneral["Comerciales y otras cuentas a pagar"]
    otrosPasivosCorrientes = dfBalanceGeneral["Pasivos Corrientes"] - creditosPrestamosCorrientes - cuentasPagar

    dfBalanceGeneralFinal = pd.DataFrame(
        {
            "Activos Totales": activosTotales,
            "Activos No Corrientes": activosNoCorrientes,
            "Propiedad, Planta y Equipo": propiedadPlantaEquipo,
            "Activos Intangibles y Valor Llave": activosIntangibles,
            "Cuentas por Cobrar No Corrientes": cuentasCobrarNoCorrientes,
            "Activos Financieros a Largo Plazo": activosFinancierosLargoPlazo,
            "Activos Diferidos": activosDiferidos,
            "Otros Activos No Corrientes": otrosActivosNoCorrientes,
            "Activos Corrientes": activosCorrientes,
            "Inventarios": inventarios,
            "Cuentas por Cobrar": cuentasCobrar,
            "Pagos Anticipados": pagosAnticipados,
            "Activos Financieros de Corto Plazo": activosFinancierosCortoPlazo,
            "Efectivo o Equivalentes": efectivoEquivalentes,
            "Otros Activos Corrientes": otrosActivosCorrientes,
            "Total de Patrimonio y Pasivos": totalPatrimonioPasivos,
            "Total de Patrimonio": totalPatrimonio,
            "Capital Suscrito": capitalSuscrito,
            "Resultados Acumulados": resultadosAcumulados,
            "Utilidad del Periodo": utilidadPeriodo,
            "Otro Patrimonio": otroPatrimonio,
            "Pasivos Totales": pasivosTotales,
            "Pasivos No Corrientes": pasivosNoCorrientes,
            "Créditos y Préstamos No Corrientes": creditosPrestamosNoCorrientes,
            "Cuentas por Pagar No Corrientes": cuentasPagarNoCorrientes,
            "Otros Pasivos No Corrientes": otrosPasivosNoCorrientes,
            "Pasivos Corrientes": pasivosCorrientes,
            "Créditos y Préstamos Corrientes": creditosPrestamosCorrientes,
            "Cuentas por Pagar": cuentasPagar,
            "Otros Pasivos Corrientes": otrosPasivosCorrientes
        }
    )
    rubrosFlujoDeCaja = [
        "Flujo neto de efectivo por (utilizados en) actividades de explotación",			
                    "Utilidad Neta",			
                    "Efectivo generado por las operaciones",			
                    "Impuesto a las ganancias pagado",			
                    "Otro flujo de efectivo de actividades operativas",			
        "Flujo neto de efectivo de (utilizadas en) actividades de inversión",			
                    "Producto de venta de propiedades, planta y equipo"			
                    "Compra de propiedades, planta y equipo",			
                    "Compra de activos intangibles",			
                    "Compra de propiedades de inversión",
                    "Ingresos por venta de instrumentos financieros",			
                    "Intereses recibidos",
                    "Otros flujos de efectivo de actividades inversión",	
        "Flujo neto de efectivo de (utilizados en) actividades de financiación",            			
                    "Ingresos procedentes de la emisión de acciones ordinarias",			
                    "Ingresos procedentes de la emisión de otros instrumentos de capital",			
                    "Ingresos provenientes de préstamos",			
                    "Reembolso de préstamos",   			
                    "Pagos de las obligaciones de arrendamiento financiero",			
                    "Intereses pagados",			
                    "Dividendos pagados",			
                    "Otros flujos de efectivo de actividades financieras",			
        "Aumento (disminución) neto en efectivo y equivalentes de efectivo",			
        "Efectivo al inicio del período",			
        "Efectivo al final del período",			
        "Flujo de caja libre",			
        "CAPEX"]

    for rubro in rubrosFlujoDeCaja:
        if rubro not in dfFlujoEfectivo:
            dfFlujoEfectivo[rubro] = 0
    
    FlujoNetoEfectivoActividadesExplotacion = dfFlujoEfectivo["Flujo neto de efectivo por (utilizados en) actividades de explotación"]
    UtilidadNeta = dfFlujoEfectivo["Utilidad Neta"]
    EfectivoGeneradoOperaciones = dfFlujoEfectivo["Efectivo generado por las operaciones"]
    ImpuestoGananciasPagado = dfFlujoEfectivo["Impuesto a las ganancias pagado"]
    OtroFlujoEfectivoOperativas = dfFlujoEfectivo["Otro flujo de efectivo de actividades operativas"]
    FlujoNetoEfectivoActividadesInversion = dfFlujoEfectivo["Flujo neto de efectivo de (utilizadas en) actividades de inversión"]
    VentaPropiedades = dfFlujoEfectivo["Producto de venta de propiedades, planta y equipo"]
    CompraPropiedades = dfFlujoEfectivo["Compra de propiedades, planta y equipo"]
    CompraActivosIntangibles = dfFlujoEfectivo["Compra de activos intangibles"]
    CompraPropiedadesInversion = dfFlujoEfectivo["Compra de propiedades de inversión"]
    IngresosVentaInstrumentos = dfFlujoEfectivo["Ingresos por venta de instrumentos financieros"]
    InteresesRecibidos = dfFlujoEfectivo["Intereses recibidos"]
    OtrosFlujosEfectivoInversion = dfFlujoEfectivo["Otros flujos de efectivo de actividades inversión"]
    FlujoNetoEfectivoActividadesFinanciacion = dfFlujoEfectivo["Flujo neto de efectivo de (utilizados en) actividades de financiación"]
    IngresosEmisionAcciones = dfFlujoEfectivo["Ingresos procedentes de la emisión de acciones ordinarias"]
    IngresosEmisionOtrosInstrumentos = dfFlujoEfectivo["Ingresos procedentes de la emisión de otros instrumentos de capital"]
    IngresosProvenientesPrestamos = dfFlujoEfectivo["Ingresos provenientes de préstamos"]
    ReembolsoPrestamos = dfFlujoEfectivo["Reembolso de préstamos"]
    PagosObligacionesArrendamiento = dfFlujoEfectivo["Pagos de las obligaciones de arrendamiento financiero"]
    InteresesPagados = dfFlujoEfectivo["Intereses pagados"]
    DividendosPagados = dfFlujoEfectivo["Dividendos pagados"]
    OtrosFlujosEfectivoFinancieras = dfFlujoEfectivo["Otros flujos de efectivo de actividades financieras"]
    AumentoNetoEfectivo = dfFlujoEfectivo["Aumento (disminución) neto en efectivo y equivalentes de efectivo"]
    EfectivoInicioPeriodo = dfFlujoEfectivo["Efectivo al inicio del período"]
    EfectivoFinalPeriodo = dfFlujoEfectivo["Efectivo al final del período"]
    FlujoCajaLibre = dfFlujoEfectivo["Flujo de caja libre"]
    CAPEX = dfFlujoEfectivo["CAPEX"]

    dfFlujoEfectivoFinal = pd.DataFrame([FlujoNetoEfectivoActividadesExplotacion, UtilidadNeta, EfectivoGeneradoOperaciones, ImpuestoGananciasPagado, OtroFlujoEfectivoOperativas, FlujoNetoEfectivoActividadesInversion, VentaPropiedades, CompraPropiedades, CompraActivosIntangibles, CompraPropiedadesInversion, IngresosVentaInstrumentos, InteresesRecibidos, OtrosFlujosEfectivoInversion, FlujoNetoEfectivoActividadesFinanciacion, IngresosEmisionAcciones, IngresosEmisionOtrosInstrumentos, IngresosProvenientesPrestamos, ReembolsoPrestamos, PagosObligacionesArrendamiento, InteresesPagados, DividendosPagados, OtrosFlujosEfectivoFinancieras, AumentoNetoEfectivo, EfectivoInicioPeriodo, EfectivoFinalPeriodo, FlujoCajaLibre, CAPEX]).T

    

    return dfEstadoResultadosFinal, dfBalanceGeneralFinal, dfFlujoEfectivoFinal, NOMBRE_EMPRESA, TIPO_ESTADO_FINANCIERO, fechasPeriodicas
