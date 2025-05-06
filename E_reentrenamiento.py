import os
import joblib
import pandas as pd
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from xgboost import XGBRegressor
from statsmodels.tsa.stattools import adfuller


def reentrenar_modelo(tecnica, df):
    os.makedirs("modelos", exist_ok=True)

    if tecnica == "svr":

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        y = df["pct_cambio_7d"]
        X = df.drop(columns=["pct_cambio_7d"])

        # Preprocesamiento
        imputador = SimpleImputer(strategy="mean")
        X_imp = imputador.fit_transform(X)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_imp)

        # Entrenamiento
        best_params_svr = {"kernel": "linear", "epsilon": 0.5, "C": 0.1}
        modelo = SVR(**best_params_svr)
        modelo.fit(X_scaled, y)

        # Guardar modelo y scaler
        joblib.dump(modelo, "models/SVR.joblib")
        joblib.dump(scaler, "models/SVR_scaler.joblib")
        print("SVR reentrenado y guardado.")

    elif tecnica == "xgboost":
        # Preprocesado
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        df = df.groupby(df.index).first()
        df = df.asfreq("D")  # frecuencia diaria

        # Test de estacionariedad
        if adfuller(df["pct_cambio_30d"])[1] > 0.05:
            df["pct_cambio_30d"] = df["pct_cambio_30d"].diff()
            df = df.dropna()

        # Separar la variable respuesta de las predictoras
        y = df["pct_cambio_30d"]
        X = df.drop(columns=["pct_cambio_30d"])

        # Entrenamiento
        best_params_xgb = {
            "colsample_bytree": 0.8,
            "learning_rate": 0.05,
            "max_depth": 2,
            "n_estimators": 100,
            "reg_alpha": 1,
            "reg_lambda": 5,
            "subsample": 0.8,
        }

        modelo = XGBRegressor(**best_params_xgb)
        modelo.fit(X, y)

        # Guardar modelo y scaler
        joblib.dump(modelo, "models/XGB.joblib")
        print("XGBoost reentrenado y guardado.")

    else:
        raise ValueError("Técnica no reconocida: usa 'svr' o 'xgboost'")
