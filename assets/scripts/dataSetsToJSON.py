import json

def transformDataSetsToJSON(estadoResultados, balanceGeneral, flujoDeCaja, ruta, nombreEmpresa, tipoEstadoFinanciero):
    # Convertir los DataFrames directamente a JSON
    jsonEstadoResultados = estadoResultados.to_json(orient='records')
    jsonBalanceGeneral = balanceGeneral.to_json(orient='records')
    jsonFlujoDeCaja = flujoDeCaja.to_json(orient='records')
    # Crear el diccionario de datos de la empresa
    datosEmpresa = {"nombreEmpresa": nombreEmpresa, "tipoEstadoFinanciero": tipoEstadoFinanciero}

    # Escribir los archivos JSON en formato correcto
    with open(ruta + 'estadoResultados.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonEstadoResultados), file, ensure_ascii=False, indent=4)
    with open(ruta + 'balanceGeneral.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonBalanceGeneral), file, ensure_ascii=False, indent=4)
    with open(ruta + 'flujoDeCaja.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonFlujoDeCaja), file, ensure_ascii=False, indent=4)
    with open(ruta + 'datosEmpresa.json', 'w', encoding='utf-8') as file:
        json.dump(datosEmpresa, file, ensure_ascii=False, indent=4)

    # Retornar los JSON como diccionarios, no como cadenas de texto
    return json.loads(jsonEstadoResultados), json.loads(jsonBalanceGeneral), json.loads(jsonFlujoDeCaja)
