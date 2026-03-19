from __future__ import annotations

from pathlib import Path
from time import perf_counter

import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed
from tensorflow.keras.models import Sequential, load_model

from backend.utils.preprocess import create_sequences


class LSTMAutoencoder:
    def __init__(self, seq_length: int = 24, threshold_percentile: int = 95) -> None:
        self.seq_length = seq_length
        self.threshold_percentile = threshold_percentile
        self.threshold: float | None = None
        self.model = self.build_model()

    def build_model(self) -> Sequential:
        model = Sequential(
            [
                LSTM(64, input_shape=(self.seq_length, 1)),
                RepeatVector(self.seq_length),
                LSTM(64, return_sequences=True),
                TimeDistributed(Dense(1)),
            ]
        )
        model.compile(optimizer="adam", loss="mse")
        return model

    def fit(self, data: pd.Series, epochs: int = 20, batch_size: int = 32) -> None:
        series = self._validate_series(data)
        if len(series) < self.seq_length:
            raise ValueError("data length must be greater than or equal to seq_length.")
        sequences, _ = create_sequences(series.to_numpy(), seq_length=self.seq_length)

        self.model.fit(
            sequences,
            sequences,
            epochs=epochs,
            batch_size=batch_size,
            verbose=0,
        )

        reconstructed = self.model.predict(sequences, verbose=0)
        reconstruction_errors = np.mean(np.square(sequences - reconstructed), axis=(1, 2))
        self.threshold = float(
            np.percentile(reconstruction_errors, self.threshold_percentile)
        )

    def predict(self, data: pd.Series) -> dict:
        series = self._validate_series(data)
        if len(series) < self.seq_length:
            raise ValueError("data length must be greater than or equal to seq_length.")
        sequences, indices = create_sequences(series.to_numpy(), seq_length=self.seq_length)

        if self.threshold is None:
            raise ValueError("Model threshold is not set. Fit or load the model first.")

        start_time = perf_counter()
        reconstructed = self.model.predict(sequences, verbose=0)
        inference_time_ms = (perf_counter() - start_time) * 1000

        reconstruction_errors = np.mean(np.square(sequences - reconstructed), axis=(1, 2))
        anomalies = (reconstruction_errors > self.threshold).astype(int)
        aligned_indices = indices + self.seq_length - 1
        aligned_series = series.iloc[aligned_indices]
        anomaly_count = int(anomalies.sum())
        total_points = int(len(anomalies))

        return {
            "timestamps": [str(index) for index in aligned_series.index.tolist()],
            "values": aligned_series.tolist(),
            "anomalies": anomalies.astype(int).tolist(),
            "reconstruction_errors": reconstruction_errors.tolist(),
            "threshold": self.threshold,
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_count / total_points if total_points else 0.0,
            "inference_time_ms": round(inference_time_ms, 3),
        }

    def save(self, path: str | Path) -> None:
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)

        metadata_path = model_path.with_suffix(model_path.suffix + ".meta.joblib")
        self.model.save(model_path)
        joblib.dump(
            {
                "seq_length": self.seq_length,
                "threshold_percentile": self.threshold_percentile,
                "threshold": self.threshold,
            },
            metadata_path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "LSTMAutoencoder":
        model_path = Path(path)
        metadata_path = model_path.with_suffix(model_path.suffix + ".meta.joblib")
        metadata = joblib.load(metadata_path)

        detector = cls(
            seq_length=metadata["seq_length"],
            threshold_percentile=metadata["threshold_percentile"],
        )
        detector.model = load_model(model_path)
        detector.threshold = metadata["threshold"]
        return detector

    @staticmethod
    def _validate_series(data: pd.Series) -> pd.Series:
        if not isinstance(data, pd.Series):
            raise TypeError("data must be a pandas Series.")

        if data.empty:
            raise ValueError("data must not be empty.")

        series = pd.to_numeric(data, errors="coerce").dropna()
        if len(series) < 1:
            raise ValueError("data must contain at least one numeric value.")

        return series
