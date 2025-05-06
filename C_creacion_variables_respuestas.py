import pandas as pd
from typing import Optional


def calcular_tendencia(
    df: pd.DataFrame,
    horizonte: int,
    threshold: float = 0,
    pct_promedio=False,
    output_path: Optional[str] = None,
):
    """
    Calcula la tendencia futura basada en la variación porcentual del precio medio.

    :param df: (pd.DataFrame) datos de Bitcoin.
    :param horizonte: (int) Número de períodos para calcular la tendencia.
    :param threshold: (float, opcional) Umbral para definir tendencias alcistas/bajistas. Default: 0.
    :param output_path: (str, opcional) Ruta donde guardar el CSV procesado. Default: None
    :return: pd.DataFrame con la tendencia calculada.
    """
    # Crear una copia del DataFrame para no modificar el original
    df_result = df.copy()

    if pct_promedio:
        precio_medio = df["close_binance"].rolling(window=horizonte).mean()
        df_result[f"pct_cambio_{horizonte}d"] = (
            (precio_medio.shift(-horizonte) - precio_medio) / precio_medio * 100
        )

    else:
        # Calcular la variación porcentual futura
        # Usamos el precio actual y el precio futuro después de 'horizonte' días
        future_price = df_result["close_binance"].shift(-horizonte)
        df_result[f"pct_cambio_{horizonte}d"] = (
            (future_price - df_result["close_binance"])
            / df_result["close_binance"]
            * 100
        )

    # Definir la tendencia futura
    df_result[f"tendencia_futura_{horizonte}d"] = 0  # Neutral por defecto
    df_result.loc[
        df_result[f"pct_cambio_{horizonte}d"] > threshold,
        f"tendencia_futura_{horizonte}d",
    ] = 1  # Alcista
    df_result.loc[
        df_result[f"pct_cambio_{horizonte}d"] < -threshold,
        f"tendencia_futura_{horizonte}d",
    ] = -1  # Bajista

    return df_result


def calcular_variables_respuesta(df, parquet_path):
    df = df.copy()
    horizontes = [7, 30]
    for h in horizontes:
        df_tend = calcular_tendencia(df, horizonte=h, pct_promedio=True)
        for col in [f"pct_cambio_{h}d", f"tendencia_futura_{h}d"]:
            df[col] = df_tend[col]

    df.to_parquet(parquet_path)
    return df
