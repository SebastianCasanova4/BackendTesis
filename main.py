import json
from fastapi import FastAPI, File, HTTPException, UploadFile
import pandas as pd
import joblib
from fastapi.middleware.cors import CORSMiddleware
from assets.models.predictionsModel import projection_Balance_General, projection_Estado_Resultados, projection_Flujo_Efectivo
from assets.scripts.dataSeparation_utils import dataSeparation
from assets.scripts.upload_utils import dataUpload
from assets.scripts.dataSetsToJSON import transformDataSetsToJSON
import os



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# # Cargar Modelos
# pipeline_activos = joblib.load('./assets/models/pipeline_model_activos.joblib')
# pipeline_pasivos = joblib.load('./assets/models/pipeline_model_pasivos.joblib')
# pipeline_patrimonio = joblib.load('./assets/models/pipeline_model_patrimonio.joblib')

# # Ruta para la proyección
# @app.get("/proyectar")
# def proyectar_balance():
#     # Cargar y procesar archivo local
#     df = pd.read_excel("Company_financials__1184173-Transformed.xlsx", header=7)
#     df_transposed = df.T
#     df_transposed.columns = df_transposed.iloc[0]
#     df_transposed = df_transposed.drop(df_transposed.index[0])
#     df_transposed.columns = df_transposed.columns.str.strip()

#     # Seleccionar features
#     features_activos = ["Activos no corrientes", "Activos Corrientes"]
#     features_pasivos = ["Pasivos no corrientes", "Pasivos Corrientes"]
#     features_patrimonio = [
#         "Capital Suscrito", "Prima de emisión", "Reserva de revalorización", 
#         "Otras reservas", "Resultados acumulados", "Ganancia o Pérdida del Periodo", 
#         "Otros componentes del patrimonio"
#     ]

#     # Preparar dataframes para predicción
#     df_activos = df_transposed[features_activos].dropna()
#     df_pasivos = df_transposed[features_pasivos].dropna()
#     df_patrimonio = df_transposed[features_patrimonio].fillna(value=0)

#     # Proyección
#     activos_pred = pipeline_activos.predict(df_activos)
#     pasivos_pred = pipeline_pasivos.predict(df_pasivos)
#     patrimonio_pred = pipeline_patrimonio.predict(df_patrimonio)

#     # Retornar resultados
#     return {
#         "Activos proyectados": activos_pred.tolist(),
#         "Pasivos proyectados": pasivos_pred.tolist(),
#         "Patrimonio proyectado": patrimonio_pred.tolist()
#     }

@app.api_route("/upload", methods=["OPTIONS", "POST"])
def upload_file(num_years: str, file: UploadFile = File(...)):
    num_years = int(num_years)
    try:
        response, filename = dataUpload(file)
        filename = file.filename[:-5]
        if os.path.exists(f"./output/{filename+str(num_years)}/"):
            # Leer los archivos JSON y convertirlos a objetos Python
            with open(f"./output/{filename+str(num_years)}/estadoResultados.json", "r") as f:
                jsonEstadoResultados = json.load(f)
            with open(f"./output/{filename+str(num_years)}/balanceGeneral.json", "r") as f:
                jsonBalanceGeneral = json.load(f)
            with open(f"./output/{filename+str(num_years)}/flujoDeCaja.json", "r") as f:
                jsonFlujoDeCaja = json.load(f)
            with open(f"./output/{filename+str(num_years)}/datosEmpresa.json", "r") as f:
                datosEmpresa = json.load(f)

            nombreEmpresa = datosEmpresa["nombreEmpresa"]
            tipoEstadoFinanciero = datosEmpresa["tipoEstadoFinanciero"]
            fechasEmpresa = datosEmpresa["fechas"]

            # Devuelve los datos como respuesta JSON
            return {
                "message": response,
                "fechas": fechasEmpresa,
                "empresa": nombreEmpresa,
                "tipoEstadoFinanciero": tipoEstadoFinanciero,
                "estadoResultados": jsonEstadoResultados,
                "balanceGeneral": jsonBalanceGeneral,
                "flujoDeCaja": jsonFlujoDeCaja
            }

        try:
            dfEstadoResultados, dfBalanceGeneral, dfFlujoEfectivo, NOMBRE_EMPRESA, TIPO_ESTADO_FINANCIERO, fechasPeriodicas = dataSeparation(filename)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al separar los datos: {e}")
        
        try:
            proyeccionEstadoResultados = projection_Estado_Resultados(num_years, dfEstadoResultados)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al proyectar el estado de resultados: {e}")
        resultadosNetosProyectados = proyeccionEstadoResultados["Ganancia (Pérdida) Neta"][-4:]
        
        try:
            proyeccionBalanceGeneral = projection_Balance_General(num_years, dfBalanceGeneral, resultadosNetosProyectados)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al proyectar el balance general: {e}")
        
        try:
            proyeccionFlujoEfectivo = projection_Flujo_Efectivo(num_years, dfFlujoEfectivo)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al proyectar el flujo de efectivo: {e}") 

        # Crear directorio para guardar los archivos
        if not os.path.exists(f"./output/{filename+str(num_years)}/"):
            os.makedirs(f"./output/{filename+str(num_years)}/")

        directorioArchivo = f"./output/{filename+str(num_years)}/"
        listaFechas = list(proyeccionEstadoResultados.index)
        jsonEstadoResultados, jsonBalanceGeneral, jsonFlujoDeCaja = transformDataSetsToJSON(proyeccionEstadoResultados, proyeccionBalanceGeneral, proyeccionFlujoEfectivo, directorioArchivo, nombreEmpresa=NOMBRE_EMPRESA, tipoEstadoFinanciero=TIPO_ESTADO_FINANCIERO, fechas=listaFechas)
        return {"message": response, "fechas": listaFechas, "empresa": NOMBRE_EMPRESA, "tipoEstadoFinanciero": TIPO_ESTADO_FINANCIERO, "estadoResultados": jsonEstadoResultados, "balanceGeneral": jsonBalanceGeneral, "flujoDeCaja": jsonFlujoDeCaja}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {e}")