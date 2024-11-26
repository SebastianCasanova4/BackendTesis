from fastapi import FastAPI, File, HTTPException, UploadFile
import pandas as pd
import joblib
from fastapi.middleware.cors import CORSMiddleware
from assets.models.predictionsModel import projection_Estado_Resultados
from assets.scripts.dataSeparation_utils import dataSeparation
from assets.scripts.upload_utils import dataUpload



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar Modelos
pipeline_activos = joblib.load('./assets/models/pipeline_model_activos.joblib')
pipeline_pasivos = joblib.load('./assets/models/pipeline_model_pasivos.joblib')
pipeline_patrimonio = joblib.load('./assets/models/pipeline_model_patrimonio.joblib')

# Ruta para la proyección
@app.get("/proyectar")
def proyectar_balance():
    # Cargar y procesar archivo local
    df = pd.read_excel("Company_financials__1184173-Transformed.xlsx", header=7)
    df_transposed = df.T
    df_transposed.columns = df_transposed.iloc[0]
    df_transposed = df_transposed.drop(df_transposed.index[0])
    df_transposed.columns = df_transposed.columns.str.strip()

    # Seleccionar features
    features_activos = ["Activos no corrientes", "Activos Corrientes"]
    features_pasivos = ["Pasivos no corrientes", "Pasivos Corrientes"]
    features_patrimonio = [
        "Capital Suscrito", "Prima de emisión", "Reserva de revalorización", 
        "Otras reservas", "Resultados acumulados", "Ganancia o Pérdida del Periodo", 
        "Otros componentes del patrimonio"
    ]

    # Preparar dataframes para predicción
    df_activos = df_transposed[features_activos].dropna()
    df_pasivos = df_transposed[features_pasivos].dropna()
    df_patrimonio = df_transposed[features_patrimonio].fillna(value=0)

    # Proyección
    activos_pred = pipeline_activos.predict(df_activos)
    pasivos_pred = pipeline_pasivos.predict(df_pasivos)
    patrimonio_pred = pipeline_patrimonio.predict(df_patrimonio)

    # Retornar resultados
    return {
        "Activos proyectados": activos_pred.tolist(),
        "Pasivos proyectados": pasivos_pred.tolist(),
        "Patrimonio proyectado": patrimonio_pred.tolist()
    }

@app.api_route("/upload", methods=["OPTIONS", "POST"])
def upload_file(file: UploadFile = File(...)):
    try:
        response, filename = dataUpload(file)
        dfEstadoResultados, dfBalanceGeneral, dfFlujoEfectivo, NOMBRE_EMPRESA, TIPO_ESTADO_FINANCIERO, fechasPeriodicas = dataSeparation(filename)
        # exportar el df a excel
        # dfEstadoResultados.to_excel(f"./output/{filename}_EstadoResultados.xlsx")
        proyeccionEstadoResultados = projection_Estado_Resultados(4, dfEstadoResultados)
        filename = filename.split(".")[0]
        proyeccionEstadoResultados.to_excel(f"./output/{filename}_ProyeccionEstadoResultados.xlsx")
        return {"message": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {e}")