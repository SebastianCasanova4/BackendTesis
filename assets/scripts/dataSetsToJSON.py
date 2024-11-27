import json

def transformDataSetsToJSON(estadoResultados, balanceGeneral, flujoDeCaja, ruta, nombreEmpresa, tipoEstadoFinanciero):
    jsonEstadoResultados = estadoResultados.to_json(orient='records')
    jsonBalanceGeneral = balanceGeneral.to_json(orient='records')
    jsonFlujoDeCaja = flujoDeCaja.to_json(orient='records')
    datosEmpresa = {"nombreEmpresa": nombreEmpresa, "tipoEstadoFinanciero": tipoEstadoFinanciero}
    json.dumps(datosEmpresa, ensure_ascii=False)

    # Escribir los archivos JSON con encoding UTF-8 y force_ascii=False
    with open(ruta + 'estadoResultados.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonEstadoResultados), file, ensure_ascii=False, indent=4)
    with open(ruta + 'balanceGeneral.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonBalanceGeneral), file, ensure_ascii=False, indent=4)
    with open(ruta + 'flujoDeCaja.json', 'w', encoding='utf-8') as file:
        json.dump(json.loads(jsonFlujoDeCaja), file, ensure_ascii=False, indent=4)
    with open(ruta + 'datosEmpresa.json', 'w', encoding='utf-8') as file:
        json.dump(datosEmpresa, file, ensure_ascii=False, indent=4)

    # retornar los json
    return jsonEstadoResultados, jsonBalanceGeneral, jsonFlujoDeCaja