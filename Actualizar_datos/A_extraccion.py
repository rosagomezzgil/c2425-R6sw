import pandas as pd
import requests
import time
from typing import Optional, List
import yfinance as yf
from pytrends.request import TrendReq
from datetime import datetime

def get_yfinance_series(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    max_retries: int = 5
) -> Optional[pd.DataFrame]:
    """
    Extrae datos de Yahoo Finance de un activo financiero.

    Parámetros:
    - ticker (str): Símbolo del activo en Yahoo Finance.
    - start_date (str): Fecha de inicio en formato "YYYY-MM-DD".
    - end_date (str): Fecha de fin en formato "YYYY-MM-DD".
    - interval (str): Intervalo de datos ('1d', '1h', etc.).
    - max_retries (int): Número máximo de intentos en caso de error.

    Retorna:
    - pd.DataFrame con los datos históricos. Indexado por fecha.
    """

    retries = 0
    while retries < max_retries:
        try:
            df = yf.download(ticker, start=start_date, end=end_date, interval=interval)

            if df.empty:
                raise ValueError(f"No se encontraron datos para {ticker}")

            # Convertir el índice en fecha
            df.index.name = "timestamp"
            df.sort_index(inplace=True)

            return df

        except Exception as e:
            retries += 1
            wait_time = 10 * retries
            print(f"Error descargando {ticker}: {e}. Reintentando en {wait_time} segundos...")
            time.sleep(wait_time)

    raise RuntimeError(f"No se pudo descargar {ticker} después de {max_retries} intentos.")


def get_binance_futures_series(
    symbol: str = "BTCUSDT",
    days: int = 365,
    interval: str = "1h"
) -> pd.DataFrame:
    """
    Extrae datos históricos de Binance Futures (mercado de derivados).

    Parámetros:
    - symbol (str): Par de trading (ej. "BTCUSDT").
    - days (int): Número de días hacia atrás a recuperar.
    - interval (str): Intervalo de las velas ('1m', '5m', '1h', '1d').

    Retorna:
    - pd.DataFrame con columnas: open, high, low, close, volume, trades. Indexado por fecha.
    """

    url = "https://fapi.binance.com/fapi/v1/klines"
    all_data = []
    limit = 1000  # Máximo permitido por Binance
    interval_ms = {
        "1m": 60 * 1000,
        "5m": 5 * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "1h": 60 * 60 * 1000,
        "1d": 24 * 60 * 60 * 1000,
    }[interval]

    end_time = int(time.time() * 1000)
    start_time = end_time - (days * 24 * 60 * 60 * 1000)

    while start_time < end_time:
        params = {
            "symbol": symbol,
            "interval": interval,
            "startTime": start_time,
            "endTime": end_time,
            "limit": limit,
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list):
                print("No se obtuvieron más datos o error en la API.")
                break

            df = pd.DataFrame(
                data,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_asset_volume",
                    "trades",
                    "taker_buy_base",
                    "taker_buy_quote",
                    "ignore",
                ],
            )

            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            df.set_index("timestamp", inplace=True)
            df = df.rename(columns={"volume": "volumen"})

            all_data.append(df[["open", "high", "low", "close", "volumen", "trades"]])

            start_time = int(df.index[-1].timestamp() * 1000) + interval_ms
            time.sleep(0.5)  # Para no saturar la API

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error en la solicitud a Binance Futures: {e}")

    if all_data:
        full_df = pd.concat(all_data)
        full_df.sort_index(inplace=True)
        return full_df
    else:
        raise RuntimeError("No se obtuvieron datos de Binance Futures.")


def get_bitcoin_hashrate_series(
    timespan: str = "all",
    rolling_average: str = "24hours"
) -> pd.DataFrame:
    """
    Extrae el hashrate de Bitcoin desde Blockchain.com.

    Parámetros:
    - timespan (str): Rango de tiempo (ej. "30days", "1year", "all").
    - rolling_average (str): Promedio móvil (ej. "8hours", "24hours").

    Retorna:
    - pd.DataFrame con el hashrate. Indexado por fecha.
    """

    url = f"https://api.blockchain.info/charts/hash-rate?timespan={timespan}&rollingAverage={rolling_average}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data["values"])

        # Procesar DataFrame
        df["timestamp"] = pd.to_datetime(df["x"], unit="s")
        df = df[["timestamp", "y"]].copy()
        df.rename(columns={"y": "hashrate"}, inplace=True)

        df.set_index("timestamp", inplace=True)
        df.sort_index(inplace=True)

        return df

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al obtener datos del hashrate: {e}")

def get_google_trends_series(
    keywords: List[str] = ["bitcoin"],
    timeframe: str = "today 5-y",
    geo: str = ""
) -> pd.DataFrame:
    """
    Extrae datos de Google Trends para las palabras clave especificadas.

    Parámetros:
    - keywords (List[str]): Palabras clave a buscar.
    - timeframe (str): Intervalo de tiempo (por ejemplo, 'today 5-y').
    - geo (str): Código geográfico (ej. 'US', 'ES').

    Retorna:
    - pd.DataFrame con las tendencias de búsqueda. Indexado por fecha.
    """

    pytrends = TrendReq()

    try:
        # Pausa pequeña para evitar bloqueos
        time.sleep(5)
        pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()

        if df.empty:
            raise ValueError("No se recibieron datos de Google Trends.")

        # Mantener solo fecha como índice y las keywords como columnas
        df = df[keywords].copy()
        df.index.name = "timestamp"
        df.sort_index(inplace=True)

        return df

    except (requests.exceptions.RequestException, ValueError) as e:
        raise e

def get_binance_ohlcv_series(
    symbol: str = "BTCUSDT",
    interval: str = "1d",
    limit: int = 1000,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None
) -> pd.DataFrame:
    """
    Extrae datos OHLCV históricos desde Binance.

    Parámetros:
    - symbol (str): Par de trading (ej: 'BTCUSDT').
    - interval (str): Intervalo ('1m', '1h', '1d', etc.).
    - limit (int): Número de registros a obtener.
    - start_time (int, opcional): Timestamp inicial en milisegundos.
    - end_time (int, opcional): Timestamp final en milisegundos.

    Retorna:
    - pd.DataFrame con columnas: open, high, low, close, volume, trades. Indexado por fecha.
    """

    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit,
    }
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(
        data,
        columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ],
    )

    # Procesar el DataFrame
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    numeric_cols = ["open", "high", "low", "close", "volume", "trades"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df = df[["timestamp", "open", "high", "low", "close", "volume", "trades"]].copy()
    df = df.rename(columns={"volume": "volumen"})

    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    return df

def get_fear_greed_series(limit: int = 0, date_format: str = "world") -> pd.DataFrame:
    """
    Extrae el índice de Miedo y Codicia (Fear & Greed Index) desde la API de alternative.me.

    Parámetros:
    - limit (int): Número de registros a obtener (0 para todos).
    - date_format (str): Formato de fecha ('world' o 'us').

    Retorna:
    - pd.DataFrame con 'fear_greed_index' y fecha como índice.
    """

    url = f"https://api.alternative.me/fng/?limit={limit}&format=json&date_format={date_format}"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json().get("data", [])

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(
        df["timestamp"], dayfirst=(date_format == "world"), errors="coerce"
    )

    df = df[["timestamp", "value"]].copy()
    df.rename(columns={"value": "fear_greed_index"}, inplace=True)
    df["fear_greed_index"] = pd.to_numeric(df["fear_greed_index"], errors="coerce")

    df.set_index("timestamp", inplace=True)
    df.sort_index(inplace=True)

    return df


def actualizar_parquet_general(parquet_path: str):
    """
    Actualiza un archivo Parquet con nuevos datos de diversas fuentes financieras.

    Esta función:
    1. Carga un DataFrame histórico desde un archivo Parquet.
    2. Determina cuántos días faltan hasta la fecha actual.
    3. Extrae nuevos datos de múltiples APIs (Yahoo Finance, Binance, Blockchain.com, Google Trends, Alternative).
    4. Filtra las nuevas fechas y evita duplicados.
    5. Combina los datos nuevos con los existentes.
    6. Guarda el DataFrame actualizado en el mismo archivo Parquet.

    :param parquet_path: Ruta al archivo Parquet existente.
    :return: DataFrame actualizado con nuevas filas.
    """

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
        for col in ['open', 'high', 'low', 'close', 'volumen', 'trades']:
            columnas_nuevas[f'{col}_binance'] = df_binance_spot[col]
    except Exception as e:
        print(f"Error actualizando Binance Spot: {e}")

    try:
        # Binance Futures (solo close también)
        df_binance_futures = get_binance_futures_series(symbol="BTCUSDT", days=dias_a_actualizar, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['open', 'high', 'low', 'close', 'volumen', 'trades']:
            columnas_nuevas[f'{col}_mDbinance'] = df_binance_futures[col]
    except Exception as e:
        print(f"Error actualizando Binance Futures: {e}")

    try:
        # Yahoo Finance - SP500
        df_sp500 = get_yfinance_series(ticker="^GSPC", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            columnas_nuevas[f'{col.lower()}_sp500'] = df_sp500[col].squeeze()
    except Exception as e:
        print(f"Error actualizando SP500: {e}")

    try:
        # Yahoo Finance - Nasdaq
        df_nasdaq  = get_yfinance_series(ticker="^IXIC", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            columnas_nuevas[f'{col.lower()}_nasdaq'] = df_nasdaq[col].squeeze()
    except Exception as e:
        print(f"Error actualizando Nasdaq: {e}")

    try:
        # Yahoo Finance - dxy
        df_dxy   = get_yfinance_series(ticker="DX-Y.NYB", start_date=start_date, end_date=end_date, interval="1d")
        # Guardar cada columna que nos interesa
        for col in ['Open', 'High', 'Low', 'Close']:
            columnas_nuevas[f'{col.lower()}_dxy'] = df_dxy[col].squeeze()
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
    #df_actualizado.to_parquet(parquet_path)
    print(f"Parquet actualizado. Nuevas filas añadidas: {len(df_nuevos)}")

    return df_actualizado

#Funcion auxiliar
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
