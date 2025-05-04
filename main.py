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
from plotly.subplots import make_subplots
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from joblib import load

from G_pipeline import pipeline

app = FastAPI()

# Servir archivos estáticos desde la carpeta 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Generar la gráfica de velas al inicio
def crear_grafica(request: Request = None):
    """
    Crea la gráfica de velas con soporte para filtrado por fechas

    Args:
        request: Objeto Request de FastAPI, opcional. Si se proporciona, se usarán
                sus parámetros query para filtrar por fechas.
    """
    # Cargar los datos del archivo Parquet
    df = pd.read_parquet(r"data\data.parquet")

    # Asegurar que los datos están ordenados por fecha
    df = df.sort_values('timestamp')

    # Filtrar por fechas si se proporcionan en la solicitud
    start_date = None
    end_date = None

    if request and "start" in request.query_params and "end" in request.query_params:
        try:
            start_date = request.query_params.get("start")
            end_date = request.query_params.get("end")

            print(f"Parámetros de fechas recibidos: start={start_date}, end={end_date}")

            # Si las fechas no tienen el formato ISO completo, intentar añadir la parte de tiempo
            if 'T' not in start_date:
                start_date = start_date + 'T00:00:00'
            if 'T' not in end_date:
                end_date = end_date + 'T23:59:59'

            print(f"Fechas formateadas: start={start_date}, end={end_date}")

            # Convertir a datetime para poder filtrar
            try:
                start_date = datetime.fromisoformat(start_date)
                end_date = datetime.fromisoformat(end_date)
            except ValueError as e:
                print(f"Error al convertir fechas con fromisoformat: {e}")
                # Intentar un método alternativo
                start_date = datetime.strptime(start_date.split('T')[0], '%Y-%m-%d')
                end_date = datetime.strptime(end_date.split('T')[0], '%Y-%m-%d')
                # Añadir horas para fin del día si es end_date
                end_date = end_date.replace(hour=23, minute=59, second=59)

            print(f"Objetos datetime creados: start={start_date}, end={end_date}")

            # Filtrar DataFrame
            df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= end_date)]
            print(f"Datos filtrados. Filas restantes: {len(df)}")

            if len(df) == 0:
                print("¡ADVERTENCIA! El filtrado resultó en 0 filas. Usando todos los datos disponibles.")
                df = pd.read_parquet(r"data\data.parquet")
                df = df.sort_values('timestamp')

        except Exception as e:
            print(f"Error al filtrar por fechas: {e}")
            import traceback
            traceback.print_exc()

    # Crear una figura con subplots: gráfica principal y volumen más RSI abajo
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("BTC/USD", "Volumen", "RSI")
    )

    # Añadir las velas a la gráfica principal
    fig.add_trace(
        go.Candlestick(
            x=df['timestamp'],
            open=df['open_binance'],
            high=df['high_binance'],
            low=df['low_binance'],
            close=df['close_binance'],
            name='BTC-USD',
            increasing_line_color='#0bf67e',  # Neon verde para velas alcistas
            decreasing_line_color='#ff5252',  # Rojo para velas bajistas
            increasing_fillcolor='rgba(11, 246, 126, 0.3)',
            decreasing_fillcolor='rgba(255, 82, 82, 0.3)'
        ),
        row=1, col=1
    )

    # Añadir SMA y EMA a la gráfica principal
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['SMA_50_binance'],
            line=dict(color='#00b4ff', width=1.5),  # Neon azul
            name='SMA 50'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['SMA_200_binance'],
            line=dict(color='#7b5dfa', width=1.5),  # Neon púrpura
            name='SMA 200'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['EMA_50_binance'],
            line=dict(color='#ffd700', width=1.5, dash='dot'),  # Dorado punteado
            name='EMA 50'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['EMA_200_binance'],
            line=dict(color='#ff8c00', width=1.5, dash='dot'),  # Naranja punteado
            name='EMA 200'
        ),
        row=1, col=1
    )

    # Añadir Fear & Greed Index como una línea en la gráfica principal
    if 'fear_greed_index_fg' in df.columns:
        # Escalar el índice para que se vea bien en el gráfico
        max_price = df['high_binance'].max()
        min_price = df['low_binance'].min()
        range_price = max_price - min_price

        # Escalar el Fear & Greed Index para que esté en el 20% inferior del gráfico
        scale_factor = range_price * 0.2
        base_level = min_price

        df['fear_greed_scaled'] = base_level + (df['fear_greed_index_fg'] / 100) * scale_factor

        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['fear_greed_scaled'],
                line=dict(color='rgba(255, 255, 255, 0.7)', width=1),
                fill='tozeroy',
                fillcolor='rgba(255, 255, 255, 0.1)',
                name='Fear & Greed',
                hovertemplate='Fear & Greed: %{text}<extra></extra>',
                text=df['fear_greed_index_fg']
            ),
            row=1, col=1
        )

    # Añadir volumen de operaciones en el segundo subplot
    colors = [
        '#0bf67e' if row['close_binance'] >= row['open_binance'] else '#ff5252'
        for _, row in df.iterrows()
    ]

    fig.add_trace(
        go.Bar(
            x=df['timestamp'],
            y=df['volumen_binance'],
            marker_color=colors,
            name='Volumen'
        ),
        row=2, col=1
    )

    # Añadir SMA de volumen
    df['volumen_sma20'] = df['volumen_binance'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['volumen_sma20'],
            line=dict(color='#7b5dfa', width=1.5),
            name='Volumen SMA 20'
        ),
        row=2, col=1
    )

    # Añadir RSI en el tercer subplot
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['RSI_binance'],
            line=dict(color='#00b4ff', width=1.5),
            name='RSI'
        ),
        row=3, col=1
    )

    # Añadir líneas de referencia para RSI
    fig.add_shape(
        type='line',
        x0=df['timestamp'].iloc[0],
        x1=df['timestamp'].iloc[-1],
        y0=70,
        y1=70,
        line=dict(color='rgba(255, 82, 82, 0.5)', width=1, dash='dash'),
        row=3, col=1
    )

    fig.add_shape(
        type='line',
        x0=df['timestamp'].iloc[0],
        x1=df['timestamp'].iloc[-1],
        y0=30,
        y1=30,
        line=dict(color='rgba(11, 246, 126, 0.5)', width=1, dash='dash'),
        row=3, col=1
    )

    # Mejorar el aspecto visual de la gráfica
    fig.update_layout(
        title='Bitcoin (BTC-USD) - Análisis Técnico',
        title_font=dict(size=24, color='white', family='Segoe UI, sans-serif'),
        font=dict(family='Segoe UI, sans-serif', color='white', size=12),

        plot_bgcolor='#1a1d25',  # Fondo oscuro para la gráfica
        paper_bgcolor='#0c0e12',  # Fondo oscuro para el área alrededor de la gráfica

        xaxis=dict(
            gridcolor='rgba(255, 255, 255, 0.1)',
            rangeslider=dict(visible=False),
            showgrid=True
        ),

        yaxis=dict(
            title='Precio (USD)',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True,
            side='right',  # Mover la escala a la derecha como en Binance
            tickformat='$,.0f'  # Formato de precio con $ y sin decimales
        ),

        yaxis2=dict(
            title='Volumen',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True
        ),

        yaxis3=dict(
            title='RSI',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True,
            range=[0, 100]  # El RSI siempre está entre 0 y 100
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0.05,
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.2)'
        ),

        margin=dict(l=10, r=60, t=80, b=10),  # Márgenes ajustados

        hovermode='x unified',
        showlegend=True
    )

    # Añadir anotaciones para niveles actuales
    last_close = df['close_binance'].iloc[-1]
    last_date = df['timestamp'].iloc[-1]

    fig.add_annotation(
        x=last_date,
        y=last_close,
        text=f"${last_close:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#00b4ff",
        arrowsize=1,
        arrowwidth=2,
        ax=50,
        ay=-30,
        font=dict(size=14, color="#ffffff"),
        bgcolor="rgba(0, 180, 255, 0.3)",
        bordercolor="#00b4ff",
        borderwidth=1,
        borderpad=4,
        row=1, col=1
    )

    # Añadir herramientas de crosshair para información precisa al pasar el cursor
    fig.update_xaxes(showspikes=True, spikecolor='white', spikesnap='cursor', spikemode='across')
    fig.update_yaxes(showspikes=True, spikecolor='white', spikethickness=1)

    # Configuración para dispositivos móviles
    fig.update_layout(autosize=True)

    params_string = ""
    if start_date and end_date:
        params_string = f"?start={start_date.isoformat()}&end={end_date.isoformat()}"

    # Guardar la gráfica como archivo HTML con configuración para que coincida con el estilo de la página
    config = {
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'scrollZoom': True,
        'displayModeBar': True,
        'displaylogo': False,
        'responsive': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'bitcoin_chart',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    }

    fig.write_html(
        f"static/grafica_bitcoin.html{params_string}",
        config=config,
        include_plotlyjs=True,
        full_html=True
    )

    print("Gráfica creada con éxito")

@app.on_event("startup")
def startup_event():
    '''Se ejecuta una vez al principio. Lo usamos aunque esté "deprecated" para no usar corrutinas.'''
    # Actualizar datos
    pipeline()

    # Llamar a la función para crear la gráfica al iniciar la app
    crear_grafica()

    # Cargar el modelo como atributo de la aplicación
    app.model7 = load('models/modelo_7d.joblib')
    # app.model30 = load('models/modelo_30d.joblib')

# Modelo para la respuesta de predicción
class BitcoinPrediction(BaseModel):
    current_price: float
    price_7d: float
    price_30d: float
    change_7d: float
    change_30d: float

# Endpoint para obtener el precio actual y predicciones
@app.get("/api/bitcoin/current", response_model=BitcoinPrediction)
def get_current_bitcoin():
    # Cargar los datos del archivo Parquet
    df = pd.read_parquet(r"data/data.parquet")
    pred_7d = pd.read_parquet(r"data/pred_7d.parquet")
    pred_30d = pd.read_parquet(r"data/pred_30d.parquet")

    # Asegurar que los datos están ordenados por fecha
    df = df.sort_values('timestamp')
    pred_7d = pred_7d.sort_values('timestamp')
    pred_30d = pred_30d.sort_values('timestamp')

    # Validar que los últimos timestamps coinciden
    assert df.timestamp.iloc[-1] == pred_7d.timestamp.iloc[-1]
    assert df.timestamp.iloc[-1] == pred_30d.timestamp.iloc[-1]

    # 7 DÍAS
    # Preparar los datos para la predicción
    X_last = pred_7d.drop(columns=['timestamp', 'pct_cambio_7d']).iloc[-1].to_numpy().reshape(1, -1)

    # Predecir el porcentaje de cambio
    change_7d = app.model7.predict(X_last)[0]

    # Calcular el último precio medio
    precio_medio_7d = df['close_binance'].rolling(window=7).mean().iloc[-1]

    # Calcular el precio futuro
    price_7d = precio_medio_7d * (1 + change_7d / 100)

    # 30 DÍAS
    # Preparar los datos para la predicción
    X_last = pred_30d.drop(columns=['timestamp', 'pct_cambio_30d']).iloc[-1].to_numpy().reshape(1, -1)

    # Predecir el porcentaje de cambio
    # change_30d = app.model30.predict(X_last)[0]
    change_30d = 1

    # Calcular el último precio medio
    precio_medio_30d = df['close_binance'].rolling(window=30).mean().iloc[-1]

    # Calcular el precio futuro
    price_30d = precio_medio_30d * (1 + change_30d / 100)

    return BitcoinPrediction(
        current_price=df.close_binance.iloc[-1],
        price_7d=price_7d,
        price_30d=price_30d,
        change_7d=change_7d,
        change_30d=change_30d
    )


# Endpoint para obtener la gráfica filtrada por fechas
@app.get("/static/grafica_bitcoin.html")
async def get_filtered_chart(request: Request):
    # Si se proporcionan parámetros de fecha, crear una nueva gráfica filtrada
    if "start" in request.query_params and "end" in request.query_params:
        crear_grafica(request)

    # Devolver el archivo HTML
    return FileResponse("static/grafica_bitcoin.html")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
