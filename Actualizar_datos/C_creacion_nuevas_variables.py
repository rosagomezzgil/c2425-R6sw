import pandas as pd
import numpy as np

def calcular_rsi(df, columna: str, window: int = 14):
    """
    Calcula el Índice de Fuerza Relativa (RSI) para una serie de precios.

    :param df: DataFrame que contiene los precios del activo.
    :param columna: El nombre de la columna con los precios para el cálculo.
    :param window: Ventana de tiempo para el cálculo del RSI (por defecto 14 días).
    :return: DataFrame con una nueva columna "RSI" que contiene los valores calculados.
    """
    # Crear una copia para evitar SettingWithCopyWarning
    df_copy = df.copy()

    # Calcular la diferencia de precios
    delta = df_copy[columna].diff()

    # Calcular las ganancias y pérdidas
    ganancia = delta.clip(lower=0)
    perdida = -delta.clip(upper=0)

    # Calcular la media móvil exponencial (más precisa para RSI)
    media_ganancia = ganancia.ewm(com=window - 1, adjust=False).mean()
    media_perdida = perdida.ewm(com=window - 1, adjust=False).mean()

    # Evitar divisiones por cero
    rs = np.where(media_perdida != 0, media_ganancia / media_perdida, 100)

    # Calcular el RSI
    rsi = 100 - (100 / (1 + rs))

    # Añadir la columna de RSI al DataFrame
    df_copy["RSI"] = rsi
    return df_copy


def crear_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea variables técnicas adicionales para análisis de precios.

    :param df: DataFrame con datos de precios (debe contener columnas 'timestamp', 'close', 'high', 'low')
    :return: DataFrame con variables técnicas adicionales
    """
    # Crear una copia para evitar modificar el DataFrame original
    df = df.copy()

    # Convertir timestamp a fecha si no es ya un datetime
    if not pd.api.types.is_datetime64_any_dtype(df["timestamp"]):
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Ordenar por fecha
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Variaciones y rangos
    df["var_diaria"] = df["close"].pct_change() * 100  # % de variación

    if "high" in df.columns and "low" in df.columns:
        df["rango_dia"] = df["high"] - df["low"]

    else:
        df["rango_dia"] = df["close"].diff().abs()

    for periodo in [50, 200]:
        # Medidas de volatilidad
        df[f"volatilidad_{periodo}"] = df["close"].rolling(window=periodo).std()

        # Momentum
        df[f"momentum_{periodo}"] = df["close"].pct_change(periods=periodo) * 100


    # Medias móviles
    df = crear_medias_moviles(df, columna='close', ventanas=[50,200])

    # RSI
    df = calcular_rsi(df, "close")

    return df

def crear_medias_moviles(df: pd.DataFrame, columna: str = "close", ventanas: list = [50, 200]) -> pd.DataFrame:
    """
    Crea medias móviles simples (SMA) y exponenciales (EMA) para una columna.

    :param df: DataFrame de entrada.
    :param columna: Nombre de la columna base para calcular las medias.
    :param ventanas: Lista de ventanas de tiempo para calcular las medias.
    :return: DataFrame con nuevas columnas SMA y EMA.
    """

    df = df.copy()

    for d in ventanas:
        df[f"SMA_{d}"] = df[columna].rolling(window=d).mean()
        df[f"EMA_{d}"] = df[columna].ewm(span=d, adjust=False).mean()

    return df


def interpolar_columnas(df: pd.DataFrame, columnas: list) -> pd.DataFrame:
    df = df.copy()
    for col in columnas:
        if col in df.columns:
            df[col] = df[col].interpolate(method='time')
    return df
