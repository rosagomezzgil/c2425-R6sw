"""
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()  # ← Definición de la app

templates = Jinja2Templates(directory="templates")

@app.get("/form", response_class=HTMLResponse)
def form_get(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/predict-html", response_class=HTMLResponse)
def predict_html(request: Request, x: float = Form(...), y: float = Form(...)):
    resultado = x + y  # Simulación
    return templates.TemplateResponse("form.html", {"request": request, "resultado": resultado})

"""

import pandas as pd
import plotly.graph_objects as go
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Servir archivos estáticos desde la carpeta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Generar la gráfica de velas al inicio
def crear_grafica():
    # Cargar los datos del archivo Parquet
    df = pd.read_parquet(r"C:\Users\Daniel\Universidad\PD\c2425-R6\data\parquet\data.parquet")

    # Crear la gráfica de velas
    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                                        open=df['open_binance'],
                                        high=df['high_binance'],
                                        low=df['low_binance'],
                                        close=df['close_binance'])])

    fig.update_layout(title='Gráfica de Velas de Bitcoin',
                      xaxis_title='Fecha',
                      yaxis_title='Precio (USD)')

    # Guardar la gráfica como archivo HTML
    fig.write_html("static/grafica_bitcoin.html")  # Lo guardas en 'static' para poder acceder a él desde el frontend

# Llamar a la función para crear la gráfica al iniciar la app
crear_grafica()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
