import pandas as pd

def eliminar_variables(df):

    df = df.copy()
    df.drop(columns=['open_binance', 'high_binance', 'low_binance', 'volumen_binance'], inplace=True)
    df.drop(columns=['SMA_50_binance', 'EMA_200_binance'], inplace=True)
    df.drop(columns=['SMA_50_hashrate', 'EMA_200_hashrate'], inplace=True, errors='ignore')
    df.drop(columns=['open_mDbinance','high_mDbinance','low_mDbinance','SMA_50_mDbinance','EMA_200_mDbinance'],inplace=True, errors='ignore')
    sufijos = ['_sp500', '_nasdaq', '_dxy']
    columnas = ['open', 'high', 'low', 'SMA_50', 'EMA_200']
    columnas_a_eliminar = [col + suf for col in columnas for suf in sufijos]
    df.drop(columns=columnas_a_eliminar, inplace=True, errors='ignore')
    df.drop(columns=['tendencia_futura_7d', 'tendencia_futura_30d'], inplace=True, errors='ignore')
    return df

def crear_conjunto_7d(df):

    # Crear df_7d quitando columnas de horizonte 30 días
    columnas_SVR = ['timestamp'] + \
                    ['SMA_200_dxy', 'volatilidad_200_sp500', 'EMA_50_hashrate',
                     'SMA_200_nasdaq', 'SMA_200_hashrate', 'bitcoin_gtrends',
                     'EMA_50_mDbinance', 'SMA_200_sp500', 'EMA_50_binance', 'EMA_50_sp500',
                     'close_nasdaq', 'volatilidad_200_binance', 'volatilidad_200_mDbinance',
                     'volatilidad_50_binance', 'volatilidad_50_mDbinance'] \
        + ['pct_cambio_7d']

    df_7d = df[columnas_SVR]

    # Crear df_pred_7d con las primeras 7 filas
    df_pred_7d = df_7d.tail(7)

    # Guardar en parquet
    df_pred_7d.to_parquet("data/pred_7d.parquet", index=False)

    # Eliminar filas con NaNs
    df_7d = df_7d.dropna()

    # Guardar df limpio
    df_7d.to_parquet("data/dataset_7d.parquet", index=False)

def crear_conjunto_30d(df):
    # Crear df_30d quitando columnas de horizonte 7 días
    columnas_XGBoost = ['timestamp'] + \
           ['close_binance', 'trades_binance', 'var_diaria_binance',
            'rango_dia_binance', 'volatilidad_50_binance', 'momentum_50_binance',
            'volatilidad_200_binance', 'momentum_200_binance', 'EMA_50_binance',
            'SMA_200_binance', 'RSI_binance', 'fear_greed_index_fg',
            'bitcoin_gtrends', 'hashrate_hashrate', 'SMA_200_hashrate',
            'EMA_50_hashrate', 'close_mDbinance', 'volumen_mDbinance',
            'trades_mDbinance', 'var_diaria_mDbinance', 'rango_dia_mDbinance',
            'volatilidad_50_mDbinance', 'momentum_50_mDbinance',
            'volatilidad_200_mDbinance', 'momentum_200_mDbinance',
            'EMA_50_mDbinance', 'SMA_200_mDbinance', 'RSI_mDbinance', 'close_sp500',
            'volume_sp500', 'var_diaria_sp500', 'rango_dia_sp500',
            'volatilidad_50_sp500', 'momentum_50_sp500', 'volatilidad_200_sp500',
            'momentum_200_sp500', 'EMA_50_sp500', 'SMA_200_sp500', 'RSI_sp500',
            'close_nasdaq', 'volume_nasdaq', 'var_diaria_nasdaq',
            'rango_dia_nasdaq', 'volatilidad_50_nasdaq', 'momentum_50_nasdaq',
            'volatilidad_200_nasdaq', 'momentum_200_nasdaq', 'EMA_50_nasdaq',
            'SMA_200_nasdaq', 'RSI_nasdaq', 'close_dxy', 'var_diaria_dxy',
            'rango_dia_dxy', 'volatilidad_50_dxy', 'momentum_50_dxy',
            'volatilidad_200_dxy', 'momentum_200_dxy', 'EMA_50_dxy', 'SMA_200_dxy',
            'RSI_dxy'] + \
        ['pct_cambio_30d']

    df_30d = df[columnas_XGBoost]

    # Crear df_pred_30d con las primeras 30 filas
    df_pred_30d = df_30d.tail(30)

    # Guardar en parquet
    df_pred_30d.to_parquet("data/pred_30d.parquet", index=False)

    # Eliminar filas con NaNs
    df_30d = df_30d.dropna()

    # Guardar df limpio
    df_30d.to_parquet("data/dataset_30d.parquet", index=False)