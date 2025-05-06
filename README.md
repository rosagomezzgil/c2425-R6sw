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
# Comportamientos conflictivos en la extracción de datos
- Puede llegar a darse el caso de que surja un error en la extracción de datos debido a que se haya alcanzado el límite de extracción de datos de la API de Yahoo Finance.
El código intenta extraer los datos hasta 5 veces, dejando un intervalo de tiempo entre cada intento. Una vez completados esos intentos, el resto de la ejecución debería continuar con normalidad.
El proceso puede llegar a tardar unos 2 minutos, pero después todo debería funcionar correctamente.

# Instrucciones para iniciar el entorno de desarrollo con sus dependencias.
El proyecto requiere las siguientes librerías (ver también `pyproject.toml`):

```bash
fastapi[standard]>=0.115.12
jinja2>=3.1.6
joblib>=1.5.0
pandas>=2.2.3
plotly>=6.0.1
pyarrow>=19.0.1
pydantic>=2.11.3
python-multipart>=0.0.20
pytrends>=4.9.2
requests>=2.32.3
scikit-learn>=1.6.1
statsmodels>=0.14.4
xgboost>=3.0.0
yfinance>=0.2.57
```

Puedes instalarlas todas haciendo el siguiente código desde la terminal:
```bash
uv sync
```
# Instrucciones para ejecutar ejecutar y probar el servidor web.
1. Primero situarse en la carpeta del proyecto (c2425-R6sw).


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





