from __future__ import annotations

from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.db import get_logs, get_metrics, init_db, log_predictions, save_metrics
from backend.models import (
    IsolationForestDetector,
    LSTMAutoencoder,
    OneClassSVMDetector,
)
from backend.utils import load_clean_data


MODEL_LABELS = {
    "isolation_forest": "IsolationForestDetector",
    "lstm": "LSTMAutoencoder",
    "ocsvm": "OneClassSVMDetector",
}


def _get_target_series(df: pd.DataFrame) -> pd.Series:
    if "Global_active_power" not in df.columns:
        raise ValueError("Global_active_power column is missing from cleaned data.")
    return df["Global_active_power"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    clean_df = load_clean_data()
    series = _get_target_series(clean_df)

    isolation_forest = IsolationForestDetector(contamination=0.05)
    isolation_forest.fit(series)

    lstm_autoencoder = LSTMAutoencoder(seq_length=24, threshold_percentile=95)
    lstm_autoencoder.fit(series, epochs=20, batch_size=32)

    one_class_svm = OneClassSVMDetector(nu=0.05)
    one_class_svm.fit(series)

    app.state.clean_df = clean_df
    app.state.models = {
        "isolation_forest": isolation_forest,
        "lstm": lstm_autoencoder,
        "ocsvm": one_class_svm,
    }

    yield


app = FastAPI(title="Smart City Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> JSONResponse:
    return JSONResponse(
        content={
            "status": "ok",
            "message": "Smart City backend is running.",
        }
    )


@app.get("/api/data")
def get_data() -> JSONResponse:
    clean_df = app.state.clean_df.tail(500)
    payload = {
        "timestamps": [str(index) for index in clean_df.index.tolist()],
        "values": clean_df["Global_active_power"].tolist(),
    }
    return JSONResponse(content=jsonable_encoder(payload))


@app.post("/api/predict/{model_name}")
def predict(model_name: str) -> JSONResponse:
    if model_name not in app.state.models:
        raise HTTPException(status_code=404, detail="Model not found.")

    model = app.state.models[model_name]
    series = _get_target_series(app.state.clean_df)

    try:
        predictions = model.predict(series)
        log_predictions(predictions, model_name)
        save_metrics(
            model_name=model_name,
            anomaly_count=predictions["anomaly_count"],
            anomaly_rate=predictions["anomaly_rate"],
            inference_time_ms=predictions["inference_time_ms"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse(
        content=jsonable_encoder(
            {
                "model": MODEL_LABELS[model_name],
                **predictions,
            }
        )
    )


@app.get("/api/logs")
def fetch_logs(model: str | None = None) -> JSONResponse:
    try:
        logs = get_logs(model_name=model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse(content=jsonable_encoder(logs))


@app.get("/api/metrics")
def fetch_metrics() -> JSONResponse:
    try:
        metrics = get_metrics()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return JSONResponse(content=jsonable_encoder(metrics))
