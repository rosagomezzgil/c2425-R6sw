from A_extraccion import actualizar_parquet_general
from B_creacion_nuevas_variables import aplicar_transformaciones
from C_creacion_variables_respuestas import calcular_variables_respuesta
from D_eliminacion_variables import (
    eliminar_variables,
    crear_conjunto_7d,
    crear_conjunto_30d,
)
from E_reentrenamiento import reentrenar_modelo


def pipeline(parquet_path="data/data.parquet"):

    df, actualizado = actualizar_parquet_general(parquet_path)
    if actualizado:
        df = aplicar_transformaciones(df)
        df = calcular_variables_respuesta(df, parquet_path)
        df = eliminar_variables(df)
        df_7d = crear_conjunto_7d(df)
        df_30d = crear_conjunto_30d(df)
        reentrenar_modelo("svr", df_7d)
        reentrenar_modelo("xgboost", df_30d)

    print("Pipeline finished!")


if __name__ == "__main__":

    pipeline()
