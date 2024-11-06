from fastapi import FastAPI
import pandas as pd
import joblib

app = FastAPI()

# Cargar Modelos
pipeline_activos = joblib.load('./assets/pipeline_model_activos.joblib')
pipeline_pasivos = joblib.load('./assets/pipeline_model_pasivos.joblib')
pipeline_patrimonio = joblib.load('./assets/pipeline_model_patrimonio.joblib')

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
