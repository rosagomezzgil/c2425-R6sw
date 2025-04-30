import pandas as pd
import requests
import time
from typing import Optional, List
import yfinance as yf
from pytrends.request import TrendReq


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


