# CryptoVision Insights
![LOGO](https://img.bitgetimg.com/multiLang/web/ebb606b3d63bb1f7d48e7ccdfbb984c1.png)

# Estructura del repositorio.
```bash
├── data/ # Conjuntos de datos en formato .parquet
│     ├── data.parquet
│     ├── dataset_7d.parquet
│     ├── dataset_30d.parquet
│     ├── pred_7d.parquet
│     └── pred_30d.parquet
│
├── modelos/ # Modelos entrenados en formato .joblib
│     ├── SVR.joblib
│     ├── SVR_scaler.joblib
│     └── XGB.joblib
│      
├── models/ # Alternativa de carpeta para modelos
│     ├── SVR.joblib
│     ├── SVR_scaler.joblib
│     ├── XGB.joblib
│     └── XGB_scaler.joblib
│
├── static/ # Archivos estáticos (CSS, JS, imágenes)
│     ├── css # Archivo para tocar el diseño de la web
│     │     └── styles.css         
│     ├── img # Imágenes que hay en la web
│     │     ├── icon_app.png
│     │     ├── icon_ballena.png
│     │     ├── icon_bitcoin.png
│     │     ├── icon_eiffel.png
│     │     ├── icon_flower.png
│     │     ├── icon_fox.png
│     │     ├── icon_rombo.png
│     │     └── icon_sun.png
│     ├── js # Contiene el main.js
│     │     └── main.js     
│     └── grafica_bitocin.html # HTML para la gráfica
│       
├── templates/ # Plantillas HTML para la web
│     ├── form.html
│     └── index.html
│     
├── .venv/ # Entorno virtual de Python
├── A_extraccion.py # Script de extracción de datos
├── B_creacion_nuevas_variables.py # Script de creacion de variables
├── C_creacion_variables_respuestas.py # Script de creacion de variables respuestas
├── D_eliminacion_variables.py # Script de eliminacion de variables
├── E_reentrenamiento.py # Script de reentrenamiento de modelos
├── G_pipeline.py # Script del pipeline (flujo) 
├── main.py # Archivo principal para iniciar el servidor FastAPI
├── Dockerfile # Configuración de Docker
├── pyproject.toml # Dependencias del proyecto
└── README.md # (Este archivo)
```
# Instrucciones para iniciar el entorno de desarrollo con sus dependencias.
```bash
uv sync
```
# Instrucciones para ejecutar ejecutar y probar el servidor web.
1. Primero situarse en la carpeta del proyecto.


2. Ejecutar el siguiente código:
```bash
uv run fastapi dev
```
# Instrucciones para crear la imagen docker y ejecutar el contenedor.
```bash
docker build --tag webapp .
docker run -d -p 8000:8000 --name webapp1 webapp
```
# Equipo de desarrollo.
Rodrigo Jesús-Portanet,
Pablo Alonso,
Rosa Gómez-Gil,
Ignacio Ramírez,
Daniel Higueras y
Vega García.





