import pandas as pd
from C_creacion_nuevas_variables import crear_variables, interpolar_columnas, crear_medias_moviles

# Aplicar transformaciones a activos con columnas individuales
def aplicar_transformaciones(df: pd.DataFrame) -> pd.DataFrame:
    """
    Esta función aplica varias transformaciones al DataFrame original:
    1. Interpola valores faltantes en columnas relacionadas con Google Trends, Hashrate, SP500, Nasdaq y DXY.
    2. Calcula nuevas variables financieras (volatilidad, momentum, medias móviles, RSI) para cada activo relevante.
    3. Calcula medias móviles (SMA y EMA) adicionales sobre el hashrate

    Devuelve el DataFrame actualizado.
    """

    df = df.copy()

    columnas_interpolar = [c for c in df.columns if
                           any(prefix in c for prefix in ["gtrends", "hashrate", "sp500", "nasdaq", "dxy"])]
    df = interpolar_columnas(df, columnas_interpolar)

    df.reset_index(inplace=True)

    activos = {
        "binance": ["close_binance", "high_binance", "low_binance"],
        "mDbinance": ["mDclose_mDbinance", "mDhigh_mDbinance", "mDlow_mDbinance"],
        "sp500": ["Close_sp500", "High_sp500", "Low_sp500"],
        "nasdaq": ["Close_nasdaq", "High_nasdaq", "Low_nasdaq"],
        "dxy": ["Close_dxy", "High_dxy", "Low_dxy"],
        "hashrate" : ["hashrate_hashrate"]
    }

    for nombre, columnas in activos.items():
        if all(col in df.columns for col in columnas):
            df_activo = df[["timestamp"] + columnas].copy()

            if nombre == "hashrate":
                df_activo = crear_medias_moviles(df_activo,columna="hashrate_hashrate", ventanas=[50, 200])
            else:
                df_activo.rename(columns={
                    columnas[0]: "close",
                    columnas[1]: "high",
                    columnas[2]: "low"
                }, inplace=True)

                df_activo = crear_variables(df_activo)

            # Añadir columnas de salida renombradas al df original
            for col in df_activo.columns:
                if col not in ["timestamp", "close", "high", "low", "hashrate_hashrate"]:
                    if nombre == "mDbinance":
                        if col == "RSI":
                            nuevo_nombre = f"mD_{col}_{nombre}"
                        else:
                            nuevo_nombre = f"mD{col}_{nombre}"
                    else:
                        nuevo_nombre = f"{col}_{nombre}"
                    df[nuevo_nombre] = df_activo[col]

    return df

if __name__ == "__main__":
    parquet_path = "../data/data.parquet"
    df = pd.read_parquet(parquet_path)
    df = aplicar_transformaciones(df)
    print(df.head())
    print(df.tail())
    df.to_parquet(parquet_path)


