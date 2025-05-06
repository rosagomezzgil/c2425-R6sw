# CryptoVision Insights
![LOGO](https://img.bitgetimg.com/multiLang/web/ebb606b3d63bb1f7d48e7ccdfbb984c1.png)

# Estructura del repositorio.
```bash
├── data/ # Conjuntos de datos en formato .parquet
├── modelos/ # Modelos entrenados en formato .joblib
├── models/ # Alternativa de carpeta para modelos
├── static/ # Archivos estáticos (CSS, JS, imágenes)
├── templates/ # Plantillas HTML para la web
├── .venv/ # Entorno virtual de Python
├── A_extraccion.py # Script de extracción de datos
├── B_creacion_nuevas_variables.py
├── C_creacion_variables_respuestas.py
├── D_eliminacion_variables.py
├── E_reentrenamiento.py
├── G_pipeline.py
├── main.py # Archivo principal para iniciar el servidor FastAPI
├── Dockerfile # Configuración de Docker
├── pyproject.toml # Dependencias del proyecto
├── README.md
```
# Instrucciones para iniciar el entorno de desarrollo con sus dependencias.
```bash
uv sync
```
# Instrucciones para ejecutar ejecutar y probar el servidor web.
```bash
uv run fastapi dev
```
# Instrucciones para crear la imagen docker y ejecutar el contenedor.
```bash
docker build --tag webapp .
docker run -d -p 8000:8000 --name webapp1 webapp
```
# Equipo de desarrollo.
Rodrigo Jesús-Portanet
Pablo Alonso
Rosa Gómez-Gil
Ignacio Ramírez
Daniel Higueras
Vega García





