from __future__ import annotations

from pathlib import Path
from time import perf_counter

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


class IsolationForestDetector:
    def __init__(self, contamination: float = 0.05) -> None:
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
        )

    def fit(self, data: pd.Series) -> None:
        series = self._validate_series(data)
        self.model.fit(series.to_frame(name=series.name or "value"))

    def predict(self, data: pd.Series) -> dict:
        series = self._validate_series(data)
        features = series.to_frame(name=series.name or "value")

        start_time = perf_counter()
        raw_predictions = self.model.predict(features)
        inference_time_ms = (perf_counter() - start_time) * 1000

        anomalies = [1 if pred == -1 else 0 for pred in raw_predictions]
        anomaly_count = sum(anomalies)
        total_points = len(anomalies)

        return {
            "timestamps": [str(index) for index in series.index.tolist()],
            "values": series.tolist(),
            "anomalies": anomalies,
            "anomaly_count": anomaly_count,
            "anomaly_rate": anomaly_count / total_points if total_points else 0.0,
            "inference_time_ms": round(inference_time_ms, 3),
        }

    def save(self, path: str | Path) -> None:
        model_path = Path(path)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "contamination": self.contamination,
            },
            model_path,
        )

    @classmethod
    def load(cls, path: str | Path) -> "IsolationForestDetector":
        payload = joblib.load(path)
        detector = cls(contamination=payload["contamination"])
        detector.model = payload["model"]
        return detector

    @staticmethod
    def _validate_series(data: pd.Series) -> pd.Series:
        if not isinstance(data, pd.Series):
            raise TypeError("data must be a pandas Series.")

        if data.empty:
            raise ValueError("data must not be empty.")

        series = pd.to_numeric(data, errors="coerce").dropna()
        if series.empty:
            raise ValueError("data must contain at least one numeric value.")

        return series
