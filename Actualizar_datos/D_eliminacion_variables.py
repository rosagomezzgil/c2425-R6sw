import pandas as pd

def eliminar_variables(df):

    df = df.copy()
    df.drop(columns=['open_binance', 'high_binance', 'low_binance', 'volumen_binance'], inplace=True)
    df.drop(columns=['SMA_50_binance', 'EMA_200_binance'], inplace=True)
    df.drop(columns=['SMA_50_hashrate', 'EMA_200_hashrate'], inplace=True)
    df.drop(columns=['open_mDbinance','high_mDbinance','low_mDbinance','SMA_50_mDbinance','EMA_200_mDbinance'],inplace=True)
    sufijos = ['_sp500', '_nasdaq', '_dxy']
    columnas = ['open', 'high', 'low', 'SMA_50', 'EMA_200']
    columnas_a_eliminar = [col + suf for col in columnas for suf in sufijos]
    df.drop(columns=columnas_a_eliminar, inplace=True)
    df.drop(columns=['tendencia_futura_7d', 'tendencia_futura_30d'], inplace=True)
    return df

def crear_conjunto_7d(df):

    # Crear df_7d quitando columnas de horizonte 30 días
    df_7d = df.drop(columns=['pct_cambio_30d'])

    # Crear df_pred_7d con las primeras 7 filas
    df_pred_7d = df_7d.tail(7)
    print(df_pred_7d)
    # Guardar en parquet
    df_pred_7d.to_parquet("../data/pred_7d.parquet", index=False)

    # Eliminar filas con NaNs
    df_7d = df_7d.dropna()

    # Guardar df limpio
    output_path = "../data/dataset_7d.parquet"
    df_7d.to_parquet(output_path, index=False)

def crear_conjunto_30d(df):
    # Crear df_30d quitando columnas de horizonte 7 días
    df_30d = df.drop(columns=['pct_cambio_7d'])

    # Crear df_pred_30d con las primeras 30 filas
    df_pred_30d = df_30d.tail(30)
    print(df_pred_30d)

    # Guardar en parquet
    df_pred_30d.to_parquet("../data/pred_30d.parquet", index=False)

    # Eliminar filas con NaNs
    df_30d = df_30d.dropna()

    # Guardar df limpio
    output_path = "../data/dataset_30d.parquet"
    df_30d.to_parquet(output_path, index=False)

"""
if __name__ == "__main__":
    parquet_path = "../data/data.parquet"

    # 1. Cargar el DataFrame existente
    df = pd.read_parquet(parquet_path)

    # 2.Eliminar variables
    df = eliminar_variables(df)

    # 3.Generar el parquet a 7 dias
    crear_conjunto_7d(df)

    # 4.Generar el parquet a 30 dias
    crear_conjunto_30d(df)

"""