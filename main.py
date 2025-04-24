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

    # Asegurar que los datos están ordenados por fecha
    df = df.sort_values('timestamp')

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
            y=df['volume_binance'],
            marker_color=colors,
            name='Volumen'
        ),
        row=2, col=1
    )

    # Añadir SMA de volumen
    df['volume_sma20'] = df['volume_binance'].rolling(window=20).mean()
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['volume_sma20'],
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

    # Añadir indicadores de tendencia
    if 'tendencia_futura_7d' in df.columns and 'tendencia_futura_30d' in df.columns:
        tend_7d = df['tendencia_futura_7d'].iloc[-1]
        tend_30d = df['tendencia_futura_30d'].iloc[-1]

        tend_text = f"Tendencia 7D: {tend_7d}<br>Tendencia 30D: {tend_30d}"

        fig.add_annotation(
            x=0.85,
            y=0.95,
            xref="paper",
            yref="paper",
            text=tend_text,
            showarrow=False,
            font=dict(size=12, color="#ffffff"),
            bgcolor="rgba(0, 0, 0, 0.5)",
            bordercolor="#00b4ff",
            borderwidth=1,
            borderpad=4,
            align="left"
        )

    # Añadir herramientas avanzadas
    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=[
                dict(count=1, label="1D", step="day", stepmode="backward"),
                dict(count=7, label="1W", step="day", stepmode="backward"),
                dict(count=1, label="1M", step="month", stepmode="backward"),
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(step="all", label="MAX")
            ],
            bgcolor='rgba(0,0,0,0.7)',
            activecolor='#00b4ff'
        ),
        row=1, col=1
    )

    # Añadir herramientas de crosshair para información precisa al pasar el cursor
    fig.update_xaxes(showspikes=True, spikecolor='white', spikesnap='cursor', spikemode='across')
    fig.update_yaxes(showspikes=True, spikecolor='white', spikethickness=1)

    # Configuración para dispositivos móviles
    fig.update_layout(autosize=True)

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
        "static/grafica_bitcoin.html",
        config=config,
        include_plotlyjs=True,
        full_html=True
    )

    return "Gráfica creada con éxito"

# Llamar a la función para crear la gráfica al iniciar la app
crear_grafica()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
