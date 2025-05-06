"""
API de Predicción de Precio de Bitcoin y Análisis Técnico

Esta aplicación basada en FastAPI proporciona una API para la predicción del precio
de Bitcoin y el análisis técnico. Utiliza modelos de aprendizaje automático,
específicamente SVR (Regresión por Vectores de Soporte) y XGBoost, para predecir
los precios de Bitcoin para los próximos 7 y 30 días. La aplicación también genera
gráficos en tiempo real con los datos del mercado de Bitcoin, incluyendo gráficos
de velas, volumen y RSI (Índice de Fuerza Relativa).
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from joblib import load
import numpy as np
import os
import traceback
from pathlib import Path
from typing import Optional

from G_pipeline import pipeline

app = FastAPI(
    title="Bitcoin Price Prediction API",
    description="API for Bitcoin price prediction and technical analysis",
    version="1.0.0",
)

# Serve static files from the 'static' folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Data paths
DATA_PATH = Path("data/data.parquet")
PRED_7D_PATH = Path("data/pred_7d.parquet")
PRED_30D_PATH = Path("data/pred_30d.parquet")
CHART_PATH = Path("static/grafica_bitcoin.html")


# Model for SVR input
class SVRinput(BaseModel):
    timestamp: str
    SMA_200_dxy: float
    volatilidad_200_sp500: float
    EMA_50_hashrate: float
    SMA_200_nasdaq: float
    SMA_200_hashrate: float
    bitcoin_gtrends: float
    EMA_50_mDbinance: float
    SMA_200_sp500: float
    EMA_50_binance: float
    EMA_50_sp500: float
    close_nasdaq: float
    volatilidad_200_binance: float
    volatilidad_200_mDbinance: float
    volatilidad_50_binance: float
    volatilidad_50_mDbinance: float


# Model for XGBoost input
class XGBinput(BaseModel):
    timestamp: str
    close_binance: float
    trades_binance: float
    var_diaria_binance: float
    rango_dia_binance: float
    volatilidad_50_binance: float
    momentum_50_binance: float
    volatilidad_200_binance: float
    momentum_200_binance: float
    EMA_50_binance: float
    SMA_200_binance: float
    RSI_binance: float
    fear_greed_index_fg: float
    bitcoin_gtrends: float
    hashrate_hashrate: float
    SMA_200_hashrate: float
    EMA_50_hashrate: float
    close_mDbinance: float
    volumen_mDbinance: float
    trades_mDbinance: float
    var_diaria_mDbinance: float
    rango_dia_mDbinance: float
    volatilidad_50_mDbinance: float
    momentum_50_mDbinance: float
    volatilidad_200_mDbinance: float
    momentum_200_mDbinance: float
    EMA_50_mDbinance: float
    SMA_200_mDbinance: float
    RSI_mDbinance: float
    close_sp500: float
    volume_sp500: float
    var_diaria_sp500: float
    rango_dia_sp500: float
    volatilidad_50_sp500: float
    momentum_50_sp500: float
    volatilidad_200_sp500: float
    momentum_200_sp500: float
    EMA_50_sp500: float
    SMA_200_sp500: float
    RSI_sp500: float
    close_nasdaq: float
    volume_nasdaq: float
    var_diaria_nasdaq: float
    rango_dia_nasdaq: float
    volatilidad_50_nasdaq: float
    momentum_50_nasdaq: float
    volatilidad_200_nasdaq: float
    momentum_200_nasdaq: float
    EMA_50_nasdaq: float
    SMA_200_nasdaq: float
    RSI_nasdaq: float
    close_dxy: float
    var_diaria_dxy: float
    rango_dia_dxy: float
    volatilidad_50_dxy: float
    momentum_50_dxy: float
    volatilidad_200_dxy: float
    momentum_200_dxy: float
    EMA_50_dxy: float
    SMA_200_dxy: float
    RSI_dxy: float


# Model for prediction model
class ModelPrediction(BaseModel):
    pct_change: float


# Model for prediction response
class BitcoinPrediction(BaseModel):
    current_price: float
    price_7d: float
    price_30d: float
    change_7d: float
    change_30d: float
    prediction_date: Optional[str] = None


# SVR predictions
def SVRprediction(input: SVRinput):
    try:
        # Extraer todos los campos excepto timestamp en el orden correcto
        features = [
            input.SMA_200_dxy,
            input.volatilidad_200_sp500,
            input.EMA_50_hashrate,
            input.SMA_200_nasdaq,
            input.SMA_200_hashrate,
            input.bitcoin_gtrends,
            input.EMA_50_mDbinance,
            input.SMA_200_sp500,
            input.EMA_50_binance,
            input.EMA_50_sp500,
            input.close_nasdaq,
            input.volatilidad_200_binance,
            input.volatilidad_200_mDbinance,
            input.volatilidad_50_binance,
            input.volatilidad_50_mDbinance,
        ]

        # Convertir a numpy array y reshape para el modelo
        X = np.array(features).reshape(1, -1)

        # Hacer la predicción
        prediction = app.model7.predict(X)[0]

        return prediction
    except Exception as e:
        print(f"Error en la predicción SVR: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error en la predicción")


def XGBprediction(input: XGBinput):
    try:
        # Extraer todos los campos excepto timestamp en el orden correcto
        features = [
            input.close_binance,
            input.trades_binance,
            input.var_diaria_binance,
            input.rango_dia_binance,
            input.volatilidad_50_binance,
            input.momentum_50_binance,
            input.volatilidad_200_binance,
            input.momentum_200_binance,
            input.EMA_50_binance,
            input.SMA_200_binance,
            input.RSI_binance,
            input.fear_greed_index_fg,
            input.bitcoin_gtrends,
            input.hashrate_hashrate,
            input.SMA_200_hashrate,
            input.EMA_50_hashrate,
            input.close_mDbinance,
            input.volumen_mDbinance,
            input.trades_mDbinance,
            input.var_diaria_mDbinance,
            input.rango_dia_mDbinance,
            input.volatilidad_50_mDbinance,
            input.momentum_50_mDbinance,
            input.volatilidad_200_mDbinance,
            input.momentum_200_mDbinance,
            input.EMA_50_mDbinance,
            input.SMA_200_mDbinance,
            input.RSI_mDbinance,
            input.close_sp500,
            input.volume_sp500,
            input.var_diaria_sp500,
            input.rango_dia_sp500,
            input.volatilidad_50_sp500,
            input.momentum_50_sp500,
            input.volatilidad_200_sp500,
            input.momentum_200_sp500,
            input.EMA_50_sp500,
            input.SMA_200_sp500,
            input.RSI_sp500,
            input.close_nasdaq,
            input.volume_nasdaq,
            input.var_diaria_nasdaq,
            input.rango_dia_nasdaq,
            input.volatilidad_50_nasdaq,
            input.momentum_50_nasdaq,
            input.volatilidad_200_nasdaq,
            input.momentum_200_nasdaq,
            input.EMA_50_nasdaq,
            input.SMA_200_nasdaq,
            input.RSI_nasdaq,
            input.close_dxy,
            input.var_diaria_dxy,
            input.rango_dia_dxy,
            input.volatilidad_50_dxy,
            input.momentum_50_dxy,
            input.volatilidad_200_dxy,
            input.momentum_200_dxy,
            input.EMA_50_dxy,
            input.SMA_200_dxy,
            input.RSI_dxy,
        ]

        # Convertir a numpy array y reshape para el modelo
        X = np.array(features).reshape(1, -1)

        # Hacer la predicción
        prediction = app.model30.predict(X)[0]

        return prediction
    except Exception as e:
        print(f"Error en la predicción XGB: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error en la predicción")


def create_chart(request: Request = None):

    try:
        # Load data from Parquet file
        df = pd.read_parquet(DATA_PATH)

        # Ensure data is sorted by date
        df = df.sort_values("timestamp")

        # Filter by dates if provided in the request
        start_date = None
        end_date = None

        if (
            request
            and "start" in request.query_params
            and "end" in request.query_params
        ):
            try:
                start_date = request.query_params.get("start")
                end_date = request.query_params.get("end")

                print(f"Date parameters received: start={start_date}, end={end_date}")

                # Add time part to dates if not present
                if "T" not in start_date:
                    start_date = f"{start_date}T00:00:00"
                if "T" not in end_date:
                    end_date = f"{end_date}T23:59:59"

                print(f"Formatted dates: start={start_date}, end={end_date}")

                # Convert to datetime for filtering
                try:
                    start_date = datetime.fromisoformat(start_date)
                    end_date = datetime.fromisoformat(end_date)
                except ValueError as e:
                    print(f"Error converting dates with fromisoformat: {e}")
                    # Try alternative method
                    start_date = datetime.strptime(start_date.split("T")[0], "%Y-%m-%d")
                    end_date = datetime.strptime(end_date.split("T")[0], "%Y-%m-%d")
                    # Add hours for end of day
                    end_date = end_date.replace(hour=23, minute=59, second=59)

                print(f"Datetime objects created: start={start_date}, end={end_date}")

                # Filter DataFrame
                filtered_df = df[
                    (df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)
                ]
                print(f"Data filtered. Remaining rows: {len(filtered_df)}")

                if len(filtered_df) > 0:
                    df = filtered_df
                else:
                    print(
                        "WARNING! Filtering resulted in 0 rows. Using all available data."
                    )

            except Exception as e:
                print(f"Error filtering by dates: {e}")
                traceback.print_exc()

        # Create figure with subplots: main chart, volume and RSI below
        fig = make_subplots(
            rows=3,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.6, 0.2, 0.2],
            subplot_titles=("BTC/USD", "Volume", "RSI"),
        )

        # Add candlesticks to main chart
        fig.add_trace(
            go.Candlestick(
                x=df["timestamp"],
                open=df["open_binance"],
                high=df["high_binance"],
                low=df["low_binance"],
                close=df["close_binance"],
                name="BTC-USD",
                increasing_line_color="#0bf67e",  # Neon green for bullish candles
                decreasing_line_color="#ff5252",  # Red for bearish candles
                increasing_fillcolor="rgba(11, 246, 126, 0.3)",
                decreasing_fillcolor="rgba(255, 82, 82, 0.3)",
            ),
            row=1,
            col=1,
        )

        # Add SMA and EMA to main chart
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["SMA_50_binance"],
                line=dict(color="#00b4ff", width=1.5),  # Neon blue
                name="SMA 50",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["SMA_200_binance"],
                line=dict(color="#7b5dfa", width=1.5),  # Neon purple
                name="SMA 200",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["EMA_50_binance"],
                line=dict(color="#ffd700", width=1.5, dash="dot"),  # Dotted gold
                name="EMA 50",
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["EMA_200_binance"],
                line=dict(color="#ff8c00", width=1.5, dash="dot"),  # Dotted orange
                name="EMA 200",
            ),
            row=1,
            col=1,
        )

        # Add Fear & Greed Index as a line in the main chart
        if "fear_greed_index_fg" in df.columns:
            # Scale the index to display well on the chart
            max_price = df["high_binance"].max()
            min_price = df["low_binance"].min()
            range_price = max_price - min_price

            # Scale Fear & Greed Index to be in the bottom 20% of the chart
            scale_factor = range_price * 0.2
            base_level = min_price

            df["fear_greed_scaled"] = (
                base_level + (df["fear_greed_index_fg"] / 100) * scale_factor
            )

            fig.add_trace(
                go.Scatter(
                    x=df["timestamp"],
                    y=df["fear_greed_scaled"],
                    line=dict(color="rgba(255, 255, 255, 0.7)", width=1),
                    fill="tozeroy",
                    fillcolor="rgba(255, 255, 255, 0.1)",
                    name="Fear & Greed",
                    hovertemplate="Fear & Greed: %{text}<extra></extra>",
                    text=df["fear_greed_index_fg"],
                ),
                row=1,
                col=1,
            )

        # Add trading volume in the second subplot
        colors = [
            "#0bf67e" if row["close_binance"] >= row["open_binance"] else "#ff5252"
            for _, row in df.iterrows()
        ]

        fig.add_trace(
            go.Bar(
                x=df["timestamp"],
                y=df["volumen_binance"],
                marker_color=colors,
                name="Volume",
            ),
            row=2,
            col=1,
        )

        # Add volume SMA
        df["volumen_sma20"] = df["volumen_binance"].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["volumen_sma20"],
                line=dict(color="#7b5dfa", width=1.5),
                name="Volume SMA 20",
            ),
            row=2,
            col=1,
        )

        # Add RSI in the third subplot
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["RSI_binance"],
                line=dict(color="#00b4ff", width=1.5),
                name="RSI",
            ),
            row=3,
            col=1,
        )

        # Add reference lines for RSI
        fig.add_shape(
            type="line",
            x0=df["timestamp"].iloc[0],
            x1=df["timestamp"].iloc[-1],
            y0=70,
            y1=70,
            line=dict(color="rgba(255, 82, 82, 0.5)", width=1, dash="dash"),
            row=3,
            col=1,
        )

        fig.add_shape(
            type="line",
            x0=df["timestamp"].iloc[0],
            x1=df["timestamp"].iloc[-1],
            y0=30,
            y1=30,
            line=dict(color="rgba(11, 246, 126, 0.5)", width=1, dash="dash"),
            row=3,
            col=1,
        )

        # Improve visual appearance of the chart
        fig.update_layout(
            title="Bitcoin (BTC-USD) - Technical Analysis",
            title_font=dict(size=24, color="white", family="Segoe UI, sans-serif"),
            font=dict(family="Segoe UI, sans-serif", color="white", size=12),
            plot_bgcolor="#1a1d25",  # Dark background for the chart
            paper_bgcolor="#0c0e12",  # Dark background for the area around the chart
            xaxis=dict(
                gridcolor="rgba(255, 255, 255, 0.1)",
                rangeslider=dict(visible=False),
                showgrid=True,
            ),
            yaxis=dict(
                title="Price (USD)",
                gridcolor="rgba(255, 255, 255, 0.1)",
                showgrid=True,
                side="right",  # Move scale to the right like in Binance
                tickformat="$,.0f",  # Price format with $ and no decimals
            ),
            yaxis2=dict(
                title="Volume", gridcolor="rgba(255, 255, 255, 0.1)", showgrid=True
            ),
            yaxis3=dict(
                title="RSI",
                gridcolor="rgba(255, 255, 255, 0.1)",
                showgrid=True,
                range=[0, 100],  # RSI is always between 0 and 100
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0.05,
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="rgba(255,255,255,0.2)",
            ),
            margin=dict(l=10, r=60, t=80, b=10),  # Adjusted margins
            hovermode="x unified",
            showlegend=True,
        )

        # Add annotations for current levels
        last_close = df["close_binance"].iloc[-1]
        last_date = df["timestamp"].iloc[-1]

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
            row=1,
            col=1,
        )

        # Add crosshair tools for precise information when hovering
        fig.update_xaxes(
            showspikes=True, spikecolor="white", spikesnap="cursor", spikemode="across"
        )
        fig.update_yaxes(showspikes=True, spikecolor="white", spikethickness=1)

        # Configuration for mobile devices
        fig.update_layout(autosize=True)

        params_string = ""
        if start_date and end_date:
            params_string = (
                f"?start={start_date.isoformat()}&end={end_date.isoformat()}"
            )

        # Save chart as HTML file with config to match page style
        config = {
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "scrollZoom": True,
            "displayModeBar": True,
            "displaylogo": False,
            "responsive": True,
            "toImageButtonOptions": {
                "format": "png",
                "filename": "bitcoin_chart",
                "height": 800,
                "width": 1200,
                "scale": 2,
            },
        }

        # Make sure directory exists
        os.makedirs(os.path.dirname(CHART_PATH), exist_ok=True)

        fig.write_html(
            f"{CHART_PATH}{params_string}",
            config=config,
            include_plotlyjs=True,
            full_html=True,
        )

        print("Chart created successfully")
        return True
    except Exception as e:
        print(f"Error creating chart: {e}")
        traceback.print_exc()
        return False


@app.on_event("startup")
async def startup_event():
    try:
        # Update data
        pipeline()

        # Create initial chart
        create_chart()

        # Load prediction models
        app.model7 = load("models/SVR.joblib")
        app.model30 = load("models/XGB.joblib")

        # Load scalers fot models
        app.scaler7 = load("models/SVR_scaler.joblib")
        app.scaler30 = load("models/XGB_scaler.joblib")

        print("Startup completed successfully")
    except Exception as e:
        print(f"Error during startup: {e}")
        traceback.print_exc()


@app.get("/api/bitcoin/prediction", response_model=BitcoinPrediction)
async def get_bitcoin_prediction(prediction_date: str = Query(None)):
    try:
        # Load data from Parquet files
        df = pd.read_parquet(DATA_PATH)
        pred_7d = pd.read_parquet(PRED_7D_PATH)
        pred_30d = pd.read_parquet(PRED_30D_PATH)

        # Ensure data is sorted by date
        df = df.sort_values("timestamp")
        pred_7d = pred_7d.sort_values("timestamp")
        pred_30d = pred_30d.sort_values("timestamp")

        # Validate that the latest timestamps match
        if (
            df.timestamp.iloc[-1] != pred_7d.timestamp.iloc[-1]
            or df.timestamp.iloc[-1] != pred_30d.timestamp.iloc[-1]
        ):
            print("WARNING: Latest timestamps don't match between datasets")

        # Get current date if no prediction date is provided
        if prediction_date is None:
            # Use current date for prediction
            current_price = df.close_binance.iloc[-1]

            # 7-DAY PREDICTION with current data
            X_last_7d = (
                pred_7d.drop(columns=["timestamp", "pct_cambio_7d"])
                .iloc[-1]
                .to_numpy()
                .reshape(1, -1)
            )
            X_last_7d = app.scaler7.transform(X_last_7d)
            change_7d = app.model7.predict(X_last_7d)[0]
            price_7d = current_price * (1 + change_7d / 100)

            # 30-DAY PREDICTION with current data
            X_last_30d = (
                pred_30d.drop(columns=["timestamp", "pct_cambio_30d"])
                .iloc[-1]
                .to_numpy()
                .reshape(1, -1)
            )
            X_last_30d = app.scaler30.transform(X_last_30d)
            change_30d = app.model30.predict(X_last_30d)[0]
            price_30d = current_price * (1 + change_30d / 100)

        else:
            # Convert string date to datetime
            target_date = pd.to_datetime(prediction_date)
            latest_date = df.timestamp.iloc[-1]

            # Calculate days between latest data and target date
            days_diff = (target_date - latest_date).days

            if days_diff <= 0:
                # For historical dates, use actual data if available
                historical_row = df[df.timestamp == target_date]
                if not historical_row.empty:
                    current_price = df.close_binance.iloc[
                        -1
                    ]  # Current price is still the latest
                    price_7d = historical_row.close_binance.iloc[0]  # Historical price
                    price_30d = historical_row.close_binance.iloc[0]  # Historical price

                    # Calculate changes
                    change_7d = ((price_7d - current_price) / current_price) * 100
                    change_30d = ((price_30d - current_price) / current_price) * 100
                else:
                    raise HTTPException(
                        status_code=404,
                        detail="No data available for the specified date",
                    )
            else:
                # For future dates, use the model to predict
                current_price = df.close_binance.iloc[-1]

                # Determine which model to use based on days difference
                if days_diff <= 7:
                    # Use 7-day model
                    X_last = (
                        pred_7d.drop(columns=["timestamp", "pct_cambio_7d"])
                        .iloc[-1]
                        .to_numpy()
                        .reshape(1, -1)
                    )
                    X_last = app.scaler7.transform(X_last)
                    change = app.model7.predict(X_last)[0]

                    # Scale the prediction based on days
                    scaling_factor = days_diff / 7
                    adjusted_change = change * scaling_factor

                    # Calculate predictions
                    price_prediction = current_price * (1 + adjusted_change / 100)
                    price_7d = price_prediction
                    price_30d = price_prediction  # Same as 7d for now
                    change_7d = adjusted_change
                    change_30d = adjusted_change  # Same as 7d for now

                elif days_diff <= 30:
                    # Use 30-day model
                    X_last = (
                        pred_30d.drop(columns=["timestamp", "pct_cambio_30d"])
                        .iloc[-1]
                        .to_numpy()
                        .reshape(1, -1)
                    )
                    X_last = app.scaler30.transform(X_last)
                    change = app.model30.predict(X_last)[0]

                    # Scale the prediction based on days
                    scaling_factor = days_diff / 30
                    adjusted_change = change * scaling_factor

                    # Calculate predictions
                    price_prediction = current_price * (1 + adjusted_change / 100)
                    price_7d = price_prediction
                    price_30d = price_prediction
                    change_7d = adjusted_change
                    change_30d = adjusted_change
                else:
                    # For dates beyond 30 days, use the 30-day model but with a warning
                    X_last = (
                        pred_30d.drop(columns=["timestamp", "pct_cambio_30d"])
                        .iloc[-1]
                        .to_numpy()
                        .reshape(1, -1)
                    )
                    change = app.model30.predict(X_last)[0]
                    precio_medio = (
                        df["close_binance"].rolling(window=30).mean().iloc[-1]
                    )

                    # For long-term predictions, we'll be more conservative
                    # Assume change grows at a diminishing rate
                    scaling_factor = min(
                        days_diff / 30, 3
                    )  # Cap at 3x for very long-term
                    adjusted_change = change * scaling_factor

                    # Calculate predictions
                    price_prediction = precio_medio * (1 + adjusted_change / 100)
                    price_7d = price_prediction
                    price_30d = price_prediction
                    change_7d = adjusted_change
                    change_30d = adjusted_change

                    print(
                        f"Warning: Prediction for {days_diff} days ahead may be less accurate"
                    )

        # Return prediction results
        return BitcoinPrediction(
            current_price=current_price,
            price_7d=price_7d,
            price_30d=price_30d,
            change_7d=change_7d,
            change_30d=change_30d,
            prediction_date=prediction_date,
        )
    except Exception as e:
        print(f"Error getting Bitcoin predictions: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error retrieving Bitcoin data")


@app.post("/api/bitcoin/predict/svr", response_model=ModelPrediction)
async def SVRpredict(input: SVRinput):
    pct_change_7d = SVRprediction(input)

    return ModelPrediction(pct_change=pct_change_7d)


@app.post("/api/bitcoin/predict/xgb", response_model=ModelPrediction)
async def XGBpredict(input: XGBinput):
    pct_change_30d = XGBprediction(input)

    return ModelPrediction(pct_change=pct_change_30d)


@app.get("/static/grafica_bitcoin.html")
async def get_filtered_chart(request: Request):
    try:
        # If date parameters are provided, create a new filtered chart
        if "start" in request.query_params and "end" in request.query_params:
            success = create_chart(request)
            if not success:
                raise HTTPException(
                    status_code=500, detail="Error creating filtered chart"
                )

        # Return HTML file
        return FileResponse(CHART_PATH)
    except Exception as e:
        print(f"Error serving chart: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Error serving chart")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
