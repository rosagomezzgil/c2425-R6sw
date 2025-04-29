import pandas as pd
from A_extraccion import (
    get_fear_greed_series,
    get_google_trends_series,
    get_binance_ohlcv_series,
    get_binance_futures_series,
    get_yfinance_series,
    get_bitcoin_hashrate_series
)
from datetime import datetime, date


def actualizar_parquet_general(parquet_path: str):
    # 1. Cargar el DataFrame actual
    df_actual = pd.read_parquet(parquet_path)

    # Asegurar que el timestamp es el índice
    if "timestamp" in df_actual.columns:
        df_actual["timestamp"] = pd.to_datetime(df_actual["timestamp"])
        df_actual.set_index("timestamp", inplace=True)

    # 2. Definir rango de fechas para nuevas extracciones
    ultima_fecha = df_actual.index.max()
    hoy = pd.Timestamp(datetime.utcnow().date())

    if ultima_fecha >= hoy:
        print("El DataFrame ya está actualizado.")
        return df_actual

    start_date = ultima_fecha.strftime("%Y-%m-%d")
    end_date = hoy.strftime("%Y-%m-%d")
    dias_a_actualizar = (hoy - ultima_fecha).days

    print(f"Actualizando desde {start_date} hasta {end_date} ({dias_a_actualizar} días)...")

    # 3. Llamar a cada función de extracción
    columnas_nuevas = {}

    try:
        # Fear and Greed
        df_fear = get_fear_greed_series(limit=dias_a_actualizar)
        columnas_nuevas['fear_greed_index_fg'] = df_fear['fear_greed_index']
    except Exception as e:
        print(f"Error actualizando Fear & Greed: {e}")

    try:
        # Google Trends
        timeframe = ajustar_timeframe_google_trends(dias_a_actualizar)
        df_trends = get_google_trends_series(keywords=["bitcoin"], timeframe=timeframe)
        df_trends = df_trends[df_trends.index > ultima_fecha]
        columnas_nuevas['bitcoin_gtrends'] = df_trends['bitcoin']
    except Exception as e:
        print(f"Error actualizando Google Trends: {e}")

    try:
        # Binance Spot OHLCV
        df_binance_spot = get_binance_ohlcv_series(symbol="BTCUSDT", interval="1d", limit=dias_a_actualizar)
        # Guardar cada columna que nos interesa
        for col in ['open', 'high', 'low', 'close', 'volume', 'trades']:
            columnas_nuevas[f'{col}_binance'] = df_binance_spot[col]
    except Exception as e:
        print(f"Error actualizando Binance Spot: {e}")

    try:
        # Binance Futures (solo close también)
        df_binance_futures = get_binance_futures_series(symbol="BTCUSDT", days=dias_a_actualizar, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['open', 'high', 'low', 'close', 'volume', 'trades']:
            columnas_nuevas[f'mD{col}_mDbinance'] = df_binance_futures[col]
    except Exception as e:
        print(f"Error actualizando Binance Futures: {e}")

    try:
        # Yahoo Finance - SP500
        df_sp500 = get_yfinance_series(ticker="^GSPC", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            columnas_nuevas[f'{col}_sp500'] = df_sp500[col].squeeze()
    except Exception as e:
        print(f"Error actualizando SP500: {e}")

    try:
        # Yahoo Finance - Nasdaq
        df_nasdaq  = get_yfinance_series(ticker="^IXIC", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            columnas_nuevas[f'{col}_nasdaq'] = df_nasdaq[col].squeeze()
    except Exception as e:
        print(f"Error actualizando Nasdaq: {e}")

    try:
        # Yahoo Finance - dxy
        df_dxy   = get_yfinance_series(ticker="DX-Y.NYB", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close']:
            columnas_nuevas[f'{col}_dxy'] = df_dxy[col].squeeze()
    except Exception as e:
        print(f"Error actualizando Nasdaq: {e}")

    try:
        # Blockchain.com - Hashrate
        dias_peticion = max(dias_a_actualizar, 2)  # Pedimos mínimo 2 días para evitar error API
        df_hashrate = get_bitcoin_hashrate_series(timespan=f"{dias_peticion}days",rolling_average="24hours")

        # Si originalmente solo queríamos 1 día, recortamos después
        df_hashrate = df_hashrate[df_hashrate.index > ultima_fecha]

        # Guardamos en las columnas nuevas
        columnas_nuevas['hashrate_hashrate'] = df_hashrate['hashrate']
    except Exception as e:
        print(f"Error actualizando Hashrate: {e}")

    # 4. Crear un DataFrame nuevo con todos los datos nuevos
    df_nuevos = pd.DataFrame(columnas_nuevas)
    df_nuevos.index = pd.to_datetime(df_nuevos.index)
    df_nuevos = df_nuevos[~df_nuevos.index.isin(df_actual.index)]  # Evitar duplicados

    if df_nuevos.empty:
        print("No hay datos nuevos que añadir.")
        return df_actual

    # 5. Unir los datos nuevos al DataFrame existente
    df_actualizado = pd.concat([df_actual, df_nuevos])
    for col in df_actualizado.select_dtypes(include="object").columns:
        df_actualizado[col] = pd.to_numeric(df_actualizado[col], errors="coerce")
    df_actualizado.sort_index(inplace=True)

    # 6. Guardar el parquet actualizado
    df_actualizado.to_parquet(parquet_path)
    print(f"Parquet actualizado. Nuevas filas añadidas: {len(df_nuevos)}")

    return df_actualizado

def ajustar_timeframe_google_trends(dias_actualizar: int) -> str:
    """
    Ajusta automáticamente el timeframe para Google Trends,
    garantizando que los datos vengan en formato diario.

    La API no permite hacer solicitudes personalizadas
    """
    if dias_actualizar <= 90:
        return "today 3-m"  # Últimos 3 meses
    elif dias_actualizar <= 365:
        return "today 1-y"  # Último año
    else:
        return "today 5-y"  # Últimos 5 años


if __name__ == "__main__":
    parquet_path = "../data/data.parquet"
    df = actualizar_parquet_general(parquet_path)

