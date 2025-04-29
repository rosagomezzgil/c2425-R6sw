import pandas as pd

parquet_path = "../data/data.parquet"
df = pd.read_parquet(parquet_path)
print(df.head())
print(df.tail())
print(df.info())
print(df.describe())
print(df.columns)

columnas_nuevas = ['timestamp', 'open_binance', 'high_binance', 'low_binance',
       'close_binance', 'volume_binance', 'trades_binance', 'volumen_binance',
       'SMA_50_binance', 'SMA_200_binance', 'EMA_50_binance',
       'EMA_200_binance', 'var_diaria_binance', 'volatilidad_50_binance',
       'volatilidad_200_binance', 'rango_dia_binance', 'momentum_50_binance',
       'momentum_200_binance', 'RSI_binance', 'fear_greed_index_fg',
       'bitcoin_gtrends', 'hashrate_hashrate', 'SMA_50_hashrate',
       'SMA_200_hashrate', 'EMA_50_hashrate', 'EMA_200_hashrate',
       'mDopen_mDbinance', 'mDhigh_mDbinance', 'mDlow_mDbinance',
       'mDclose_mDbinance', 'mDvolume_mDbinance', 'mDtrades_mDbinance',
       'mDvar_diaria_mDbinance', 'mDvolatilidad_50_mDbinance',
       'mDvolatilidad_200_mDbinance', 'mDrango_dia_mDbinance',
       'mDmomentum_50_mDbinance', 'mDmomentum_200_mDbinance',
       'mDSMA_50_mDbinance', 'mDSMA_200_mDbinance', 'mDEMA_50_mDbinance',
       'mDEMA_200_mDbinance', 'mD_RSI_mDbinance', 'Close_sp500', 'High_sp500',
       'Low_sp500', 'Open_sp500', 'Volume_sp500', 'SMA_50_sp500',
       'SMA_200_sp500', 'EMA_50_sp500', 'EMA_200_sp500',
       'volatilidad_50_sp500', 'volatilidad_200_sp500', 'momentum_50_sp500',
       'momentum_200_sp500', 'var_diaria_sp500', 'rango_dia_sp500',
       'RSI_sp500', 'Close_nasdaq', 'High_nasdaq', 'Low_nasdaq', 'Open_nasdaq',
       'Volume_nasdaq', 'SMA_50_nasdaq', 'SMA_200_nasdaq', 'EMA_50_nasdaq',
       'EMA_200_nasdaq', 'volatilidad_50_nasdaq', 'volatilidad_200_nasdaq',
       'momentum_50_nasdaq', 'momentum_200_nasdaq', 'var_diaria_nasdaq',
       'rango_dia_nasdaq', 'RSI_nasdaq', 'Close_dxy', 'High_dxy', 'Low_dxy',
       'Open_dxy', 'SMA_50_dxy', 'SMA_200_dxy', 'EMA_50_dxy', 'EMA_200_dxy',
       'volatilidad_50_dxy', 'volatilidad_200_dxy', 'momentum_50_dxy',
       'momentum_200_dxy', 'var_diaria_dxy', 'rango_dia_dxy', 'RSI_dxy',
       'pct_cambio_7d', 'tendencia_futura_7d', 'pct_cambio_30d',
       'tendencia_futura_30d']

columnas = ['timestamp', 'open_binance', 'high_binance', 'low_binance',
       'close_binance', 'volume_binance', 'trades_binance', 'volumen_binance',
       'SMA_50_binance', 'SMA_200_binance', 'EMA_50_binance',
       'EMA_200_binance', 'var_diaria_binance', 'volatilidad_50_binance',
       'volatilidad_200_binance', 'rango_dia_binance', 'momentum_50_binance',
       'momentum_200_binance', 'RSI_binance', 'fear_greed_index_fg',
       'bitcoin_gtrends', 'hashrate_hashrate', 'SMA_50_hashrate',
       'SMA_200_hashrate', 'EMA_50_hashrate', 'EMA_200_hashrate',
       'mDopen_mDbinance', 'mDhigh_mDbinance', 'mDlow_mDbinance',
       'mDclose_mDbinance', 'mDvolume_mDbinance', 'mDtrades_mDbinance',
       'mDvar_diaria_mDbinance', 'mDvolatilidad_50_mDbinance',
       'mDvolatilidad_200_mDbinance', 'mDrango_dia_mDbinance',
       'mDmomentum_50_mDbinance', 'mDmomentum_200_mDbinance',
       'mDSMA_50_mDbinance', 'mDSMA_200_mDbinance', 'mDEMA_50_mDbinance',
       'mDEMA_200_mDbinance', 'mD_RSI_mDbinance', 'Close_sp500', 'High_sp500',
       'Low_sp500', 'Open_sp500', 'Volume_sp500', 'SMA_50_sp500',
       'SMA_200_sp500', 'EMA_50_sp500', 'EMA_200_sp500',
       'volatilidad_50_sp500', 'volatilidad_200_sp500', 'momentum_50_sp500',
       'momentum_200_sp500', 'var_diaria_sp500', 'rango_dia_sp500',
       'RSI_sp500', 'Close_nasdaq', 'High_nasdaq', 'Low_nasdaq', 'Open_nasdaq',
       'Volume_nasdaq', 'SMA_50_nasdaq', 'SMA_200_nasdaq', 'EMA_50_nasdaq',
       'EMA_200_nasdaq', 'volatilidad_50_nasdaq', 'volatilidad_200_nasdaq',
       'momentum_50_nasdaq', 'momentum_200_nasdaq', 'var_diaria_nasdaq',
       'rango_dia_nasdaq', 'RSI_nasdaq', 'Close_dxy', 'High_dxy', 'Low_dxy',
       'Open_dxy', 'SMA_50_dxy', 'SMA_200_dxy', 'EMA_50_dxy', 'EMA_200_dxy',
       'volatilidad_50_dxy', 'volatilidad_200_dxy', 'momentum_50_dxy',
       'momentum_200_dxy', 'var_diaria_dxy', 'rango_dia_dxy', 'RSI_dxy',
       'pct_cambio_7d', 'tendencia_futura_7d', 'pct_cambio_30d',
       'tendencia_futura_30d']

for col in columnas_nuevas:
    if col not in columnas:
        print(col)
